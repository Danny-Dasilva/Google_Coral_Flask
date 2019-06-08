from teachable import main
import sys
from multiprocessing import Process
import time
from flask import Flask, render_template
from cam.apps import run_server, render_gen
app = Flask(__name__)

# def f():
#     sys.exit(main(sys.argv))


def l():
    run_server(render_gen)


# @app.route('/')
# def index():
#     return render_template('layout.html')



# def a():
#     app.run(host='0.0.0.0', debug=False)

if __name__ == '__main__':
    global p
    p = Process(target=l)
    p.start()
    sys.exit(main(sys.argv))

    # global r
    # r = Process(target=l)
    # r.start()
    





