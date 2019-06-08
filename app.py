from teachable import main
import sys
from multiprocessing import Process
import time


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
import threading

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('layout.html')

def f():
    app.run(host='0.0.0.0', debug=False)



if __name__ == '__main__':
    sys.exit(main(sys.argv))
    global p
    p = Process(target=f)
    p.start()

    