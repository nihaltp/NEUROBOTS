#ifndef MOTORS_H
#define MOTORS_H

#include <Arduino.h>

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

#endif // MOTORS_H
