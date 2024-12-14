#!/usr/bin/python3

import time
import serial
from picamera2 import Picamera2, Preview
import os  # Import os module for handling file paths

# Initialize the Picamera2 object
picam2 = Picamera2()

# Maximum resolution for the 16MP camera (preview set to 4096 as allowed)
max_resolution = (4656, 3496)  # Max capture resolution
preview_resolution = (4096, 2160)  # Adjusted preview resolution

# Create and configure the preview with the specified resolution
preview_config = picam2.create_preview_configuration(
    main={"size": preview_resolution, "format": "XBGR8888"}
)
picam2.configure(preview_config)

# Start the camera preview
picam2.start_preview(Preview.QTGL)
picam2.start()
time.sleep(1)

lensPosition = 8.3
#Use adjust cam lens script to calculate LensPosition
picam2.set_controls({"AfMode": 0, "LensPosition": lensPosition})
# Serial setup for Arduino data
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Replace with correct serial port
time.sleep(2)  # Allow time for the serial connection to initialize

# Track previous voltage for edge detection
previous_voltage = None

def capture_image():
    # Generate a unique filename based on the current time
    file_path = os.path.join(os.getcwd(), f"captured_image_{int(time.time())}.jpg")
    picam2.capture_file(file_path)
    print(f"Image captured and saved to {file_path}")
    time.sleep(1)  # Wait 1 seconds to avoid frequent captures

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
                current_voltage = float(voltage_str)  # Convert to float for comparison
                
                # Check for negative edge: current < 4 and previous >= 4
                if previous_voltage is not None and previous_voltage >= 4.0 and current_voltage < 4.0:
                    print(f"Negative edge detected: {previous_voltage} -> {current_voltage}")
                    capture_image()
                
                # Update previous voltage
                previous_voltage = current_voltage
                
        time.sleep(0.1)  # Delay for stability

except KeyboardInterrupt:
    print("Exiting program")

finally:
    ser.close()  # Close the serial connection
    picam2.stop()  # Stop the camera when done
