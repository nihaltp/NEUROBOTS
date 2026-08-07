/*
 * Test sketch for Water Pump (L298N Motor Driver)
 *
 * Requirements:
 * - ESP32-S3
 * - L298N Motor Driver
 * - Water Pump
 */

#include "../../shared/Pump.h"

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Initializing Pump Test...");

  setupPump();

  // Default state: OFF
  pumpOff();
  Serial.println("Pump stopped on startup for safety.");
}

void loop() {
  Serial.println("Pump ON");
  pumpOn(255); // Max speed
  delay(3000);

  Serial.println("Pump OFF");
  pumpOff();
  delay(3000);

  Serial.println("Test Complete. Repeating...\n");
}
