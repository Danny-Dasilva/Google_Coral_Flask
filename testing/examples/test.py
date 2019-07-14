from testing import camera
from flask import Flask, send_file, Response, render_template
from testing import teach
import keyboard
from time import sleep
from testing import Image_classify
from testing import face_detect
from threading import Thread, active_count
import signal
from threading import Thread, Event
from threading import Thread
import sys

#from adafruit_servokit import ServoKit
from time import sleep
#kit = ServoKit(channels = 16)

app = Flask(__name__)


Image = camera(teach.AI())

#Image = camera(Image_classify.AI())
#Image = camera(face_detect.AI())
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
    while True:
        sleep(0.01)
        result = Image.val
        print(result)
        #print(Image.val)
        #kit.servo[0].angle = 15
        #print("zero")
        #sleep(3)
        #kit.servo[0].angle = 30
        #sleep(3)
        #kit.servo[0].angle = 0
        #sleep(3)
        #kit.servo[1].angle = 0-
        #sleep(3)
        #kit.servo[1].angle = 45
        #sleep(3)
        '''different'''
 
if __name__ == "__main__":
    global status
    thread = Thread(target=flaskServer)
    thread.daemon = True
    thread.start()
    sleep(2)
    signal.signal(signal.SIGINT, signal_handler)
