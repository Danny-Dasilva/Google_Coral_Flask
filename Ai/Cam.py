import gstreamer
from threading import Thread, Event
from PIL import Image, ImageFont, ImageDraw
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
        self.fps = None
        self.numImages = None
        self.val = None
        thread1 = Thread(target=self.runThread)
        thread1.daemon = True
       
        thread1.start()
   
    
    def runThread(self):
        while True:
            self.result = gstreamer.run_pipeline(self.updateIMG)

    def updateIMG(self, image, width, height):

        self.img = image
        self.width = width
        self.height = height
        image = self.PILImage()
        self.result = self.AI.run(image)

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
            sleep(0.01)
            img_io = BytesIO()
            image = self.PILImage()
            if image != None:
                draw = ImageDraw.Draw(image)
                font = ImageFont.truetype("Gentona-Bold.ttf", 15)
                font2 = ImageFont.truetype("Gentona-Bold.ttf", 20)
                if(self.AI.type == "embedding"):
                    self.fps = self.result[0]
                    self.numImages = self.result[1]
                    self.val = self.result[2]
                    status = 'fps %.1f; #examples: %d; Class % 7s' % (self.fps, self.numImages,self.val)
                    draw.text((0,0), status, (255, 255, 255), font=font)
                elif(self.AI.type == "objClass"):
                    status = 'fps %.1f; #examples: %d;' % (self.fps, self.numImages)

                elif(self.AI.type == "face"):
                    status = self.result
                    if status != None:
                        for i in status:
                            draw.rectangle([i[1] * self.width, i[4] * self.height, (i[1] * self.width) + 25, (i[4] * self.height) + 20], fill="Red")
                            draw.text((i[1] * self.width, i[4] * self.height), str(i[0]), (255, 255, 255), font=font2)
                            draw.rectangle([i[1]*self.width,i[2]*self.height,i[3]*self.width,i[4]*self.height],outline="Red")
                else:
                    status = ""
                draw.rectangle([0,0,100,20], fill="Black")
                image.save(img_io, 'JPEG', quality=70)
                stream = img_io
                stream.seek(0)
                frame = stream.read()
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                yield None

