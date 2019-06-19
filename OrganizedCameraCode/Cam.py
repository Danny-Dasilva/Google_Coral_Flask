import gstreamer
from threading import Thread
from PIL import Image
import time
import flask
from io import BytesIO
class camera:
    def __init__(self):
        self.img = None
        self.width = None
        self.height = None
        thread1 = Thread(target=self.runThread)
        thread1.daemon = True
        thread1.start()

    def runThread(self):
        while True:
            result = gstreamer.run_pipeline(self.updateIMG)

    def updateIMG(self, image, width, height):
        self.img = image
        self.width = width
        self.height = height
        # time.sleep(0.01)
    def imgBytes(self):
        time.sleep(0.01)
        return self.img
    def PILImage(self):
        time.sleep(0.01)
        if(self.img != None):
            return Image.frombytes('RGB', (self.width, self.height), self.img, 'raw')
        return None
    def ImageStream(self):
        return self.convertIMG()

    def convertIMG(self):
        while True:
            time.sleep(0.001)
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

