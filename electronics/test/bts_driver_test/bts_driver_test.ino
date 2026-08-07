/*
 * Test sketch for BTS7960 Motor Driver
 *
 * Requirements:
 * - ESP32-S3
 * - 4 DC Motors
 * - BTS Motor Drivers
 */

// Placeholder GPIO pins (Update these when wiring is known)
const int MOTOR_LF_RPWM = 25; // Left Front Right PWM
const int MOTOR_LF_LPWM = 26; // Left Front Left PWM
const int MOTOR_LR_RPWM = 27; // Left Rear Right PWM
const int MOTOR_LR_LPWM = 33; // Left Rear Left PWM

const int MOTOR_RF_RPWM = 34; // Right Front Right PWM
const int MOTOR_RF_LPWM = 35; // Right Front Left PWM
const int MOTOR_RR_RPWM = 32; // Right Rear Right PWM
const int MOTOR_RR_LPWM = 13; // Right Rear Left PWM

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Initializing BTS Driver Test...");

  // Set motor pins as outputs
  pinMode(MOTOR_LF_RPWM, OUTPUT);
  pinMode(MOTOR_LF_LPWM, OUTPUT);
  pinMode(MOTOR_LR_RPWM, OUTPUT);
  pinMode(MOTOR_LR_LPWM, OUTPUT);
  
  pinMode(MOTOR_RF_RPWM, OUTPUT);
  pinMode(MOTOR_RF_LPWM, OUTPUT);
  pinMode(MOTOR_RR_RPWM, OUTPUT);
  pinMode(MOTOR_RR_LPWM, OUTPUT);

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

// Reusable helper functions
void stopMotors() {
  analogWrite(MOTOR_LF_RPWM, 0);
  analogWrite(MOTOR_LF_LPWM, 0);
  analogWrite(MOTOR_LR_RPWM, 0);
  analogWrite(MOTOR_LR_LPWM, 0);
  analogWrite(MOTOR_RF_RPWM, 0);
  analogWrite(MOTOR_RF_LPWM, 0);
  analogWrite(MOTOR_RR_RPWM, 0);
  analogWrite(MOTOR_RR_LPWM, 0);
}

void moveForward(int speed) {
  analogWrite(MOTOR_LF_RPWM, speed);
  analogWrite(MOTOR_LF_LPWM, 0);
  analogWrite(MOTOR_LR_RPWM, speed);
  analogWrite(MOTOR_LR_LPWM, 0);
  analogWrite(MOTOR_RF_RPWM, speed);
  analogWrite(MOTOR_RF_LPWM, 0);
  analogWrite(MOTOR_RR_RPWM, speed);
  analogWrite(MOTOR_RR_LPWM, 0);
}

void moveBackward(int speed) {
  analogWrite(MOTOR_LF_RPWM, 0);
  analogWrite(MOTOR_LF_LPWM, speed);
  analogWrite(MOTOR_LR_RPWM, 0);
  analogWrite(MOTOR_LR_LPWM, speed);
  analogWrite(MOTOR_RF_RPWM, 0);
  analogWrite(MOTOR_RF_LPWM, speed);
  analogWrite(MOTOR_RR_RPWM, 0);
  analogWrite(MOTOR_RR_LPWM, speed);
}

void turnLeft(int speed) {
  // Left motors backward, right motors forward
  analogWrite(MOTOR_LF_RPWM, 0);
  analogWrite(MOTOR_LF_LPWM, speed);
  analogWrite(MOTOR_LR_RPWM, 0);
  analogWrite(MOTOR_LR_LPWM, speed);
  analogWrite(MOTOR_RF_RPWM, speed);
  analogWrite(MOTOR_RF_LPWM, 0);
  analogWrite(MOTOR_RR_RPWM, speed);
  analogWrite(MOTOR_RR_LPWM, 0);
}

void turnRight(int speed) {
  // Left motors forward, right motors backward
  analogWrite(MOTOR_LF_RPWM, speed);
  analogWrite(MOTOR_LF_LPWM, 0);
  analogWrite(MOTOR_LR_RPWM, speed);
  analogWrite(MOTOR_LR_LPWM, 0);
  analogWrite(MOTOR_RF_RPWM, 0);
  analogWrite(MOTOR_RF_LPWM, speed);
  analogWrite(MOTOR_RR_RPWM, 0);
  analogWrite(MOTOR_RR_LPWM, speed);
}
