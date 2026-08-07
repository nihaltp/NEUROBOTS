/*
 * Test sketch for Water Pump (L298N Motor Driver)
 *
 * Requirements:
 * - ESP32-S3
 * - L298N Motor Driver
 * - Water Pump
 */

// Placeholder GPIO pins (Update these when wiring is known)
const int PUMP_IN1 = 14; 
const int PUMP_IN2 = 12;
const int PUMP_ENA = 15; // PWM pin for speed control

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Initializing Pump Test...");

  pinMode(PUMP_IN1, OUTPUT);
  pinMode(PUMP_IN2, OUTPUT);
  pinMode(PUMP_ENA, OUTPUT);

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

void pumpOn(int speed) {
  digitalWrite(PUMP_IN1, HIGH);
  digitalWrite(PUMP_IN2, LOW);
  analogWrite(PUMP_ENA, speed);
}

void pumpOff() {
  digitalWrite(PUMP_IN1, LOW);
  digitalWrite(PUMP_IN2, LOW);
  analogWrite(PUMP_ENA, 0);
}
