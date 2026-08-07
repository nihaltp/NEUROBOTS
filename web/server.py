import os
import sys
import json
import time
import zmq
import logging
from flask import Flask, render_template, Response, request, jsonify
from flask_socketio import SocketIO
import serial
import threading

# Add parent directory to path to import config_loader and shared
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_loader import load_config
from shared.wifi_comms import WiFiComms
from shared.ble_comms import BLEComms

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
disease_counts = {}
active_detections = {}
cooldown_period = config.get('model', {}).get('cooldown_period', 5)

connection_case = config.get('connection_case', 'b').lower()

# Comm variables
wifi_comms = None
ser = None
serial_lock = threading.Lock()
ble_comms = None

# Always initialize Serial
serial_port = config.get('serial', {}).get('port', 'COM3')
serial_baud = config.get('serial', {}).get('baudrate', 115200)
try:
    ser = serial.Serial(serial_port, serial_baud, timeout=1)
    logger.info(f"Connected to serial port {serial_port} at {serial_baud}")
except Exception as e:
    logger.error(f"Failed to connect to serial port {serial_port}: {e}")

# Always initialize WiFi
esp_ip = config.get('wifi', {}).get('esp_ip', '192.168.4.1')
esp_port = config.get('wifi', {}).get('esp_port', 12345)
local_port = config.get('wifi', {}).get('local_port', 12346)

try:
    wifi_comms = WiFiComms(local_port=local_port)
    logger.info(f"WiFi Comms initialized. Target ESP32: {esp_ip}:{esp_port}")
except Exception as e:
    logger.error(f"Failed to initialize WiFi Comms: {e}")

# Initialize BLE if starting in case 'c'
def ble_ack_callback(payload):
    socketio.emit('ble_log', {'text': payload})

ble_config = config.get('ble', {})
if ble_config and connection_case == 'c':
    try:
        ble_comms = BLEComms(
            device_name=ble_config.get('device_name', 'NeuroBot'),
            service_uuid=ble_config.get('service_uuid'),
            command_char_uuid=ble_config.get('command_char_uuid'),
            status_char_uuid=ble_config.get('status_char_uuid'),
            ack_callback=ble_ack_callback
        )
        logger.info("BLE Comms initialized in background thread.")
    except Exception as e:
        logger.error(f"Failed to initialize BLE Comms: {e}")

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

