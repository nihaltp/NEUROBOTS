import time
import json
import zmq
import logging

logger = logging.getLogger("Movement")

def check_camera_and_water(det_sub, config, send_command):
    # Get the latest frame by clearing the buffer
    latest_msg = None
    while True:
        try:
            latest_msg = det_sub.recv_string(flags=zmq.NOBLOCK)
        except zmq.Again:
            break
            
    if latest_msg:
        data = json.loads(latest_msg)
        pump_mapping = config.get('pump_control', {}).get('mapping', {})
        durations = config.get('pump_control', {}).get('durations', {})
        default_duration = config.get('pump_control', {}).get('default_duration', 1.0)
        
        classes_in_frame = set()
        for det in data.get('detections', []):
            classes_in_frame.add(det['class_name'])
            
        for class_name in classes_in_frame:
            if "Tomato" in class_name and class_name != "Healthy Tomato Plant":
                if class_name in pump_mapping:
                    pump_id = pump_mapping[class_name]
                    duration = durations.get(pump_id, durations.get(str(pump_id), default_duration))
                else:
                    logger.warning(f"Unmapped disease '{class_name}' detected. Skipping spraying.")
                    continue
                    
                logger.info(f"Target disease '{class_name}' detected! Stopping rover.")
                send_command('S')
                time.sleep(0.5)
                
                logger.info(f"Turning on pump {pump_id} for {duration} seconds.")
                pump_on_cmd = f"P{pump_id}:1"
                send_command(pump_on_cmd)
                
                pump_start = time.time()
                while time.time() - pump_start < duration:
                    time.sleep(min(0.5, duration - (time.time() - pump_start)))
                    send_command(pump_on_cmd) # Re-send to prevent timeout
                
                logger.info(f"Turning off pump {pump_id}.")
                pump_off_cmd = f"P{pump_id}:0"
                send_command(pump_off_cmd)
                
                off_start = time.time()
                while time.time() - off_start < 0.5:
                    time.sleep(0.1)
                    send_command(pump_off_cmd)
                    
                break # Only water once per check

def run_movement_sequence(config, send_command):
    context = zmq.Context()
    det_sub = context.socket(zmq.SUB)
    det_port = config['zmq']['detection_port']
    det_sub.connect(f"tcp://127.0.0.1:{det_port}")
    det_sub.setsockopt_string(zmq.SUBSCRIBE, "")

    logger.info("Starting hardcoded movement sequence...")

    logger.info("Moving forward for 5 seconds")
    send_command('F:25')
    start = time.time()
    while time.time() - start < 5.0:
        time.sleep(1.0)
        send_command('F:25') # keep alive
        
    send_command('S')
    time.sleep(0.5)
    
    logger.info("Checking camera...")
    check_camera_and_water(det_sub, config, send_command)
    
    logger.info("Moving forward for 5 seconds")
    send_command('F:25')
    start = time.time()
    while time.time() - start < 5.0:
        time.sleep(1.0)
        send_command('F:25') # keep alive
        
    send_command('S')
    time.sleep(0.5)
    
    logger.info("Checking camera...")
    check_camera_and_water(det_sub, config, send_command)
    
    logger.info("Sequence complete. Exiting movement program.")
