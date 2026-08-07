/*
 * Case C Firmware for Robotics Project
 * Direct control from Laptop to ESP32 via Bluetooth Low Energy (BLE)
 *
 * Required Libraries:
 * - NimBLE-Arduino (https://github.com/h2zero/NimBLE-Arduino)
 */

#include <Arduino.h>
#include <NimBLEDevice.h>
#include "../shared/Motors.h"
#include "../shared/Pump.h"
#include "../shared/CommandParser.h"

// BLE Configuration
static const char* DEVICE_NAME = "NeuroBot";
static const char* SERVICE_UUID = "3d0cf6a3-5f45-43b5-9d5b-5baf86d8a7b1";
static const char* COMMAND_CHAR_UUID = "d5f8a0cd-ec8a-4e48-b60d-3277a0afbd45";
static const char* STATUS_CHAR_UUID = "4d869ab8-f78c-4e9f-aee5-73452e0a5e3d";

static NimBLEServer* pServer = nullptr;
static NimBLECharacteristic* pCommandChar = nullptr;
static NimBLECharacteristic* pStatusChar = nullptr;

class ServerCallbacks : public NimBLEServerCallbacks {
    void onConnect(NimBLEServer* pServer) {
        Serial.println("BLE Client Connected");
        NimBLEDevice::startAdvertising(); // Allow multiple connections or just continue advertising
    }

    void onDisconnect(NimBLEServer* pServer) {
        Serial.println("BLE Client Disconnected");
        // Stop motors when disconnected for safety
        stopMotors();
        pumpOff(1);
        pumpOff(2);
        // Restart advertising
        NimBLEDevice::startAdvertising();
        Serial.println("Restarted Advertising");
    }
};

class CommandCallbacks : public NimBLECharacteristicCallbacks {
    void onWrite(NimBLECharacteristic* pCharacteristic) {
        std::string rxValue = pCharacteristic->getValue();
        if (rxValue.length() > 0) {
            String command = String(rxValue.c_str());
            command.trim(); // Remove any stray whitespace or newlines
            
            Serial.print("Received BLE Command: ");
            Serial.println(command);
            
            // Process the command using the unchanged CommandParser
            processCommand(command);
            
            // Send ACK back to Python via status characteristic
            String ackMsg = "ACK:" + command;
            if (pStatusChar) {
                pStatusChar->setValue(ackMsg.c_str());
                pStatusChar->notify();
            }
        }
    }
};

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("Initializing Case C (BLE Direct) System...");

    // Initialize hardware
    setupMotors();
    setupPump();
    stopMotors();
    pumpOff(1);
    pumpOff(2);

    // Initialize BLE
    NimBLEDevice::init(DEVICE_NAME);
    NimBLEDevice::setPower(ESP_PWR_LVL_P9); // Maximum power
    
    pServer = NimBLEDevice::createServer();
    pServer->setCallbacks(new ServerCallbacks());
    
    NimBLEService* pService = pServer->createService(SERVICE_UUID);
    
    pCommandChar = pService->createCharacteristic(
        COMMAND_CHAR_UUID,
        NIMBLE_PROPERTY::WRITE | NIMBLE_PROPERTY::WRITE_NR
    );
    pCommandChar->setCallbacks(new CommandCallbacks());
    
    pStatusChar = pService->createCharacteristic(
        STATUS_CHAR_UUID,
        NIMBLE_PROPERTY::NOTIFY | NIMBLE_PROPERTY::READ
    );
    pStatusChar->setValue("READY");
    
    pService->start();
    
    NimBLEAdvertising* pAdvertising = NimBLEDevice::getAdvertising();
    pAdvertising->addServiceUUID(SERVICE_UUID);
    pAdvertising->enableScanResponse(true);
    pAdvertising->setName(DEVICE_NAME);
    pAdvertising->start();
    
    Serial.println("BLE Advertising Started. Waiting for connections...");
    Serial.println("Initialization Complete.");
}

void loop() {
    // BLE is handled asynchronously via NimBLE callbacks.
    // Periodic status updates could be sent here (e.g., battery).
    delay(10);
}
