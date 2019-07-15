from Cam import camera
from flask import Flask, send_file, Response, render_template
import teach
import keyboard
from time import sleep
import Image_classify
import face_detect
from GoDrone import drone

from threading import Thread, active_count
import signal
from threading import Thread

import sys
#from adafruit_servokit import ServoKit
from time import sleep
#kit = ServoKit(channels = 16)

app = Flask(__name__)
#Image = camera(teach.AI())
Drone = drone()
#Image = camera(Image_classify.AI())
Image = camera(face_detect.AI())
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
    sys.exit()
def Drone_code():
    while True:
        sleep(0.01)
        Drone.sendSBUSData(Drone.channels)
    

if __name__ == "__main__":
    thread = Thread(target=flaskServer)
    thread.daemon = True
    thread.start()
    thread1 = Thread(target=Drone_code)
    thread1.daemon = True
    thread1.start()
    sleep(2)
    signal.signal(signal.SIGINT, signal_handler)
