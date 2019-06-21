from threading import Thread, Event
from random import random
from time import sleep
class RandomThread():
    def __init__(self, socketio, ai, camera):
        self.delay = 0.01
        self.socketio = socketio
        thread1 = Thread(target=self.randomNumberGenerator)
        thread1.daemon = True
        thread1.start()
        self.thread_stop_event = Event()
        self.AI = ai
        self.Image = camera

    def randomNumberGenerator(self):

        print("Making random numbers")
        while not self.thread_stop_event.isSet():
            image = self.Image.PILImage()
            self.socketio.emit('newnumber', {'number': self.AI.run(image)}, namespace='/test')
            sleep(self.delay)