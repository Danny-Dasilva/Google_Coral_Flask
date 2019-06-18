import teach
import sys
from multiprocessing import Process
import time
import socket
from time import sleep
from flask import Flask, render_template
from threading import Thread
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

# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect((socket.gethostname(), 1235))

# def a():

#     msg = s.recv(1024)
#     print(msg.decode("utf-8"))
    
    
if __name__ == '__main__':
    print("Thread Starting")
    #t1 = Thread(target = teach.main, args=sys.argv)
    t1 = Thread(target = teach.testThread)
    t1.start
    print("Thread started")
'''
if __name__ == '__main__':
    # global p
     p = Process(target=teach.main)
     p.start()
    sys.exit(teach.main(sys.argv))
'''
    
####code 



