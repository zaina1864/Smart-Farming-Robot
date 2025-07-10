# bottle2rover.py – Web-controlled Smart Farming Rover (AIRE305 Project)
# This script runs a Bottle web server to receive robot movement commands via AJAX
# and control an Arduino-connected rover and GPIO-based spray system.

from bottle import route, run, static_file, request
import serial
import time
import RPi.GPIO as GPIO

# GPIO Setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)  # Relay control pin for spraying

# Serial Communication Setup with Arduino
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=5)
ser.flush()

# Command Codes (must match with Arduino side)
Forward = 10
Backward = 20
Right = 30
Left = 4
startStep = 50
stopCar = 70

# Moisture result stored here (used in /action response)
moisture = "Not Detected Yet"

def rover(action):
    """Interprets action strings and sends corresponding serial or GPIO commands."""
    global moisture
    messageCode = ""

    if action == "forward":
        print("Moving Forward")
        messageCode = str(Forward)

    elif action == "backward":
        print("Moving Backward")
        messageCode = str(Backward)

    elif action == "left":
        print("Turning Left")
        messageCode = str(Left)

    elif action == "right":
        print("Turning Right")
        messageCode = str(Right)

    elif action == "stop":
        print("Stopping Rover")
        messageCode = str(stopCar)

    elif action == "spray":
        print("Activating Sprayer")
        GPIO.output(17, True)
        time.sleep(2)
        GPIO.output(17, False)
        return  # no serial data

    elif action == "startM":
        print("Starting Moisture Measurement")
        messageCode = str(startStep)
        messageCode += "\n"
        ser.write(messageCode.encode('utf-8'))
        time.sleep(4)
        moisture = ser.readline().decode('utf-8').rstrip()
        print("Moisture Level:", moisture)
        return  # moisture already updated

    # For motor commands
    if messageCode:
        messageCode += "\n"
        ser.write(messageCode.encode('utf-8'))
        receive_string = ser.readline().decode('utf-8').rstrip()
        print("Arduino says:", receive_string)

# Serve the control HTML interface (index.html)
@route('/')
def server_static():
    return static_file("index.html", root='')

# AJAX endpoint for receiving movement/sensor actions
@route('/action')
def get_action():
    action = request.headers.get('myaction')
    print("Requested action:", action)
    rover(action)
    return str(moisture)

# Run the Bottle server (change host to your Pi's IP)
run(host='192.168.0.101', port=8080, debug=False)
