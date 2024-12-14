#!/usr/bin/python3

import time
import os  # Import os module for handling file paths
from picamera2 import Picamera2, Preview

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
# Use adjust cam lens script to calculate LensPosition
picam2.set_controls({"AfMode": 0, "LensPosition": lensPosition})

def capture_image():
    # Generate a unique filename based on the current time
    file_path = os.path.join(os.getcwd(), f"captured_image_{int(time.time())}.jpg")
    picam2.capture_file(file_path)
    print(f"Image captured and saved to {file_path}")
    time.sleep(1)  # Wait 1 second to avoid frequent captures

try:
    print("Press Enter to capture an image, or type 'exit' to quit...")
    while True:
        # Check if Enter key was pressed
        user_input = input("Press Enter to capture an image, or type 'exit' to quit: ")
        if user_input == "":
            capture_image()

        if user_input.lower() == "exit":
            print("Exiting program...")
            break

except KeyboardInterrupt:
    print("Exiting program")

finally:
    picam2.stop()  # Stop the camera when done
