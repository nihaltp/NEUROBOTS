import os
import sys
import time
import json
import zmq
import subprocess
import threading
import requests
import logging

# Add parent directory to path to import config_loader
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config_loader import load_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Master")

def send_command(command):
    try:
        response = requests.post('http://127.0.0.1:5000/api/command', json={'command': command}, timeout=2)
        if response.status_code == 200:
            logger.info(f"Command '{command}' sent successfully.")
        else:
            logger.warning(f"Failed to send command '{command}': {response.text}")
    except Exception as e:
        logger.error(f"Error sending command '{command}': {e}")

def autonomous_loop(config):
    context = zmq.Context()
    det_sub = context.socket(zmq.SUB)
    det_port = config['zmq']['detection_port']
    det_sub.connect(f"tcp://127.0.0.1:{det_port}")
    det_sub.setsockopt_string(zmq.SUBSCRIBE, "")
    
    cooldown_period = config.get('model', {}).get('cooldown_period', 5)
    pump_mapping = config.get('pump_control', {}).get('mapping', {})
    durations = config.get('pump_control', {}).get('durations', {})
    default_duration = config.get('pump_control', {}).get('default_duration', 1.0)
    
    active_detections = {}
    
    logger.info("Starting autonomous movement loop...")
    
    # Start moving forward by default
    send_command('F:50')
    
    while True:
        try:
            # Non-blocking receive
            msg = det_sub.recv_string(flags=zmq.NOBLOCK)
            data = json.loads(msg)
            
            current_time = time.time()
            classes_in_frame = set()
            
            for det in data.get('detections', []):
                classes_in_frame.add(det['class_name'])
                
            for class_name in classes_in_frame:
                last_seen = active_detections.get(class_name, 0)
                if current_time - last_seen > cooldown_period:
                    if class_name in pump_mapping:
                        pump_id = pump_mapping[class_name]
                        duration = durations.get(pump_id, durations.get(str(pump_id), default_duration))
                        
                        logger.info(f"Target disease '{class_name}' detected! Stopping rover.")
                        # Stop rover
                        send_command('S')
                        time.sleep(0.5) # Give it time to stop
                        
                        logger.info(f"Turning on pump {pump_id} for {duration} seconds.")
                        send_command(f"P{pump_id}:1")
                        
                        time.sleep(duration)
                        
                        logger.info(f"Turning off pump {pump_id}.")
                        send_command(f"P{pump_id}:0")
                        time.sleep(0.5) # Give pump time to stop
                        
                        logger.info("Resuming forward movement.")
                        send_command('F:50')
                        
                # Update last seen to prevent rapid re-triggering while still in frame
                active_detections[class_name] = current_time
                
        except zmq.Again:
            time.sleep(0.05)
        except Exception as e:
            logger.error(f"Error in autonomous loop: {e}")
            time.sleep(0.5)

def main():
    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return

    logger.info("Starting Web Server...")
    server_process = subprocess.Popen([sys.executable, "web/server.py"])
    
    logger.info("Starting Disease Detection...")
    detection_process = subprocess.Popen([sys.executable, "disease_detection/detect_disease.py"])
    
    # Give the server time to start up before starting the autonomous loop
    time.sleep(5)
    
    auto_thread = threading.Thread(target=autonomous_loop, args=(config,), daemon=True)
    auto_thread.start()

    try:
        # Keep main thread alive
        while True:
            # Check if any process died
            if server_process.poll() is not None:
                logger.error("Web server process terminated unexpectedly.")
                break
            if detection_process.poll() is not None:
                logger.error("Detection process terminated unexpectedly.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down...")
    finally:
        logger.info("Sending HALT ALL command to rover before shutdown...")
        send_command("STOPALL")
        time.sleep(0.5) # Give it a moment to send before killing server
        logger.info("Terminating subprocesses...")
        server_process.terminate()
        detection_process.terminate()
        server_process.wait()
        detection_process.wait()
        logger.info("Shutdown complete.")

if __name__ == "__main__":
    main()
