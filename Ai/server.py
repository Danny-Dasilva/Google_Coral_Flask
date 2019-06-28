from Cam import camera
from flask import Flask, send_file, Response, render_template
import teach
import keyboard
from time import sleep
import Image_classify
import face_detect

from threading import Thread, active_count
import signal
from threading import Thread

import sys
from adafruit_servokit import ServoKit
from time import sleep
kit = ServoKit(channels = 16)

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
    sys.exit()
def Robot_code():
    while True:
        sleep(0.01)
        result = Image.val

        if(result == "One"):
            print("One")
            #kit.servo[0].angle = 0
            kit.servo[0].angle = 0
            sleep(0.4)
            #kit.continuous_servo[1].throttle = 0.3
            kit.servo[1].angle = 0
        elif(result == "Two"):
            print("Two")
<<<<<<< HEAD
            #kit.servo[0].angle = 30
            #sleep(0)
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
    #print("7777777777777777")
=======
            #kit.servo[0].angle = 180
            kit.servo[0].angle = 30
            sleep(0.4)
            kit.servo[1].angle = 0
        else:
            kit.servo[1].angle = 17
        sys.exit(0)
>>>>>>> 991c6bc0de57cec63f2f1027fe195dd0ce27b9f5
