from Cam import camera
from flask_socketio import SocketIO
from flask import Flask, send_file, Response, render_template
import teach
from threading import Thread
from UpdateString import RandomThread
import sys
from adafruit_servokit import ServoKit
kit = ServoKit(channels = 16)

app = Flask(__name__)
socketio = SocketIO(app, async_mode='gevent')
Image = camera(teach.AI(), socketio)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(Image.ImageStream(), mimetype='multipart/x-mixed-replace; boundary=frame')

def flaskServer():
    socketio.run(app, host="0.0.0.0")

if __name__ == "__main__":
    global status
    thread = Thread(target=flaskServer)
    thread.daemon = True
    thread.start()
    while True:
        result = Image.getAIResult()
        if(result == "One"):
            kit.servo[0].angle = 0
        elif(result == "Two"):
            kit.servo[0].angle = 180
