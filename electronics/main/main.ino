/*
 * Main Firmware for Robotics Project
 *
 * Hardware:
 * - ESP32-S3
 * - 4 DC Motors (BTS7960 Drivers)
 * - 1 Water Pump (L298N Driver)
 */

#include "../shared/HardwareConfig.h"
#include "../shared/Motors.h"
#include "../shared/Pump.h"
#include "../shared/CommandParser.h"

void setup() {
  Serial.begin(SERIAL_BAUD_RATE);
  delay(1000);
  Serial.println("Initializing System...");

  setupMotors();
  setupPump();

  stopMotors();
  pumpOff(1);
  pumpOff(2);
  Serial.println("Initialization Complete.");
}

void loop() {
  checkCommandTimeout();

  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();  // Remove whitespace/newlines
    processCommand(command);
  }
}
