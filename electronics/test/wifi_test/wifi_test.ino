#include "../../shared/WiFiComms.h"

// Replace with your network credentials
const char* ssid = "NEUROBOT_ESP";
const char* password = "robot_password";

const unsigned int localPort = 12345;
WiFiComms wifiComms(ssid, password, localPort);

// The IP address of the Python server and its port 
// When ESP is AP, it usually assigns 192.168.4.2 to the first connected device (your laptop)
const char* targetIP = "192.168.4.2"; 
const unsigned int targetPort = 12346;

unsigned long lastSendTime = 0;

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    // Start as Access Point
    wifiComms.setupAP();
}

void loop() {
    // 1. Receive messages from Python
    String incoming = wifiComms.receiveMessage();
    if (incoming.length() > 0) {
        Serial.print("Received from Python: ");
        Serial.println(incoming);
    }

    // 2. Send messages to Python when user types in Serial Monitor
    if (Serial.available() > 0) {
        String msg = Serial.readStringUntil('\n');
        msg.trim(); // Remove whitespace/newlines
        if (msg.length() > 0) {
            wifiComms.sendMessage(targetIP, targetPort, msg.c_str());
            Serial.print("Sent to Python: ");
            Serial.println(msg);
        }
    }
}
