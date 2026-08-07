#ifndef COMMAND_PARSER_H
#define COMMAND_PARSER_H

#include <Arduino.h>
#include "Motors.h"
#include "Pump.h"

void processCommand(String command) {
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
