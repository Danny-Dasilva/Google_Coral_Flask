import gstreamer
from threading import Thread
from PIL import Image
class cameraStream(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.img = None
        self.width = None
        self.height = None

    def run(self):
        result = gstreamer.run_pipeline(self.updateIMG)

    def updateIMG(self, image, width, height):
        self.img = image
        self.width = width
        self.height = height

class camera():
    import cameraStream
    def __init__(self):
        self.stream = cameraStream(4)
        self.stream.start()
    def imgBytes(self):
        return self.stream.img
    def PILImage(self):
        return Image.frombytes('RGB', (self.stream.width, self.stream.height), self.stream.img, 'raw')

