# NeuroBots Agricultural Robot Dashboard

This project provides a headless web interface for controlling and monitoring the Raspberry Pi based agricultural robot. It features a low-latency MJPEG camera stream and live bounding box overlays using WebSockets, decoupled via ZeroMQ for high performance and extensibility.

## Project Structure

- `disease_detection/detect_disease.py`: Core AI script running YOLO. Modified to capture frames and publish them via ZeroMQ instead of processing it synchronously with a web server.
- `web/server.py`: Flask-based web server that serves the UI and proxies ZeroMQ messages to WebSocket/MJPEG streams.
- `web/templates/`: HTML interface
- `web/static/`: CSS and JS for the frontend
- `config.yaml`: Centralized configuration.
- `config_loader.py`: Script to load YAML config.

## AI Model Details

- **Architecture:** YOLOv11
- **Source:** The model was originally trained in the Kaggle project [Plant Disease Object Detection Project | YOLOv11 by killa92](https://www.kaggle.com/code/killa92/plant-disease-object-detection-project-yolov11/).
- **Dataset:** Trained on the **PlantDoc** dataset.
- **Classes:** Capable of detecting 30 distinct classes of plant leaves and diseases (including various Apple, Corn, Tomato, and Potato diseases).
- **Optimization:** We obtained the pre-trained weights from the Kaggle source and explicitly **optimized it** (exported to ONNX format as `weights/best.onnx`) for faster, lightweight inference on edge devices like the Raspberry Pi.

*Note: For detailed metrics (like mAP, precision, and recall), please refer to the original Kaggle notebook's evaluation logs.*

## Dependencies

You need the following Python libraries installed on the Raspberry Pi:

```bash
pip install -r requirements.txt
```

## Expected Hardware

- **Raspberry Pi** (or similar edge computing device)
- **USB Camera** (`/dev/video0`) or IP Camera
- **ESP32 Microcontroller** for Rover/Motor control
- **Pumps** connected to the ESP32 for spraying treatments

## Configuration Example

The system behavior is highly customizable via `config.yaml`. Below is a representative snippet configuring the camera, AI model, and pump mappings:

```yaml
camera:
  type: "usb" # Or "ip"
  index: 0

model:
  path: "weights/plant_disease_classifier.onnx"
  labels: "weights/labels.json"
  cooldown_period: 5

pump_control:
  default_duration: 1.0
  mapping:
    "Tomato with Late Blight": 1
    "Tomato with Early Blight": 2
  durations:
    1: 1.5
    2: 3.0
```

## Startup Order & Usage Flow

Because the architecture uses ZeroMQ to decouple the camera/detector from the web server, multiple processes are required. The recommended startup method is to use the master script, which handles the orchestration.

### Recommended: Master Script

This script automatically launches all necessary subprocesses, starts the autonomous control loop, and handles safe shutdowns:

```bash
python master.py
```

### Manual Startup (Debugging)

If you prefer to run components individually:

1. **Start the Detector:** Claims the camera, runs inference, and publishes via ZMQ.

   ```bash
   python disease_detection/detect_disease.py
   ```

2. **Start the Web Server:** Serves the dashboard on port 5000 and proxies streams.

   ```bash
   python web/server.py
   ```

## Accessing the Dashboard

Open a browser on any device on the same network and navigate to:

```bash
http://<RASPBERRY_PI_IP>:5000
```

## Failure Recovery

- **Subprocess Crashes:** `master.py` continuously monitors the Web Server and Detection processes. If either crashes, it sends a `STOPALL` command to the rover (preventing runaway states) and cleanly terminates the remaining processes.
- **Hardware Disconnects:** If the camera or ESP32 disconnects, errors are logged and the respective scripts may exit. Check physical connections and `/dev/video0` permissions before restarting `master.py`.
- **ZMQ Permission Errors:** If ZeroMQ sockets fail to bind, ensure no orphaned Python processes are holding the ports defined in `config.yaml`.
