#ifndef COMMAND_PARSER_H
#define COMMAND_PARSER_H

#include <Arduino.h>
#include "Motors.h"
#include "Pump.h"

void processCommand(String command) {
  int speed_percent = 60; // default ~150 PWM
  int colonIndex = command.indexOf(':');
  
  if (colonIndex != -1 && (command.startsWith("F") || command.startsWith("B") || command.startsWith("L") || command.startsWith("R"))) {
    speed_percent = command.substring(colonIndex + 1).toInt();
    speed_percent = constrain(speed_percent, 0, 100);
  }
  
  int pwm_speed = map(speed_percent, 0, 100, 0, 255);

  if (command.startsWith("F")) {
    Serial.println("ACK: Moving Forward");
    moveForward(pwm_speed);
  } else if (command.startsWith("B")) {
    Serial.println("ACK: Moving Backward");
    moveBackward(pwm_speed);
  } else if (command.startsWith("L")) {
    Serial.println("ACK: Turning Left");
    turnLeft(pwm_speed);
  } else if (command.startsWith("R")) {
    Serial.println("ACK: Turning Right");
    turnRight(pwm_speed);
  } else if (command.startsWith("S")) {
    Serial.println("ACK: Stopping");
    stopMotors();
  } else if (command.startsWith("P1:1")) {
    Serial.println("ACK: Pump 1 ON");
    pumpOn(1, 255);
  } else if (command.startsWith("P1:0")) {
    Serial.println("ACK: Pump 1 OFF");
    pumpOff(1);
  } else if (command.startsWith("P2:1")) {
    Serial.println("ACK: Pump 2 ON");
    pumpOn(2, 255);
  } else if (command.startsWith("P2:0")) {
    Serial.println("ACK: Pump 2 OFF");
    pumpOff(2);

  } else {
    Serial.print("ERR: Unknown Command: ");
    Serial.println(command);
  }
}

#endif // COMMAND_PARSER_H
