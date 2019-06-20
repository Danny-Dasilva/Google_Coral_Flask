from threading import Thread, Event
from random import random
from time import sleep
class RandomThread():
    def __init__(self, socketio):
        self.delay = 0.05
        self.socketio = socketio
        thread1 = Thread(target=self.randomNumberGenerator)
        thread1.daemon = True
        thread1.start()
        self.thread_stop_event = Event()

    def randomNumberGenerator(self):

        print("Making random numbers")
        while not self.thread_stop_event.isSet():
            number = round(random()*10, 3)
            print(number)
            self.socketio.emit('newnumber', {'number': number}, namespace='/test')
            sleep(self.delay)