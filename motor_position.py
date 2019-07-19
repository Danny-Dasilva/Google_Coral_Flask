import serial
from adafruit_servokit import ServoKit
from threading import Thread

def updateEncoder():
    global position
    port = "/dev/ttyACM0"
    baudRate = 9600
    ser = serial.Serial(port=port, baudrate=baudRate)
    while True:
        current_reading = ""

        while True:
            token = ser.read()
            if(token == b'/'):
                current_reading = int(current_reading)
                break
            else:
                current_reading = current_reading + token.decode("utf-8")
#        print(current_reading)
        position = current_reading

global position
position = 0

thread1 = Thread(target=updateEncoder, daemon=True)
thread1.start()

kit = ServoKit(channels=16)

while True:
    print(position)
#    kit.continuous_servo[4].throttle = .1
