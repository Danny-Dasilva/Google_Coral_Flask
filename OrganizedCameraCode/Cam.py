import gstreamer
from threading import Thread, Event
from PIL import Image
from time import sleep
import flask
from io import BytesIO
class camera:

    def __init__(self, ai):
        self.img = None
        self.width = None
        self.height = None
        self.AI = ai
        self.result = None
        thread1 = Thread(target=self.runThread)
        thread1.daemon = True
       
        thread1.start()
   
    
    def runThread(self):
        self.result = sys.exit(gstreamer.run_pipeline(self.updateIMG))

    def updateIMG(self, image, width, height):

        self.img = image
        self.width = width
        self.height = height
        image = self.PILImage()
        self.result = self.AI.run(image)
        # time.sleep(0.01)
    def imgBytes(self):
        sleep(0.001)
        return self.img
    def PILImage(self):

        sleep(0.001)
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

