from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context, send_file
from random import random
from time import sleep
from threading import Thread, Event
import socket
from PIL import Image
import datetime
import io

__author__ = 'slynn'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

#turn the flask app into a socketio app
socketio = SocketIO(app)

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 1234))

class RandomThread(Thread):
    def __init__(self):
        self.delay = .05
        super(RandomThread, self).__init__()

    def randomNumberGenerator(self):
        """
        Generate a random number every 1 second and emit to a socketio instance (broadcast)
        Ideally to be run in a separate thread?
        """
        #infinite loop of magical random numbers
        print("Making random numbers")
        message = []
        while not thread_stop_event.isSet():
            
        
            msg = s.recv(8)
            # print(msg.decode("utf-8"))
            # number = round(random()*10, 3)
            
            #
            #img.mode, img.size
            m = "RGB"
            si = (320, 180)
            # if 172833:
                
            #     number = Image.frombytes(m, si, msg)
            #     number.save(str(datetime.datetime.now().time()) + "image.png")
            #     #socketio.emit('newnumber', {'number': number}, namespace='/test')
                sleep(self.delay)

    def run(self):
        self.randomNumberGenerator()





@app.route('/')
def index():
    #only by sending this page first will the client be connected to the socketio instance
    return render_template('index.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')

    #Start the random number generator thread only if the thread has not been started before.
    if not thread.isAlive():
        print("Starting Thread")
        thread = RandomThread()
        thread.start()

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=False)

        
    










    