def send_command(command):
    if connection_case == 'a':
        if ser and ser.is_open:
            with serial_lock:
                try:
                    ser.reset_input_buffer()
                    ser.write((command + '\n').encode('utf-8'))
                    
                    # Wait for ACK or ERR (relies on serial timeout=1)
                    response = ser.readline().decode('utf-8', errors='ignore').strip()
                    if response.startswith('ACK'):
                        logger.info(f"ESP32 Acknowledged: {response}")
                        return {'status': 'success', 'command': command, 'response': response}, 200
                    elif response.startswith('ERR'):
                        logger.error(f"ESP32 Error: {response}")
                        return {'error': response}, 400
                    else:
                        logger.warning(f"Timeout or unknown response for command '{command}': '{response}'")
                        return {'error': 'Timeout or unknown response from robot'}, 504
                        
                except Exception as e:
                    logger.error(f"Failed to write to serial: {e}")
                    return {'error': str(e)}, 500
        else:
            logger.warning(f"Serial port not available. Command '{command}' dropped.")
            return {'error': 'Serial port not connected'}, 503
    elif connection_case == 'b':
        if wifi_comms:
            try:
                # Send the command via UDP
                wifi_comms.send_message(esp_ip, esp_port, command + '\n')
                
                # Optionally, we could wait for a response, but UDP is connectionless.
                # We'll just assume success for now, or check for a quick reply.
                start_time = time.time()
                response = None
                while time.time() - start_time < 1.0:
                    msg, addr = wifi_comms.receive_message()
                    if msg:
                        response = msg.strip()
                        break
                    time.sleep(0.01)
                    
                if response:
                    if response.startswith('ACK'):
                        logger.info(f"ESP32 Acknowledged: {response}")
                        return {'status': 'success', 'command': command, 'response': response}, 200
                    elif response.startswith('ERR'):
                        logger.error(f"ESP32 Error: {response}")
                        return {'error': response}, 400
                    else:
                        logger.info(f"ESP32 Replied: {response}")
                        return {'status': 'success', 'command': command, 'response': response}, 200
                else:
                    logger.warning(f"No response from ESP32 for command '{command}'")
                    # With UDP, we might not get an ACK reliably, so still return success but note timeout
                    return {'status': 'success', 'command': command, 'note': 'No response from robot'}, 200
                    
            except Exception as e:
                logger.error(f"Failed to send over WiFi: {e}")
                return {'error': str(e)}, 500
        else:
            logger.warning(f"WiFi comms not initialized. Command '{command}' dropped.")
            return {'error': 'WiFi not available'}, 503
    elif connection_case == 'c':
        if ble_comms:
            ble_comms.send_command(command)
            return {'status': 'success', 'command': command, 'note': 'Queued for BLE transmission'}, 200
        else:
            logger.warning(f"BLE comms not initialized. Command '{command}' dropped.")
            return {'error': 'BLE not available'}, 503
    else:
        return {'error': f'Unknown connection case {connection_case}'}, 400


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
                    disease_counts[class_name] = disease_counts.get(class_name, 0) + 1
                    logger.info(f"New instance of {class_name} detected. Total count: {total_diseases_detected}")
                    
                
                # Always update last_seen if detected in this frame
                active_detections[class_name] = current_time
            
            # Add total_count to the payload
            data['total_count'] = total_diseases_detected
            data['disease_counts'] = disease_counts
            socketio.emit('detections', data)
        except Exception as e:
            logger.error(f"Error in detection listener: {e}")
            time.sleep(0.1)

@app.route('/')
def index():
    master_mode = os.environ.get("MASTER_MODE") == "1"
    return render_template('index.html', master_mode=master_mode)

@app.route('/control')
def control():
    return render_template('control.html')

@app.route('/api/set_connection', methods=['POST'])
def set_connection():
    global connection_case, ble_comms
    data = request.json
    mode = data.get('mode', 'a')
    if mode in ['a', 'b', 'c']:
        connection_case = mode
        logger.info(f"Connection mode changed to: {mode}")
        
        # Initialize ble_comms on demand
        if mode == 'c' and not ble_comms:
            ble_config = config.get('ble', {})
            if ble_config:
                try:
                    ble_comms = BLEComms(
                        device_name=ble_config.get('device_name', 'NeuroBot'),
                        service_uuid=ble_config.get('service_uuid'),
                        command_char_uuid=ble_config.get('command_char_uuid'),
                        status_char_uuid=ble_config.get('status_char_uuid'),
                        ack_callback=ble_ack_callback
                    )
                    logger.info("BLE Comms initialized in background thread.")
                except Exception as e:
                    logger.error(f"Failed to initialize BLE Comms: {e}")
        elif mode != 'c' and ble_comms:
            ble_comms.close()
            ble_comms = None
            
        return jsonify({'status': 'success', 'mode': mode})
    return jsonify({'error': 'Invalid mode'}), 400

@app.route('/api/command', methods=['POST'])
def handle_command():
    data = request.json
    command = data.get('command')
    if not command:
        return jsonify({'error': 'No command provided'}), 400
    
    logger.info(f"Received command: {command}")
    
    response_data, status_code = send_command(command)
    return jsonify(response_data), status_code

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@socketio.on('connect')
def handle_connect():
    logger.info("Client connected")
    socketio.emit('stats_update', {'total_count': total_diseases_detected, 'disease_counts': disease_counts})

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
