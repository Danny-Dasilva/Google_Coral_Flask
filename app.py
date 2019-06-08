from teachable import main
import sys
from multiprocessing import Process
import time
from Cam.apps import run_server
from Cam.classify import render_gen


# def f():
#     sys.exit(main(sys.argv))


# def l():
#     run_server(render_gen)



# if __name__ == '__main__':
#     sys.exit(main(sys.argv))

#     # global p
#     # p = Process(target=f)
#     # p.start()

#     global r
#     r = Process(target=l)
#     r.start()
    

from flask import Flask, render_template, Response
from camera import Camera
import threading

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('layout.html')

def gen():
    sys.exit(main(sys.argv))



if __name__ == '__main__':
    threading.Thread(target=gen).start()
    app.run(host='0.0.0.0', debug=True)