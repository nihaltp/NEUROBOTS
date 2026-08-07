/*
 * Test sketch for Command Parser
 */

#include "../../shared/CommandParser.h"

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Initializing Command Test...");

  setupMotors();
  setupPump();

  // Default state: OFF
  stopMotors();
  pumpOff();
}

void loop() {
  Serial.println("\n--- Sending Test Commands ---");
  
  processCommand("F");
  delay(1500);

  processCommand("S");
  delay(1000);

  processCommand("B");
  delay(1500);

  processCommand("S");
  delay(1000);

  processCommand("L");
  delay(1000);
  
  processCommand("S");
  delay(1000);

  processCommand("R");
  delay(1000);
  
  processCommand("S");
  delay(1000);

  processCommand("P1");
  delay(2000);
  
  processCommand("P0");
  delay(1000);
  
  processCommand("INVALID");
  delay(2000);

  Serial.println("--- End of Test Sequence ---");
  delay(3000);
}
