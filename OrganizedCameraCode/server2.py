from Cam import camera
from flask import Flask, send_file, Response, render_template
import teach
from threading import Thread
from UpdateString import RandomThread
import sys


app = Flask(__name__)
Image = camera(teach.AI())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(Image.ImageStream(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
