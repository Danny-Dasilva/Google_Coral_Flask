from app import Detect, Classify, Teachable, Empty, pose_camera, anonymizer, synthesizer
from flask import Flask, send_file, Response, render_template
from app.Cam import camera
import keyboard
from time import sleep
from threading import Thread, active_count
import signal
from threading import Thread, Event
from threading import Thread
import sys



app = Flask(__name__)


Image = camera(synthesizer.AI())
#Image = camera(Teachable.AI())
#Image = camera(Classify.AI())
#Image = camera(Detect.AI())
#Image = camera(Empty.AI())
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
        result = Image.result
        print('result')

if __name__ == "__main__":
    global status
    thread = Thread(target=flaskServer)
    thread.start()
    # = Thread(target=Robot_code)
    #thread5.start()
    sleep(2)
    signal.signal(signal.SIGINT, signal_handler)


