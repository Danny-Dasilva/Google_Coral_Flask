from teachable import main
import sys
from multiprocessing import Process
import time
import socket
from flask import Flask, render_template
from cam.apps import run_server, render_gen

# app = Flask(__name__)

# def f():
#     sys.exit(main(sys.argv))


# def l():
#     run_server(render_gen)


# @app.route('/')
# def index():
#     return render_template('layout.html')


# def a():
#     app.run(host='0.0.0.0', debug=False)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 1234))

def a():
    msg = s.recv(8)
    print(msg.decode("utf-8"))
    


if __name__ == '__main__':
    global p
    p = Process(target=a)
    p.start()
    sys.exit(main(sys.argv))

    # global r
    # r = Process(target=l)
    # r.start()
    




