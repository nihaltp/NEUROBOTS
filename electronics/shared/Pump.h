#ifndef PUMP_H
#define PUMP_H

#include <Arduino.h>

// Pump (L298N)
const int PUMP_IN1 = 14;
const int PUMP_IN2 = 12;
const int PUMP_ENA = 15;

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

#endif // PUMP_H
