from app import Cam, Detect, Classify, Teachable
from flask import Flask, send_file, Response, render_template
import keyboard
from time import sleep
from threading import Thread, active_count
import signal
from threading import Thread, Event
from threading import Thread
import sys

#from adafruit_servokit import ServoKit
#kit = ServoKit(channels = 16)

app = Flask(__name__)


#Image = Cam.camera(Teachable.AI())

#Image = Cam.camera(Classify.AI())
#Image = Cam.camera(Detect.AI())
Image = Cam.camera('None')
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
 
if __name__ == "__main__":
    global status
    thread = Thread(target=flaskServer)
    thread.daemon = True
    thread.start()
    sleep(2)
    signal.signal(signal.SIGINT, signal_handler)
