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


#Image = camera(anonymizer.AI())
#Image = camera(Teachable.AI())
Image = camera(Classify.AI())
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

def my_function():
    while True:
        sleep(0.01)
        #result = Image.result
        # count = Image.numImages
        # fps = Image.fps
        # Inference = Image.inference
        # Class = Image.Class
        # Score = Image.Score

        #print(result)

if __name__ == "__main__":
    global status
    thread = Thread(target=flaskServer)
    thread.start()
    thread5 = Thread(target=my_function)
    thread5.start()
    sleep(2)
    signal.signal(signal.SIGINT, signal_handler)


