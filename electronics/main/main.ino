/*
 * Main Firmware for Robotics Project
 *
 * Hardware:
 * - ESP32-S3
 * - 4 DC Motors (BTS7960 Drivers)
 * - 1 Water Pump (L298N Driver)
 */

// Motors (BTS7960)
// Left Front
const int MOTOR_LF_RPWM = 25;
const int MOTOR_LF_LPWM = 26;

// Left Rear
const int MOTOR_LR_RPWM = 27;
const int MOTOR_LR_LPWM = 33;

// Right Front
const int MOTOR_RF_RPWM = 34;
const int MOTOR_RF_LPWM = 35;

// Right Rear
const int MOTOR_RR_RPWM = 32;
const int MOTOR_RR_LPWM = 13;

// Pump (L298N)
const int PUMP_IN1 = 14;
const int PUMP_IN2 = 12;
const int PUMP_ENA = 15;

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

void setupMotors() {
  pinMode(MOTOR_LF_RPWM, OUTPUT);
  pinMode(MOTOR_LF_LPWM, OUTPUT);
  pinMode(MOTOR_LR_RPWM, OUTPUT);
  pinMode(MOTOR_LR_LPWM, OUTPUT);
  pinMode(MOTOR_RF_RPWM, OUTPUT);
  pinMode(MOTOR_RF_LPWM, OUTPUT);
  pinMode(MOTOR_RR_RPWM, OUTPUT);
  pinMode(MOTOR_RR_LPWM, OUTPUT);
}

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
  analogWrite(MOTOR_LF_RPWM, speed);
  analogWrite(MOTOR_LF_LPWM, 0);
  analogWrite(MOTOR_LR_RPWM, speed);
  analogWrite(MOTOR_LR_LPWM, 0);
  analogWrite(MOTOR_RF_RPWM, 0);
  analogWrite(MOTOR_RF_LPWM, speed);
  analogWrite(MOTOR_RR_RPWM, 0);
  analogWrite(MOTOR_RR_LPWM, speed);
}

void setupPump() {
  pinMode(PUMP_IN1, OUTPUT);
  pinMode(PUMP_IN2, OUTPUT);
  pinMode(PUMP_ENA, OUTPUT);
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
