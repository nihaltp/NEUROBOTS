import cv2
import json
import time
import argparse
import logging
import zmq
import sys
import os
from ultralytics import YOLO

# Add parent directory to path to import config_loader
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_loader import load_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Headless Plant Disease Detection")
    parser.add_argument("--show", action="store_true", help="Display the camera feed with bounding boxes for local testing.")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging and verbose model output.")
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
    frame_pub.bind(f"tcp://*:{config['zmq']['frame_port']}")
    logger.info(f"Frame Publisher bound to port {config['zmq']['frame_port']}")
    
    # Detection Publisher
    det_pub = context.socket(zmq.PUB)
    det_pub.bind(f"tcp://*:{config['zmq']['detection_port']}")
    logger.info(f"Detection Publisher bound to port {config['zmq']['detection_port']}")
    
    # Control Subscriber
    control_sub = context.socket(zmq.SUB)
    control_sub.bind(f"tcp://*:{config['zmq']['control_port']}")
    control_sub.setsockopt_string(zmq.SUBSCRIBE, "")
    logger.info(f"Control Subscriber bound to port {config['zmq']['control_port']}")

    model_path = config['model']['path']
    confidence_threshold = config['model'].get('confidence_threshold', 0.5)
    
    try:
        model = YOLO(model_path, task='detect')
        logger.info(f"Model loaded successfully from {model_path}")
    except Exception as e:
        logger.error(f"Failed to load model from {model_path}: {e}")
        return

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config['camera']['width'])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config['camera']['height'])
    if 'fps' in config['camera']:
        cap.set(cv2.CAP_PROP_FPS, config['camera']['fps'])

    if not cap.isOpened():
        logger.error("Failed to open the webcam (index 0).")
        return
        
    logger.info("Webcam opened successfully.")

    detection_enabled = True # Default state
    
    try:
        while True:
            # Check for control messages
            try:
                msg = control_sub.recv_string(flags=zmq.NOBLOCK)
                try:
                    command = json.loads(msg)
                    if 'detection_enabled' in command:
                        detection_enabled = command['detection_enabled']
                        logger.info(f"Detection enabled set to: {detection_enabled}")
                except json.JSONDecodeError:
                    pass
            except zmq.Again:
                pass # No messages available

            ret, frame = cap.read()
            if not ret:
                logger.error("Failed to grab frame from webcam.")
                time.sleep(1)
                continue
                
            frame_detections = []
            
            if detection_enabled:
                # Run inference
                results = model.predict(source=frame, verbose=args.debug, device='cpu')
                
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        conf = float(box.conf[0])
                        if conf < confidence_threshold:
                            continue
                            
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        cls_idx = int(box.cls[0])
                        class_name = model.names[cls_idx]
                        
                        frame_detections.append({
                            "class_name": class_name,
                            "confidence": round(conf, 4),
                            "bbox": {
                                "x_min": int(x1),
                                "y_min": int(y1),
                                "x_max": int(x2),
                                "y_max": int(y2)
                            }
                        })
                        
                        if args.show:
                            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                            label = f"{class_name}: {conf:.2f}"
                            cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Publish detections
                output_payload = {
                    "timestamp": time.time(),
                    "detections": frame_detections
                }
                if args.debug and frame_detections:
                    logger.debug(f"Detected {len(frame_detections)} objects.")
                det_pub.send_string(json.dumps(output_payload))
                
            # Publish frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            frame_pub.send(buffer.tobytes())
            
            if args.show:
                cv2.imshow('Plant Disease Detection', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    except KeyboardInterrupt:
        logger.info("Stopping detector script gracefully...")
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
