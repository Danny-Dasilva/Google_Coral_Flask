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
from flask import Flask
from celery import Celery

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('layout.html')


@celery.task
def my_background_task():
    app.run(host='0.0.0.0', debug=False)

task = my_background_task.apply_async()
    



if __name__ == '__main__':
    sys.exit(main(sys.argv))

    