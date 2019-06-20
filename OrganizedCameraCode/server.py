from Cam import camera
from flask import Flask, send_file, Response, render_template
import teach
from threading import Thread
import sys
Image = camera()
app = Flask(__name__)

@app.route('/video_feed')
def video_feed():
    return Response(Image.ImageStream(), mimetype='multipart/x-mixed-replace; boundary=frame')

def flaskServer():
    app.run(host='0.0.0.0', debug=False)

if __name__ == "__main__":
    thread = Thread(target=flaskServer)
    thread.daemon = True
    thread.start()
    print("Past")
    teach.main(sys.argv)
    while True:
        image = Image.PILImage()
        if(image != None):
            print(teach.teachable.classify(image))
