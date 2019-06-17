from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context, send_file
from random import random
from time import sleep
from threading import Thread, Event
import socket
from PIL import Image
import io



app = Flask(__name__)

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 1234))




def serve_pil_image(pil_img):
    img_io = io.BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')
    
@app.route('/')
def serve_img():
    msg = s.recv(172833)
    # print(msg.decode("utf-8"))
    # number = round(random()*10, 3)
    
    #
    #img.mode, img.size
    m = "RGB"
    si = (320, 180)
    if msg:

        number = Image.frombytes(m, si, msg)
        # number.save("working_functional_image.png")
        img = number
       
        
    return serve_pil_image(img)




if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)

        
    










    