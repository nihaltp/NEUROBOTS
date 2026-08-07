#ifndef WIFI_COMMS_H
#define WIFI_COMMS_H

#include <WiFi.h>
#include <WiFiUdp.h>

class WiFiComms {
private:
    const char* ssid;
    const char* password;
    unsigned int localPort;
    WiFiUDP udp;
    char incomingPacket[255];

public:
    WiFiComms(const char* ssid, const char* password, unsigned int port) {
        this->ssid = ssid;
        this->password = password;
        this->localPort = port;
    }

    void setup() {
        Serial.printf("Connecting to %s ", ssid);
        WiFi.begin(ssid, password);
        while (WiFi.status() != WL_CONNECTED) {
            delay(500);
            Serial.print(".");
        }
        Serial.println(" CONNECTED");
        Serial.print("IP Address: ");
        Serial.println(WiFi.localIP());

        udp.begin(localPort);
        Serial.printf("Listening on UDP port %d\n", localPort);
    }

    // Start ESP as a Wi-Fi Access Point
    void setupAP() {
        Serial.printf("Starting Access Point: %s\n", ssid);
        // By default, this assigns the ESP the IP 192.168.4.1
        WiFi.softAP(ssid, password);
        
        IPAddress IP = WiFi.softAPIP();
        Serial.print("AP IP Address: ");
        Serial.println(IP);

        udp.begin(localPort);
        Serial.printf("Listening on UDP port %d\n", localPort);
    }

    // Check if a message was received and return it
    String receiveMessage() {
        int packetSize = udp.parsePacket();
        if (packetSize) {
            int len = udp.read(incomingPacket, 254);
            if (len > 0) {
                incomingPacket[len] = 0;
            }
            return String(incomingPacket);
        }
        return "";
    }

    // Send a message to a specific IP and port
    void sendMessage(const char* ipAddress, unsigned int port, const char* message) {
        udp.beginPacket(ipAddress, port);
        udp.printf("%s", message);
        udp.endPacket();
    }
};

#endif
