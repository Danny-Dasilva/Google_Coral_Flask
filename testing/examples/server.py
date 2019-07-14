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
servo_max = 110
servo_min = 70
servo_max1 = 100
servo_min1 = 80
app = Flask(__name__)
#Image = camera(teach.AI())
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
    position = 90
    position1 = 90
    while True:
        sleep(.03)
        result = Image.val
        
        if result:
            for i in result:
                x = i[1]
                y = i[2]
                #print(y)
                if x < .35:
                    position = position + .25
                    if position > servo_max:
                        position = servo_max
                if x > .45:
                    position = position - .25
                    if position < servo_min:
                        position = servo_min

                kit.servo[1].angle = position
                if y < .20:
                    position1 = position1 + .1
                    if position1 > servo_max1:
                        print('max angle met')
                        position1 = servo_max1
                if y > .35:
                    position1 = position1 - .1
                    if position1 < servo_min1:
                        position1 = servo_min1

                kit.servo[0].angle = position1
                print(y)  
                print(position1)
                #kit.servo[1].angle = 40 + 100 * -x

if __name__ == "__main__":
    thread = Thread(target=flaskServer)
    thread.daemon = True
    thread.start()
    thread1 = Thread(target=Drone_code)
    thread1.daemon = True
    thread1.start()
    sleep(2)
    signal.signal(signal.SIGINT, signal_handler)
