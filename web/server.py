import os
import sys
import json
import time
import zmq
import logging
from flask import Flask, render_template, Response, request, jsonify
from flask_socketio import SocketIO
import serial

# Add parent directory to path to import config_loader
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_loader import load_config

config = load_config()
log_level_str = config.get('logging', {}).get('level', 'INFO').upper()
log_level = getattr(logging, log_level_str, logging.INFO)

# Configure logging
logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WebServer")

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Disease counting state
total_diseases_detected = 0
active_detections = {}
cooldown_period = config.get('model', {}).get('cooldown_period', 5)

# Serial Port setup
serial_port = config.get('serial', {}).get('port', 'COM3')
serial_baud = config.get('serial', {}).get('baudrate', 115200)
ser = None
try:
    ser = serial.Serial(serial_port, serial_baud, timeout=1)
    logger.info(f"Connected to serial port {serial_port} at {serial_baud}")
except Exception as e:
    logger.error(f"Failed to connect to serial port {serial_port}: {e}")

# ZMQ Context
context = zmq.Context()

# Frame Subscriber
frame_sub = context.socket(zmq.SUB)
frame_sub.setsockopt(zmq.CONFLATE, 1) # Only keep latest frame
frame_sub.connect(f"tcp://127.0.0.1:{config['zmq']['frame_port']}")
frame_sub.setsockopt_string(zmq.SUBSCRIBE, "")

# Detection Subscriber
det_sub = context.socket(zmq.SUB)
det_sub.connect(f"tcp://127.0.0.1:{config['zmq']['detection_port']}")
det_sub.setsockopt_string(zmq.SUBSCRIBE, "")

# Control Publisher
control_pub = context.socket(zmq.PUB)
control_pub.connect(f"tcp://127.0.0.1:{config['zmq']['control_port']}")

def generate_frames():
    """Generator for MJPEG streaming."""
    while True:
        try:
            frame = frame_sub.recv()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            logger.error(f"Error reading frame: {e}")
            time.sleep(0.1)

def detection_listener():
    """Background task to listen for detections and push to clients."""
    global total_diseases_detected
    
    logger.info("Starting detection listener thread...")
    while True:
        try:
            msg = det_sub.recv_string()
            data = json.loads(msg)
            
            # Process detections for counting with debounce
            current_time = time.time()
            classes_in_frame = set()
            
            for det in data.get('detections', []):
                classes_in_frame.add(det['class_name'])
                
            for class_name in classes_in_frame:
                last_seen = active_detections.get(class_name, 0)
                if current_time - last_seen > cooldown_period:
                    total_diseases_detected += 1
                    logger.info(f"New instance of {class_name} detected. Total count: {total_diseases_detected}")
                
                # Always update last_seen if detected in this frame
                active_detections[class_name] = current_time
            
            # Add total_count to the payload
            data['total_count'] = total_diseases_detected
            socketio.emit('detections', data)
        except Exception as e:
            logger.error(f"Error in detection listener: {e}")
            time.sleep(0.1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/control')
def control():
    return render_template('control.html')

@app.route('/api/command', methods=['POST'])
def handle_command():
    data = request.json
    command = data.get('command')
    if not command:
        return jsonify({'error': 'No command provided'}), 400
    
    logger.info(f"Received command: {command}")
    
    if ser and ser.is_open:
        try:
            ser.write((command + '\n').encode('utf-8'))
            return jsonify({'status': 'success', 'command': command})
        except Exception as e:
            logger.error(f"Failed to write to serial: {e}")
            return jsonify({'error': str(e)}), 500
    else:
        logger.warning(f"Serial port not available. Command '{command}' dropped.")
        return jsonify({'error': 'Serial port not connected'}), 503

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@socketio.on('connect')
def handle_connect():
    logger.info("Client connected")
    socketio.emit('stats_update', {'total_count': total_diseases_detected})

@socketio.on('toggle_detection')
def handle_toggle_detection(data):
    logger.info(f"Toggle detection requested: {data}")
    # Forward the command to the detector via ZMQ
    control_pub.send_string(json.dumps({'detection_enabled': data.get('enabled', False)}))

if __name__ == '__main__':
    # Start the background task for detections
    socketio.start_background_task(target=detection_listener)
    
    host = config['server'].get('host', '0.0.0.0')
    port = config['server'].get('port', 5000)
    debug = config['server'].get('debug', False)
    
    logger.info(f"Starting web server on {host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug)
