#ifndef COMMAND_PARSER_H
#define COMMAND_PARSER_H

#include <Arduino.h>
#include "Motors.h"
#include "Pump.h"

unsigned long lastCommandTime = 0;
const unsigned long COMMAND_TIMEOUT_MS = 2000; // Stop hardware if no command for 2 seconds

void checkCommandTimeout() {
  // If we have received a command before, and time elapsed exceeds timeout
  if (lastCommandTime > 0 && millis() - lastCommandTime > COMMAND_TIMEOUT_MS) {
    stopMotors();
    pumpOff(1);
    pumpOff(2);
    lastCommandTime = 0; // Reset so it doesn't repeatedly call stop
    Serial.println("ERR: Command Timeout! Halted all hardware for safety.");
  }
}

void processCommand(String command) {
  lastCommandTime = millis();
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
  } else if (command.startsWith("STOPALL")) {
    Serial.println("ACK: HALT ALL");
    stopMotors();
    pumpOff(1);
    pumpOff(2);

  } else {
    Serial.print("ERR: Unknown Command: ");
    Serial.println(command);
  }
}

#endif // COMMAND_PARSER_H
