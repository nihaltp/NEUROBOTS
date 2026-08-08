import time
import json
import zmq
import logging

logger = logging.getLogger("Movement")

def run_movement_sequence(config, send_command):
    context = zmq.Context()
    det_sub = context.socket(zmq.SUB)
    det_port = config['zmq']['detection_port']
    det_sub.connect(f"tcp://127.0.0.1:{det_port}")
    det_sub.setsockopt_string(zmq.SUBSCRIBE, "")

    control_pub = context.socket(zmq.PUB)
    control_port = config['zmq']['control_port']
    control_pub.connect(f"tcp://127.0.0.1:{control_port}")

    # Give sockets time to connect
    time.sleep(1.0)
    
    logger.info("Starting autonomous loop...")
    while True:
        try:
            # 1. Disable detection
            control_pub.send_string(json.dumps({"detection_enabled": False}))
            
            # 2. Move forward for 2 seconds
            logger.info("Moving forward for 2 seconds")
            send_command('F:25')
            start = time.time()
            while time.time() - start < 2.0:
                time.sleep(0.5)
                send_command('F:25') # keep alive
            send_command('S')
            
            # 3. Enable detection
            logger.info("Enabling camera detection...")
            control_pub.send_string(json.dumps({"detection_enabled": True}))
            
            # 4. Wait for detection
            detected = False
            # Clear buffer first
            while True:
                try:
                    det_sub.recv_string(flags=zmq.NOBLOCK)
                except zmq.Again:
                    break
            
            logger.info("Waiting for detection...")
            while not detected:
                latest_msg = det_sub.recv_string()
                data = json.loads(latest_msg)
                
                classes_in_frame = set()
                for det in data.get('detections', []):
                    classes_in_frame.add(det['class_name'])
                    
                for class_name in classes_in_frame:
                    if "Tomato" in class_name and class_name != "Healthy Tomato Plant":
                        pump_mapping = config.get('pump_control', {}).get('mapping', {})
                        if class_name in pump_mapping:
                            logger.info(f"Target disease '{class_name}' detected!")
                            durations = config.get('pump_control', {}).get('durations', {})
                            default_duration = config.get('pump_control', {}).get('default_duration', 1.0)
                            pump_id = pump_mapping[class_name]
                            duration = durations.get(pump_id, durations.get(str(pump_id), default_duration))
                            
                            logger.info(f"Turning on pump {pump_id} for {duration} seconds.")
                            pump_on_cmd = f"P{pump_id}:1"
                            send_command(pump_on_cmd)
                            
                            pump_start = time.time()
                            while time.time() - pump_start < duration:
                                time.sleep(min(0.5, duration - (time.time() - pump_start)))
                                send_command(pump_on_cmd)
                                
                            logger.info(f"Turning off pump {pump_id}.")
                            pump_off_cmd = f"P{pump_id}:0"
                            send_command(pump_off_cmd)
                            
                            off_start = time.time()
                            while time.time() - off_start < 0.5:
                                time.sleep(0.1)
                                send_command(pump_off_cmd)
                            
                            detected = True
                            break
                            
                if detected:
                    break

        except Exception as e:
            logger.error(f"Error in autonomous loop: {e}")
            time.sleep(2)

if __name__ == "__main__":
    import os
    import sys
    import requests

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    try:
        from config_loader import load_config
    except ImportError:
        logger.error("Could not import config_loader.")
        sys.exit(1)

    def standalone_send_command(command):
        try:
            response = requests.post('http://127.0.0.1:5000/api/command', json={'command': command}, timeout=2)
            if response.status_code == 200:
                logger.info(f"Command '{command}' sent successfully.")
            else:
                logger.warning(f"Failed to send command '{command}': {response.text}")
        except Exception as e:
            logger.error(f"Error sending command '{command}': {e}")

    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)

    try:
        run_movement_sequence(config, standalone_send_command)
    except KeyboardInterrupt:
        logger.info("Standalone movement sequence interrupted.")
