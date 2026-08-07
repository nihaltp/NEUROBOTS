/*
 * Test sketch for BTS7960 Motor Driver
 *
 * Requirements:
 * - ESP32-S3
 * - 4 DC Motors
 * - BTS Motor Drivers
 */

#include "../../shared/Motors.h"

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Initializing BTS Driver Test...");

  setupMotors();

  // Stop all motors on startup for safety
  stopMotors();
  Serial.println("Motors stopped on startup for safety.");
}

void loop() {
  Serial.println("Moving Forward");
  moveForward(150); // Speed 0-255
  delay(2000);

  Serial.println("Stopping");
  stopMotors();
  delay(1000);

  Serial.println("Moving Backward");
  moveBackward(150);
  delay(2000);

  Serial.println("Stopping");
  stopMotors();
  delay(1000);
  
  Serial.println("Turning Left");
  turnLeft(150);
  delay(2000);
  
  Serial.println("Stopping");
  stopMotors();
  delay(1000);

  Serial.println("Turning Right");
  turnRight(150);
  delay(2000);
  
  Serial.println("Stopping");
  stopMotors();
  delay(1000);

  Serial.println("Test Complete. Repeating...\n");
  delay(3000);
}

// Hardware functions are now in shared headers
