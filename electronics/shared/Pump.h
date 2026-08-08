#ifndef PUMP_H
#define PUMP_H

#include <Arduino.h>
#include "HardwareConfig.h"

void setupPump() {
  pinMode(PUMP1_IN1, OUTPUT);
  pinMode(PUMP1_IN2, OUTPUT);
  pinMode(PUMP1_ENA, OUTPUT);
  
  pinMode(PUMP2_IN1, OUTPUT);
  pinMode(PUMP2_IN2, OUTPUT);
  pinMode(PUMP2_ENA, OUTPUT);
}

void pumpOn(int pump_id, int speed) {
  if (pump_id == 1) {
    digitalWrite(PUMP1_IN1, HIGH);
    digitalWrite(PUMP1_IN2, LOW);
    analogWrite(PUMP1_ENA, speed);
  } else if (pump_id == 2) {
    digitalWrite(PUMP2_IN1, HIGH);
    digitalWrite(PUMP2_IN2, LOW);
    analogWrite(PUMP2_ENA, speed);
  }
}

void pumpOff(int pump_id) {
  if (pump_id == 1) {
    digitalWrite(PUMP1_IN1, LOW);
    digitalWrite(PUMP1_IN2, LOW);
    analogWrite(PUMP1_ENA, 0);
  } else if (pump_id == 2) {
    digitalWrite(PUMP2_IN1, LOW);
    digitalWrite(PUMP2_IN2, LOW);
    analogWrite(PUMP2_ENA, 0);
  }
}

#endif // PUMP_H
