# Case B (Wi-Fi Direct) Firmware

This directory contains the firmware for "Case B" of the NEUROBOTS project.
In this mode, the ESP32 acts as a Wi-Fi Access Point (AP) and creates a WebSocket server.
The laptop connects directly to the ESP32's Wi-Fi network and sends commands over WebSockets, bypassing the Raspberry Pi.

## Requirements

To compile this code, you need to install the following libraries in your Arduino IDE:

1. `ESPAsyncWebServer` (Download from <https://github.com/me-no-dev/ESPAsyncWebServer>)
2. `AsyncTCP` (Download from <https://github.com/me-no-dev/AsyncTCP>)

## Usage

1. Flash `case_b.ino` to your ESP32.
2. On your laptop, connect to the Wi-Fi network `NEUROBOTS_AP` with password `neurobots123`.
3. Open the web interface (running locally on your laptop) and select "Case B" mode to connect via WebSockets to `ws://192.168.4.1:81/`.
