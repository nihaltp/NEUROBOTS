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

## Running the Server

Because the architecture uses ZeroMQ to decouple the camera/detector from the web server, you must run both processes.

### 1. Start the Detector

This process claims the camera `/dev/video0`, captures frames, runs inference (if enabled), and publishes the data.

```bash
python disease_detection/detect_disease.py
```

### 2. Start the Web Server

This process serves the dashboard on port 5000 and streams data from the detector.

```bash
python web/server.py
```

## Accessing the Dashboard

Open a browser on any device on the same network and navigate to:

```bash
http://<RASPBERRY_PI_IP>:5000
```
