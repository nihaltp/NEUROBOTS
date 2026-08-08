#ifndef MOTORS_H
#define MOTORS_H

#include <Arduino.h>
#include "HardwareConfig.h"

void setupMotors() {
  pinMode(MOTOR_L_RPWM, OUTPUT);
  pinMode(MOTOR_L_LPWM, OUTPUT);
  pinMode(MOTOR_R_RPWM, OUTPUT);
  pinMode(MOTOR_R_LPWM, OUTPUT);
}

void stopMotors() {
  analogWrite(MOTOR_L_RPWM, 0);
  analogWrite(MOTOR_L_LPWM, 0);
  analogWrite(MOTOR_R_RPWM, 0);
  analogWrite(MOTOR_R_LPWM, 0);
}

void moveForward(int speed) {
  analogWrite(MOTOR_L_RPWM, speed);
  analogWrite(MOTOR_L_LPWM, 0);
  analogWrite(MOTOR_R_RPWM, speed);
  analogWrite(MOTOR_R_LPWM, 0);
}

void moveBackward(int speed) {
  analogWrite(MOTOR_L_RPWM, 0);
  analogWrite(MOTOR_L_LPWM, speed);
  analogWrite(MOTOR_R_RPWM, 0);
  analogWrite(MOTOR_R_LPWM, speed);
}

void turnLeft(int speed) {
  analogWrite(MOTOR_L_RPWM, 0);
  analogWrite(MOTOR_L_LPWM, speed);
  analogWrite(MOTOR_R_RPWM, speed);
  analogWrite(MOTOR_R_LPWM, 0);
}

void turnRight(int speed) {
  analogWrite(MOTOR_L_RPWM, speed);
  analogWrite(MOTOR_L_LPWM, 0);
  analogWrite(MOTOR_R_RPWM, 0);
  analogWrite(MOTOR_R_LPWM, speed);
}

void turnHalfLeft(int speed) {
  analogWrite(MOTOR_L_RPWM, 0);
  analogWrite(MOTOR_L_LPWM, 0);
  analogWrite(MOTOR_R_RPWM, speed);
  analogWrite(MOTOR_R_LPWM, 0);
}

void turnHalfRight(int speed) {
  analogWrite(MOTOR_L_RPWM, speed);
  analogWrite(MOTOR_L_LPWM, 0);
  analogWrite(MOTOR_R_RPWM, 0);
  analogWrite(MOTOR_R_LPWM, 0);
}

#endif // MOTORS_H
