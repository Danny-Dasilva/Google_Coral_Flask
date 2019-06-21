from Cam import camera
from flask import Flask, send_file, Response, render_template
import teach
from threading import Thread
from UpdateString import RandomThread
import sys
from adafruit_servokit import ServoKit
kit = ServoKit(channels = 16)

app = Flask(__name__)
Image = camera(teach.AI())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(Image.ImageStream(), mimetype='multipart/x-mixed-replace; boundary=frame')

def flaskServer():
    app.run(host="0.0.0.0", debug=False)

if __name__ == "__main__":
    global status
    thread = Thread(target=flaskServer)
    thread.daemon = True
    thread.start()
    while True:
        result = Image.result
        if(result == "One"):
            print("One")
            kit.servo[0].angle = 0
        elif(result == "Two"):
            print("Two")
            kit.servo[0].angle = 180
