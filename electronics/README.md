# Robotics Project Electronics Firmware

This folder contains the firmware for the robotics project based on the ESP32-S3 microcontroller.

## Hardware Components

* **Microcontroller:** ESP32-S3
* **Movement:** 4x DC Motors controlled by BTS7960 Motor Drivers
* **Pump:** 1x Water Pump controlled by L298N Motor Driver

## Folder Structure

The project code is organized into tests and the main application to ensure components can be verified independently.

```text
electronics/
├── code/
│   └── main/              # Combined main firmware for the entire robot
│       └── main.ino
│
├── test/
│   ├── bts_driver_test/   # Standalone test for the 4 DC Motors and BTS drivers
│   │   └── bts_driver_test.ino
│   └── pump_test/         # Standalone test for the water pump and L298N driver
│       └── pump_test.ino
```

## Getting Started

1. **Wiring**: Check the pin definitions at the top of each `.ino` file. They are currently set to placeholders. Update `const int` declarations to match your physical wiring setup.
2. **Testing**: Before running the full `main` code, it is recommended to run the standalone tests in the `test/` folder to verify the functionality of individual components.
3. **Flashing**: Open the desired folder in the Arduino IDE and upload the code to your ESP32-S3 board. Ensure the correct board is selected in your IDE.
4. **Debugging**: All sketches output debugging messages over Serial at `115200` baud. Use the Serial Monitor to observe system states.

## Safety Features

Both the main firmware and tests are configured to stop all motors and turn off the pump on startup (`setup()`) to prevent unexpected hardware activation upon power-up or reboot.
