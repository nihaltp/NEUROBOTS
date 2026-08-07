/*
 * Main Firmware for Robotics Project
 *
 * Hardware:
 * - ESP32-S3
 * - 4 DC Motors (BTS7960 Drivers)
 * - 1 Water Pump (L298N Driver)
 */

#include "../shared/Motors.h"
#include "../shared/Pump.h"

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Initializing System...");

  setupMotors();
  setupPump();

  stopMotors();
  pumpOff();
  Serial.println("Initialization Complete.");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();  // Remove whitespace/newlines

    if (command.startsWith("F")) {
      Serial.println("ACK: Moving Forward");
      moveForward(150);
    } else if (command.startsWith("B")) {
      Serial.println("ACK: Moving Backward");
      moveBackward(150);
    } else if (command.startsWith("L")) {
      Serial.println("ACK: Turning Left");
      turnLeft(150);
    } else if (command.startsWith("R")) {
      Serial.println("ACK: Turning Right");
      turnRight(150);
    } else if (command.startsWith("S")) {
      Serial.println("ACK: Stopping");
      stopMotors();
    } else if (command.startsWith("P1")) {
      Serial.println("ACK: Pump ON");
      pumpOn(255);
    } else if (command.startsWith("P0")) {
      Serial.println("ACK: Pump OFF");
      pumpOff();
    } else {
      Serial.print("ERR: Unknown Command");
      Serial.println(command);
    }
  }
}
