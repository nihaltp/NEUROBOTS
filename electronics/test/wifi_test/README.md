# ESP32 to Python Wi-Fi Communication Test

This folder contains a test sketch to verify bidirectional UDP communication between the ESP32 and a Python script running on your laptop over Wi-Fi.

The ESP32 is configured to run as a **Wi-Fi Access Point (AP)**, meaning it creates its own Wi-Fi network that your laptop connects to directly.

## Prerequisites

1. **Hardware:** ESP32 board and a Micro-USB/USB-C cable.
2. **Software:**
   - Arduino IDE installed with ESP32 board support.
   - Python 3.x installed on your laptop.

## Setup Instructions

### 1. Configure the ESP32

1. Open the [`wifi_test.ino`](wifi_test.ino) file in the Arduino IDE.
2. At the top of the file, modify the network credentials to whatever you want your robot's Wi-Fi network to be named:

   ```cpp
   const char* ssid = "NEUROBOT_ESP"; // Replace with your desired Network Name
   const char* password = "robot_password"; // Replace with your desired Password (min 8 chars)
   ```

3. Connect your ESP32 to your computer and select the correct Port and Board in the Arduino IDE.
4. Click **Upload** to flash the code to the ESP32.
5. Once uploaded, open the **Serial Monitor** (set baud rate to `115200`). You should see it print that the Access Point has started and its IP is `192.168.4.1`. Keep the ESP32 powered on.

### 2. Connect Your Laptop to the ESP32

1. Open your laptop's Wi-Fi network settings.
2. Scan for available networks and connect to the network name you specified in step 1 (e.g., `NEUROBOT_ESP`).
3. Enter the password you specified. (Note: Your laptop won't have internet access while connected to the ESP32).

### 3. Run the Python Script

1. Open a terminal or command prompt on your laptop.
2. Navigate to the root directory of the NEUROBOTS repository (`d:\github_competitions\NEUROBOTS`).
3. Run the Python test script:

   ```bash
   python test_wifi_comms.py
   ```

4. **Observe the Results:**
   - In the terminal running the Python script, you should see messages arriving from the ESP32 every 5 seconds.
   - In the Arduino IDE's Serial Monitor, you should see messages arriving from the Python script every 3 seconds.

## Troubleshooting

- **Python not receiving messages:** Make sure your laptop's firewall isn't blocking incoming UDP connections on port 12346.
- **ESP32 not receiving messages:** Make sure your laptop was assigned the IP `192.168.4.2` when it connected to the ESP32. (You can check this using `ipconfig` on Windows or `ifconfig` on Mac/Linux). If it was assigned a different IP, update `targetIP` in the `wifi_test.ino` sketch and re-upload.
