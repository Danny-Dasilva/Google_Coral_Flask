import teach
import sys
from threading import Thread
from flask import Flask, send_file, Response, render_template
from io import BytesIO
from customCamera import Camera
app = Flask(__name__)
import time
def printVariable():
    time.sleep(1)
    while True:
        #print(teach.flaskImage)
        #print(teach.flaskStatus)
        time.sleep(0.05)

def flaskServer():
    print("ServerStarted")
    app.run(host='0.0.0.0', debug=False)

def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

@app.route('/')
def serve_img():
    return render_template('index.html')
def gen(cam):
    while True:
        img_io = BytesIO()
        teach.flaskImage.save(img_io, 'JPEG', quality=70)
        frame = cam.get_frame(img_io)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":

    #thread = Thread(target=printVariable)
    #thread.daemon = True

    thread1 = Thread(target=flaskServer)
    thread1.daemon = True
    #thread.start()
    thread1.start()

    teach.main(sys.argv)
    sys.exit(0)








