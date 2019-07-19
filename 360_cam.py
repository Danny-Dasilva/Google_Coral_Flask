from app import Cam, Detect, Classify, Teachable
from flask import Flask, send_file, Response, render_template
import keyboard
from time import sleep
from threading import Thread, active_count
import signal
from threading import Thread, Event
from threading import Thread
import sys
from adafruit_servokit import ServoKit


kit = ServoKit(channels = 16)

app = Flask(__name__)
#Image = Cam.camera(Teachable.AI())
#Image = Cam.camera(Classify.AI())
Image = Cam.camera(Detect.AI())




servo_max = 110
servo_min = 70
servo_max1 = 100
servo_min1 = 80


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
    servo_1 = 90
    servo_2 = 90
    while True:
        sleep(.03)
        result = Image.val
        
        if result:
            for i in result:
                x = i[1]
                y = i[2]
                #print(y)
                if x < .35:
                    servo_1 = servo_1 + .25
                    if servo_1 > servo_max:
                        servo_1 = servo_max
                if x > .45:
                    servo_1 = servo_1 - .25
                    if servo_1 < servo_min:
                        servo_1 = servo_min

                kit.servo[1].angle = servo_1
                if y < .20:
                    servo_2 = servo_2 + .1
                    if servo_2 > servo_max1:
                        print('max angle met')
                        servo_2 = servo_max1
                if y > .35:
                    servo_2 = servo_2 - .1
                    if servo_2 < servo_min1:
                        servo_2 = servo_min1

                kit.servo[0].angle = servo_2
                print(y)
                print(servo_2)

if __name__ == "__main__":
    thread = Thread(target=flaskServer)
    thread.daemon = True
    thread.start()
    thread1 = Thread(target=Drone_code)
    thread1.daemon = True
    thread1.start()
    sleep(2)
    signal.signal(signal.SIGINT, signal_handler)
