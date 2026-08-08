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

shutting_down = False

def send_command(command):
    global shutting_down
    if shutting_down and command != "STOPALL":
        return
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
    current_command = 'F:50'
    send_command(current_command)
    last_heartbeat_time = time.time()
    
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
                        current_command = 'S'
                        send_command(current_command)
                        
                        # Wait a bit for rover to stop, while keeping watchdog happy
                        stop_start = time.time()
                        while time.time() - stop_start < 0.5:
                            time.sleep(0.1)
                            send_command(current_command)
                        
                        logger.info(f"Turning on pump {pump_id} for {duration} seconds.")
                        pump_on_cmd = f"P{pump_id}:1"
                        send_command(pump_on_cmd)
                        
                        pump_start = time.time()
                        while time.time() - pump_start < duration:
                            time.sleep(min(0.5, duration - (time.time() - pump_start)))
                            # Re-send pump command to prevent ESP32 from timing out during long durations
                            send_command(pump_on_cmd)
                        
                        logger.info(f"Turning off pump {pump_id}.")
                        pump_off_cmd = f"P{pump_id}:0"
                        send_command(pump_off_cmd)
                        
                        off_start = time.time()
                        while time.time() - off_start < 0.5:
                            time.sleep(0.1)
                            send_command(pump_off_cmd)
                        
                        logger.info("Resuming forward movement.")
                        current_command = 'F:50'
                        send_command(current_command)
                        last_heartbeat_time = time.time()
                        
                # Update last seen to prevent rapid re-triggering while still in frame
                active_detections[class_name] = current_time
                
        except zmq.Again:
            # If no detection message, check if we need to send a heartbeat
            if time.time() - last_heartbeat_time > 1.0:
                send_command(current_command)
                last_heartbeat_time = time.time()
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

    kwargs = {}
    if os.name == 'nt':
        kwargs['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP

    logger.info("Starting Web Server...")
    env = os.environ.copy()
    env["MASTER_MODE"] = "1"
    server_process = subprocess.Popen([sys.executable, "web/server.py"], env=env, **kwargs)
    
    logger.info("Starting Disease Detection...")
    detection_process = subprocess.Popen([sys.executable, "disease_detection/detect_disease.py"], **kwargs)
    
    # Give the server time to start up before starting the autonomous loop
    time.sleep(5)
    
    auto_thread = threading.Thread(target=autonomous_loop, args=(config,), daemon=True)
    auto_thread.start()

    try:
        # Keep main thread alive
        while True:
            # Check if any process died
            if server_process.poll() is not None:
                logger.error("Web server process terminated unexpectedly. Restarting...")
                server_process = subprocess.Popen([sys.executable, "web/server.py"], env=env, **kwargs)
            if detection_process.poll() is not None:
                logger.error("Detection process terminated unexpectedly. Restarting...")
                detection_process = subprocess.Popen([sys.executable, "disease_detection/detect_disease.py"], **kwargs)
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down...")
    finally:
        global shutting_down
        shutting_down = True
        logger.info("Sending HALT ALL command to rover before shutdown...")
        while True:
            if server_process.poll() is not None:
                logger.error("Web server process is dead, cannot send STOPALL.")
                break
            try:
                logger.info("Requesting STOPALL...")
                response = requests.post('http://127.0.0.1:5000/api/command', json={'command': "STOPALL"}, timeout=2)
                if response.status_code == 200 and response.json().get('status') == 'success':
                    logger.info("ACK of stopping everything received.")
                    break
                else:
                    logger.warning("Failed to get ACK, retrying...")
            except KeyboardInterrupt:
                logger.info("Force quit requested during shutdown. Exiting immediately.")
                break
            except Exception as e:
                logger.error(f"Error sending STOPALL: {e}")
            
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Force quit requested during shutdown. Exiting immediately.")
                break
        
        logger.info("Terminating subprocesses...")
        server_process.terminate()
        detection_process.terminate()
        server_process.wait()
        detection_process.wait()
        logger.info("Shutdown complete.")

if __name__ == "__main__":
    main()
