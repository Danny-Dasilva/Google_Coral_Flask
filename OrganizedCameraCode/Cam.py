import gstreamer
from threading import Thread, Event
from PIL import Image
from time import sleep
import flask
from io import BytesIO
class camera:

    def __init__(self, ai, socketio):
        self.img = None
        self.width = None
        self.height = None
        self.AI = ai
        self.socketio = socketio
        self.result = None
        thread1 = Thread(target=self.runThread)
        thread1.daemon = True
        thread2 = Thread(target=self.updateString)
        thread2.daemon = True
        thread2.start()
        thread1.start()
    def updateString(self):

        while True:
            #print("Thread2")
            image = self.PILImage()
            self.result = self.AI.run(image)
            self.socketio.emit('newnumber', {'number': self.result}, namespace='/test')
            sleep(0.01)
    def getAIResult(self):
        return self.result
    def runThread(self):
        while True:
            self.result = gstreamer.run_pipeline(self.updateIMG)

    def updateIMG(self, image, width, height):

        self.img = image
        self.width = width
        self.height = height
        # time.sleep(0.01)
    def imgBytes(self):
        sleep(0.01)
        return self.img
    def PILImage(self):

        sleep(0.01)
        if(self.img != None):
            return Image.frombytes('RGB', (self.width, self.height), self.img, 'raw')
        return None
    def ImageStream(self):
        return self.convertIMG()

    def convertIMG(self):
        while True:
            sleep(0.001)
            img_io = BytesIO()
            image = self.PILImage()
            if image != None:
                image.save(img_io, 'JPEG', quality=70)
                stream = img_io
                stream.seek(0)
                frame = stream.read()
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                yield None

