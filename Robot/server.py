from Cam import camera
from flask import Flask, send_file, Response, render_template
import teach
import keyboard
from time import sleep
import Image_classify
import face_detect
from threading import Thread, active_count
import signal
<<<<<<< HEAD
from threading import Thread, Event

=======
from threading import Thread
>>>>>>> a791a0c3aa46feaead11e8538ef2129addac1ff3
import sys


#from adafruit_servokit import ServoKit
#kit = ServoKit(channels = 16)

app = Flask(__name__)
<<<<<<< HEAD
#Image = camera(teach.AI())
=======


Image = camera(teach.AI())
>>>>>>> a791a0c3aa46feaead11e8538ef2129addac1ff3
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
    sys.exit(0)

def Robot_code():
    while True:
        sleep(0.01)
        result = Image.val
        print(Image.val)
        #kit.servo[0].angle = 15
        #print("zero")
        #sleep(3)
        #kit.servo[0].angle = 30
        #sleep(3)
        #kit.servo[0].angle = 0
        #sleep(3)
        #kit.servo[1].angle = 0
        #sleep(3)
        #kit.servo[1].angle = 45
        #sleep(3)
       
if __name__ == "__main__":
    global status
    thread = Thread(target=flaskServer)
    thread.daemon = True
    thread.start()
    sleep(2)
    thread2 = Thread(target=Robot_code)
    thread2.deamon = True
    thread2.start()
    signal.signal(signal.SIGINT, signal_handler)
