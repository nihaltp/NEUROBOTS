/*
 * Case B Firmware for Robotics Project
 * Direct control from Laptop to ESP32 via Wi-Fi WebSockets
 *
 * Required Libraries:
 * - ESPAsyncWebServer (https://github.com/mathieucarbou/ESPAsyncWebServer)
 * - AsyncTCP (https://github.com/mathieucarbou/AsyncTCP)
 */

#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include "../shared/Motors.h"
#include "../shared/Pump.h"
#include "../shared/CommandParser.h"

const char* ssid = "NEUROBOTS_AP";
const char* password = "neurobots123";

AsyncWebServer server(81);
AsyncWebSocket ws("/");

void onWebSocketEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type,
                      void *arg, uint8_t *data, size_t len) {
    switch (type) {
        case WS_EVT_CONNECT:
            Serial.printf("WebSocket client #%lu connected from %s\n", (long unsigned int)client->id(), client->remoteIP().toString().c_str());
            break;
        case WS_EVT_DISCONNECT:
            Serial.printf("WebSocket client #%lu disconnected\n", (long unsigned int)client->id());
            break;
        case WS_EVT_DATA: {
            AwsFrameInfo *info = (AwsFrameInfo*)arg;
            if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
                data[len] = 0;
                String command = (char*)data;
                command.trim();
                Serial.print("Received WS Command: ");
                Serial.println(command);
                processCommand(command);
            }
            break;
        }
        case WS_EVT_PONG:
        case WS_EVT_ERROR:
            break;
    }
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("Initializing Case B (Wi-Fi Direct) System...");

    setupMotors();
    setupPump();
    stopMotors();
    pumpOff(1);
    pumpOff(2);

    Serial.print("Setting up Access Point: ");
    Serial.println(ssid);
    WiFi.softAP(ssid, password);

    IPAddress IP = WiFi.softAPIP();
    Serial.print("AP IP Address: ");
    Serial.println(IP);

    ws.onEvent(onWebSocketEvent);
    server.addHandler(&ws);
    server.begin();

    Serial.println("WebSocket server started on port 81");
    Serial.println("Initialization Complete.");
}

void loop() {
    checkCommandTimeout();
    ws.cleanupClients();
}
