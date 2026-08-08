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
    except requests.exceptions.RequestException as e:
        logger.exception(f"Network error sending command '{command}': {e}")
    except Exception as e:
        logger.exception(f"Unexpected error sending command '{command}': {e}")


def main():
    try:
        config = load_config()
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        logger.exception(f"Failed to load config due to file or format error: {e}")
        return
    except Exception as e:
        logger.exception(f"Unexpected error loading config: {e}")
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
    
    from movement import run_movement_sequence
    auto_thread = threading.Thread(target=run_movement_sequence, args=(config, send_command), daemon=True)
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
            except requests.exceptions.RequestException as e:
                logger.exception(f"Network error sending STOPALL: {e}")
            except Exception as e:
                logger.exception(f"Unexpected error sending STOPALL: {e}")
            
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
