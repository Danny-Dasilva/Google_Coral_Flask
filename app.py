import teach
import sys
from threading import Thread
from flask import Flask, send_file
from io import BytesIO
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
    return serve_pil_image(teach.flaskImage)
if __name__ == "__main__":

    #thread = Thread(target=printVariable)
    #thread.daemon = True

    thread1 = Thread(target=flaskServer)
    thread1.daemon = True
    #thread.start()
    thread1.start()

    teach.main(sys.argv)
    sys.exit(0)








