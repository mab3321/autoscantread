#!/bin/bash

# Define the serial port and baud rate
SERIAL_PORT="/dev/ttyUSB0"
BAUD_RATE="9600"

# Configure the serial port
stty -F "$SERIAL_PORT" "$BAUD_RATE" cs8 -cstopb -parenb

# Start libcamera-still in keypress mode in the background
libcamera-still -t 0 --keypress --datetime &
LIBCAMERA_PID=$!

# Ensure libcamera-still terminates on script exit
trap "kill $LIBCAMERA_PID" EXIT

echo "Monitoring sensor data from $SERIAL_PORT..."
# Read data from the serial port
while IFS= read -r line; do
    # Read from serial port
    line=$(cat "$SERIAL_PORT")
    echo "Sensor Data: $line"

    # Check if the line contains the voltage data
    if [[ "$line" == *"|"* ]]; then
        # Extract the voltage value
        voltage=$(echo "$line" | awk -F'|' '{print $2}' | awk -F':' '{print $2}' | tr -d '[:space:]')

        # Convert to float for comparison
        if (( $(echo "$voltage < 4.0" | bc -l) )); then
            echo "Voltage below threshold ($voltage). Triggering capture..."
            
            # Simulate "Enter" key press
            echo -ne '\n' > "/proc/$LIBCAMERA_PID/fd/0"
        fi
    fi
done < "$SERIAL_PORT"
