import cv2
import json
import time
import argparse
import logging
import zmq
import sys
import os
import numpy as np
import onnxruntime as ort

# Add parent directory to path to import config_loader
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_loader import load_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ImageNet normalization values (used by the HuggingFace MobileNetV2 preprocessor)
IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)
INPUT_SIZE = 224


def preprocess_frame(frame):
    """
    Preprocess a BGR OpenCV frame for the MobileNetV2 classifier.
    1. Resize to 224x224
    2. Convert BGR -> RGB
    3. Scale to [0, 1]
    4. Normalize with ImageNet mean/std
    5. Transpose to CHW and add batch dimension -> (1, 3, 224, 224)
    """
    img = cv2.resize(frame, (INPUT_SIZE, INPUT_SIZE))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32) / 255.0
    img = (img - IMAGENET_MEAN) / IMAGENET_STD
    img = np.transpose(img, (2, 0, 1))  # HWC -> CHW
    img = np.expand_dims(img, axis=0)    # Add batch dim
    return img


def softmax(logits):
    """Compute softmax probabilities from logits."""
    exp = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
    return exp / np.sum(exp, axis=-1, keepdims=True)


def main():
    parser = argparse.ArgumentParser(description="Headless Plant Disease Classification")
    parser.add_argument("--show", action="store_true", help="Display the camera feed with classification overlay for local testing.")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging and verbose output.")
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled.")

    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return

    if not args.debug:
        log_level_str = config.get('logging', {}).get('level', 'INFO').upper()
        log_level = getattr(logging, log_level_str, logging.INFO)
        logging.getLogger().setLevel(log_level)
        logger.setLevel(log_level)

    # Setup ZMQ Context and Sockets
    context = zmq.Context()
    
    # Frame Publisher
    frame_pub = context.socket(zmq.PUB)
    frame_pub.setsockopt(zmq.LINGER, 0)
    frame_pub.bind(f"tcp://*:{config['zmq']['frame_port']}")
    logger.info(f"Frame Publisher bound to port {config['zmq']['frame_port']}")
    
    # Detection Publisher
    det_pub = context.socket(zmq.PUB)
    det_pub.setsockopt(zmq.LINGER, 0)
    det_pub.bind(f"tcp://*:{config['zmq']['detection_port']}")
    logger.info(f"Detection Publisher bound to port {config['zmq']['detection_port']}")
    
    # Control Subscriber
    control_sub = context.socket(zmq.SUB)
    control_sub.setsockopt(zmq.LINGER, 0)
    control_sub.bind(f"tcp://*:{config['zmq']['control_port']}")
    control_sub.setsockopt_string(zmq.SUBSCRIBE, "")
    logger.info(f"Control Subscriber bound to port {config['zmq']['control_port']}")

    model_path = config['model']['path']
    labels_path = config['model'].get('labels', 'weights/labels.json')
    confidence_threshold = config['model'].get('confidence_threshold', 0.5)
    
    # Load ONNX model
    try:
        session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        input_name = session.get_inputs()[0].name
        logger.info(f"ONNX model loaded successfully from {model_path}")
    except Exception as e:
        logger.error(f"Failed to load ONNX model from {model_path}: {e}")
        return

    # Load class labels
    try:
        with open(labels_path, 'r') as f:
            labels = json.load(f)
        # Ensure keys are ints
        labels = {int(k): v for k, v in labels.items()}
        logger.info(f"Loaded {len(labels)} class labels from {labels_path}")
    except Exception as e:
        logger.error(f"Failed to load labels from {labels_path}: {e}")
        return

    cam_type = config['camera'].get('type', 'usb')
    if cam_type == 'ip':
        cam_source = config['camera'].get('ip_url', '')
    else:
        cam_source = config['camera'].get('index', 0)

    cap = cv2.VideoCapture(cam_source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config['camera']['width'])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config['camera']['height'])
    if 'fps' in config['camera']:
        cap.set(cv2.CAP_PROP_FPS, config['camera']['fps'])

    if not cap.isOpened():
        logger.error(f"Failed to open the webcam ({cam_type}: {cam_source}).")
        return
        
    logger.info("Webcam opened successfully.")

    detection_enabled = True # Default state
    
    active_display_detection = None
    display_until_time = 0.0
    display_duration = config['model'].get('display_duration', 3.0)
    
    last_heartbeat_time = 0
    client_connected = False
    last_det_heartbeat = 0
    
    try:
        while True:
            # Check for control messages
            try:
                while True: # Drain all messages
                    msg = control_sub.recv_string(flags=zmq.NOBLOCK)
                    try:
                        command = json.loads(msg)
                        if 'heartbeat' in command:
                            last_heartbeat_time = time.time()
                            if not client_connected:
                                logger.info("Web client connected.")
                                client_connected = True
                        if 'detection_enabled' in command:
                            detection_enabled = command['detection_enabled']
                            logger.info(f"Detection enabled set to: {detection_enabled}")
                    except json.JSONDecodeError:
                        pass
            except zmq.Again:
                pass # No messages available

            current_time = time.time()
            if client_connected and current_time - last_heartbeat_time > 5.0:
                logger.warning("Web client disconnected. Suspending detection to save resources.")
                client_connected = False

            ret, frame = cap.read()
            if not ret:
                logger.error("Failed to grab frame from webcam.")
                time.sleep(1)
                continue
                
            display_frame = frame.copy() if args.show else None
            frame_detections = []
            
            # Only run inference if client is connected or we are showing locally
            if detection_enabled and (client_connected or args.show):
                # Preprocess and run classification
                input_tensor = preprocess_frame(frame)
                outputs = session.run(None, {input_name: input_tensor})
                logits = outputs[0][0]  # Shape: (num_classes,)
                
                # Get probabilities
                probs = softmax(logits)
                top_idx = int(np.argmax(probs))
                top_conf = float(probs[top_idx])
                
                if top_conf >= confidence_threshold:
                    class_name = labels.get(top_idx, f"Unknown ({top_idx})")
                    
                    # Only report the detection if it's a Tomato class
                    if "Tomato" in class_name:
                        active_display_detection = (class_name, round(top_conf, 4))
                        display_until_time = time.time() + display_duration

                if active_display_detection and time.time() < display_until_time:
                    disp_class_name, disp_conf = active_display_detection
                    frame_detections.append({
                        "class_name": disp_class_name,
                        "confidence": disp_conf,
                    })
                    
                    if args.show:
                        label = f"{disp_class_name}: {disp_conf:.2f}"
                        cv2.putText(display_frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
                elif args.show:
                    # Show top prediction even below threshold (in red)
                    class_name = labels.get(top_idx, f"Unknown ({top_idx})")
                    if "Tomato" in class_name:
                        label = f"{class_name}: {top_conf:.2f} (low)"
                        cv2.putText(display_frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

                if args.debug:
                    # Log top 3 predictions
                    top3_indices = np.argsort(probs)[-3:][::-1]
                    for i, idx in enumerate(top3_indices):
                        logger.debug(f"  Top-{i+1}: {labels.get(int(idx), idx)} ({probs[idx]:.4f})")

                # Publish detections
                output_payload = {
                    "timestamp": current_time,
                    "detections": frame_detections
                }
                if args.debug and frame_detections:
                    logger.debug(f"Classified as: {frame_detections[0]['class_name']} ({frame_detections[0]['confidence']:.4f})")
                det_pub.send_string(json.dumps(output_payload))
            else:
                # Send heartbeat on det_pub to let server know we're still alive
                if current_time - last_det_heartbeat > 1.0:
                    det_pub.send_string(json.dumps({"heartbeat": True, "timestamp": current_time}))
                    last_det_heartbeat = current_time
                
            # Publish frame as JPEG only if client is connected to save CPU
            if client_connected:
                _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                frame_pub.send(buffer.tobytes())
            
            if args.show:
                cv2.imshow('Plant Disease Classification', display_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    except KeyboardInterrupt:
        logger.info("Stopping classifier script gracefully...")
    finally:
        cap.release()
        frame_pub.close()
        det_pub.close()
        control_sub.close()
        context.term()
        if args.show:
            cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
