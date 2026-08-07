import time
import sys
import threading
from shared.wifi_comms import WiFiComms

# Global queue for user input
user_input_queue = []

def input_thread():
    while True:
        try:
            msg = input()
            if msg.strip():
                user_input_queue.append(msg.strip())
        except EOFError:
            break

def main():
    # Provide the ESP32 IP address (Default for ESP AP is usually 192.168.4.1)
    esp_ip = "192.168.4.1" 
    esp_port = 12345
    
    print(f"Starting Python WiFi Comms Test on UDP port 12346")
    print(f"Target ESP32 IP: {esp_ip}:{esp_port}")
    print("Type a message and press Enter to send to ESP32")
    print("Press Ctrl+C to exit")
    
    comms = WiFiComms(local_port=12346)
    
    # Start the input thread
    t = threading.Thread(target=input_thread, daemon=True)
    t.start()
    
    try:
        while True:
            # 1. Receive messages from ESP
            msg, addr = comms.receive_message()
            if msg:
                # Use carriage return to overwrite the current input line temporarily
                print(f"\rReceived from ESP ({addr[0]}): {msg}")
                
            # 2. Send messages to ESP when user types in terminal
            if user_input_queue:
                out_msg = user_input_queue.pop(0)
                comms.send_message(esp_ip, esp_port, out_msg)
                print(f"Sent to ESP: {out_msg}")
                
            time.sleep(0.01) # Small delay to prevent CPU hogging
            
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        comms.close()

if __name__ == "__main__":
    main()
