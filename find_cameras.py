import cv2

def find_cameras():
    print("Scanning for connected cameras (indices 0-10)...")
    found_any = False
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"Camera found at index: {i}")
            found_any = True
            cap.release()
    
    if not found_any:
        print("No cameras found.")

if __name__ == "__main__":
    find_cameras()
