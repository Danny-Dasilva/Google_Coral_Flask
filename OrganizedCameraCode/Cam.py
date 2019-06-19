import gstreamer
from threading import Thread
from PIL import Image
class camera:
    def __init__(self):
        self.img = None
        self.width = None
        self.height = None
        thread1 = Thread(target=self.runThread)
        thread1.daemon = True
        thread1.start()
    def runThread(self):
        result = gstreamer.run_pipeline(self.updateIMG)
    def updateIMG(self, image, width, height):
        self.img = image
        self.width = width
        self.height = height
        #print(width)
        #print(height)
        #print(image)
    def imgBytes(self):
        return self.img
    def PILImage(self):
        return Image.frombytes('RGB', (self.width, self.height), self.img, 'raw')

