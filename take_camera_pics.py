#!/usr/bin/python3

import time
import serial
from picamera2 import Picamera2, Preview
import os  # Import os module for handling file paths

# Initialize the Picamera2 object
picam2 = Picamera2()
picam2.start_preview(Preview.QTGL)

# Create and configure the preview with a compatible format for QGlPicamera2
preview_config = picam2.create_preview_configuration(
    main={"size": (2328, 1748), "format": "XBGR8888"}
)
picam2.configure(preview_config)

# Start the camera
picam2.start()
time.sleep(1)

# Serial setup for Arduino data
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Replace with correct serial port
time.sleep(2)  # Allow time for the serial connection to initialize

def capture_image():
    # Generate a unique filename based on the current time
    file_path = os.path.join(os.getcwd(), f"captured_image_{int(time.time())}.jpg")
    picam2.capture_file(file_path)
    print(f"Image captured and saved to {file_path}")

try:
    print("Monitoring sensor data...")
    while True:
        if ser.in_waiting > 0:
            # Read data from Arduino
            data = ser.readline().decode('utf-8').strip()
            print("Sensor Value:", data)
            
            # Parse sensor value and voltage from the received data
            if "|" in data:
                parts = data.split("|")
                voltage_str = parts[1].split(":")[1].strip()  # Extract voltage part
                voltage = float(voltage_str)  # Convert to float for comparison
                
                # Check if voltage is below threshold
                if voltage < 4.0:
                    capture_image()
                
        time.sleep(0.1)  # Delay for stability

except KeyboardInterrupt:
    print("Exiting program")

finally:
    ser.close()  # Close the serial connection
    picam2.stop()  # Stop the camera when done
