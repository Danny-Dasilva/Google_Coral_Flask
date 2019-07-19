
from app import Detect, Classify, Teachable, Empty
from flask import Flask, send_file, Response, render_template
from app.Cam import camera
import keyboard
from time import sleep
import time
from threading import Thread, active_count
import signal
from threading import Thread, Event
from threading import Thread
import sys
import serial
from adafruit_servokit import ServoKit


app = Flask(__name__)


Image = camera(Teachable.AI())

#Image = Cam.camera(Classify.AI())
#Image = Cam.camera(Detect.AI())
#Image = Cam.camera(Empty.AI())



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(Image.ImageStream(), mimetype='multipart/x-mixed-replace; boundary=frame')

def flaskServer():
    app.run(host="0.0.0.0", debug=False)

def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    sys.exit(0)

def Robot_code():
    global position

    target = 0
    drop_flag = False
    kit = ServoKit(channels=16)
    start_flag = False
    while True:
        sleep(0.01)
        result = Image.val
        print(result)
#        print(position)
        if(result == "Start"):
            start_flag = True
        if(not drop_flag and start_flag):
            if(result == "Board"):
                pass
            if(result == "One"):
                target = 0
                drop_flag = True
            if(result == "Two"):
                target = 1 * 36
                drop_flag = True
            if(result == "Three"):
                target = 2 * 36
                drop_flag = True
            if(result == "Four"):
                target =  3 * 36
                drop_flag = True
            if(result == "Five"):
                target =  4 * 36
                drop_flag = True
            if(result == "Six"):
                target =  5 * 36
                drop_flag = True
            if(result == "Seven"):
                target =  6 * 36
                drop_flag = True
            if(result == "Eight"):
                target =  7 * 36
                drop_flag = True
            if(result == "Nine"):
                target =  8 * 36
                drop_flag = True
            if(result == "Ten"):
                target =  9 * 36
                drop_flag = True

        if(target > position + 4):
            kit.continuous_servo[4].throttle = .15
        elif(target < position - 4):
            kit.continuous_servo[4].throttle = -.02
        else:
            kit.continuous_servo[4].throttle = .05
            if(drop_flag):
                drop_flag = False
                kit.servo[0].angle = 15
                sleep(2)
                kit.servo[0].angle = 30

def update_encoder():
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
        position = current_reading

if __name__ == "__main__":
    global status
    global position
    global kit

    position = 0
    thread = Thread(target=flaskServer)
    thread.start()
    thread3 = Thread(target=Robot_code)
    thread3.start()
    sleep(2)
    signal.signal(signal.SIGINT, signal_handler)
    thread1 = Thread(target=update_encoder, daemon=True)
    thread1.start()
