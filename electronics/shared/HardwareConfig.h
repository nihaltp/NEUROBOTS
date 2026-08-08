#ifndef HARDWARE_CONFIG_H
#define HARDWARE_CONFIG_H

// Serial Configuration
#define SERIAL_BAUD_RATE 115200

// Motors (BTS7960) Pin Definitions
// Left
#define MOTOR_L_RPWM 4  // Forward
#define MOTOR_L_LPWM 5  // Backward

// Right
#define MOTOR_R_RPWM 7  // Forward
#define MOTOR_R_LPWM 8  // Backward

// Pump 1 (L298N) Pin Definitions
#define PUMP1_IN1 14
#define PUMP1_IN2 12
#define PUMP1_ENA 15

// Pump 2 (L298N) Pin Definitions
#define PUMP2_IN1 16
#define PUMP2_IN2 17
#define PUMP2_ENA 18

#endif // HARDWARE_CONFIG_H
