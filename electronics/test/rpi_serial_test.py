import serial
import time

# Update the port with the actual serial port connected to ESP32
# e.g., '/dev/ttyUSB0' or '/dev/serial0' on Raspberry Pi
# SERIAL_PORT = '/dev/ttyUSB0'
SERIAL_PORT = 'COM5'
BAUD_RATE = 115200

def main():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to ESP32 on {SERIAL_PORT} at {BAUD_RATE} baud.")
        time.sleep(2) # Wait for ESP32 to reset

        commands = ['F', 'S', 'B', 'S', 'L', 'S', 'R', 'S', 'P1', 'P0']
        
        for cmd in commands:
            print(f"Sending command: {cmd}")
            ser.write((cmd + '\n').encode('utf-8'))
            
            # Read response
            time.sleep(0.5)
            while ser.in_waiting > 0:
                response = ser.readline().decode('utf-8').strip()
                print(f"ESP32: {response}")
                
            time.sleep(1.5)
            
        print("\nAutomated test finished.")
        print("Enter commands manually (F, B, L, R, S, P1, P0). Type 'exit' to quit.")
        while True:
            user_cmd = input("Command: ").strip()
            if user_cmd.lower() == 'exit':
                break
                
            if user_cmd:
                ser.write((user_cmd + '\n').encode('utf-8'))
                
                # Give ESP32 a moment to respond
                time.sleep(0.1)
                while ser.in_waiting > 0:
                    response = ser.readline().decode('utf-8').strip()
                    print(f"ESP32: {response}")
            
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial connection closed.")

if __name__ == '__main__':
    main()
