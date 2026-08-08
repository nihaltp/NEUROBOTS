# Case C (BLE Direct) Firmware

This directory contains the firmware for "Case C" of the NEUROBOTS project.
In this mode, the ESP32 acts as a Bluetooth Low Energy (BLE) peripheral.
The laptop connects directly to the ESP32 via BLE and sends commands, bypassing the Raspberry Pi.

## Requirements

To compile this code, you need to install the following library in your Arduino IDE:

1. `NimBLE-Arduino` (Install via Arduino Library Manager or <https://github.com/h2zero/NimBLE-Arduino>)

## Usage

1. Flash `case_c.ino` to your ESP32.
2. The ESP32 will start advertising as `NeuroBot`.
3. Use a BLE client to connect and send commands to the designated characteristics.
