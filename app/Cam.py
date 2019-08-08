import sys
from app import gstreamer
from threading import Thread, Event
from PIL import Image, ImageFont, ImageDraw
from time import sleep
import flask
from io import BytesIO
import sys

EDGES = (
    ('nose', 'left eye'),
    ('nose', 'right eye'),
    ('nose', 'left ear'),
    ('nose', 'right ear'),
    ('left ear', 'left eye'),
    ('right ear', 'right eye'),
    ('left eye', 'right eye'),
    ('left shoulder', 'right shoulder'),
    ('left shoulder', 'left elbow'),
    ('left shoulder', 'left hip'),
    ('right shoulder', 'right elbow'),
    ('right shoulder', 'right hip'),
    ('left elbow', 'left wrist'),
    ('right elbow', 'right wrist'),
    ('left hip', 'right hip'),
    ('left hip', 'left knee'),
    ('right hip', 'right knee'),
    ('left knee', 'left ankle'),
    ('right knee', 'right ankle'),
)

class camera:

    def __init__(self, ai):
        self.img = None
        self.width = None
        self.height = None
        self.shape = None
        self.AI = ai
        self.bac_img = None
        self.result = None
        self.fps = None
        self.numImages = None
        self.val = None
        thread1 = Thread(target=self.runThread)
        thread1.deamon = True
        thread1.start()


    def runThread(self):
        while True:

            pipeline = gstreamer.run_pipeline(self.updateIMG)
            self.result = sys.exit(pipeline)

    def updateIMG(self, image, width, height):

        self.img = image
        self.width = width
        self.height = height
        if self.AI.type == 'None':
            self.AI.type = 'None'
            pass
        if self.AI.type == 'Anonymizer' or 'Pose':
            image = self.NPImage()
            self.result = self.AI.run(image)


        else:
            image = self.PILImage()
            self.result = self.AI.run(image)


    def imgBytes(self):
        sleep(0.01)
        return self.img
    def NPImage(self):

        sleep(0.01)
        if(self.img != None):
            return(self.img)
        return None

    def PILImage(self):

        sleep(0.01)
        if(self.img != None):
            return Image.frombytes('RGB', (self.width, self.height), self.img, 'raw')
        return None
    def backround(self):

        sleep(0.01)
        if(self.bac_img != None):
            return Image.frombytes('RGB', (self.width, self.height), self.bac_img, 'raw')
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
                font = ImageFont.truetype("./app/fonts/Gentona-Bold.ttf", 15)
                font2 = ImageFont.truetype("./app/fonts/Gentona-Bold.ttf", 20)

                def draw_pose(pose, color='yellow', threshold=0.2):
                    xys = {}
                    for label, keypoint in pose.keypoints.items():
                        if keypoint.score < threshold: continue
                        xys[label] = (int(keypoint.yx[1]), int(keypoint.yx[0]))
                        r = 2
                        x = int(keypoint.yx[1])
                        y = int(keypoint.yx[0])
                        draw.ellipse((x - r, y - r, x + r, y + r), fill=(255, 0, 0, 0))

                    for a, b in EDGES:
                        if a not in xys or b not in xys: continue
                        ax, ay = xys[a]
                        bx, by = xys[b]
                        draw.line((ax, ay, bx, by), fill=(0, 0, 255), width=1)


                if(self.AI.type == "embedding"):
                    draw.rectangle([0,0,200,20], fill="Black")
                    self.fps = self.result[0]
                    self.numImages = self.result[1]
                    self.val = self.result[2]
                    status = 'fps %.1f; #ex: %d; Class%7s' % (self.fps, self.numImages,self.val)
                    draw.text((0,0), status, (255, 255, 255), font=font)
                elif(self.AI.type == "objClass"):
                    draw.rectangle([0,0,320,20], fill="Black")
                    self.fps = self.result[0]
                    self.numImages = self.result[1]
                    status = 'fps %.1f; % 7s' % (self.fps, self.numImages)
                    draw.text((0,0), status, (255, 255, 255), font=font)

                elif(self.AI.type == "face"):
                    status = self.result
                    if len(status) > 0:
                        self.val = status
                        for i in status:
                            draw.rectangle([i[1] * self.width, i[4] * self.height, (i[1] * self.width) + 25, (i[4] * self.height) + 20], fill="Red")
                            draw.text((i[1] * self.width, i[4] * self.height), str(i[0]), (255, 255, 255), font=font2)
                            draw.rectangle([i[1]*self.width,i[2]*self.height,i[3]*self.width,i[4]*self.height],outline="Red")


                elif (self.AI.type == "Pose"):
                    outputs = self.result[0]
                    for pose in outputs:
                        draw_pose(pose)

                elif (self.AI.type == "Anonymizer"):
                    back_image = self.result[0][1]
                    self.bac_img = self.result[0][1]
                    #print(back_image)

                    outputs = self.result[0][0]
                    if back_image != None:
                        image.paste(self.backround())

                    for pose in outputs:
                        draw_pose(pose)

                    # for pose in outputs:
                    #     draw_pose(pose)


                    # outputs = self.result[0]
                    #
                    # def draw_pose(pose, color='yellow', threshold=0.2):
                    #     xys = {}
                    #     for label, keypoint in pose.keypoints.items():
                    #         if keypoint.score < threshold: continue
                    #         xys[label] = (int(keypoint.yx[1]), int(keypoint.yx[0]))
                    #         r = 2
                    #         x = int(keypoint.yx[1])
                    #         y = int(keypoint.yx[0])
                    #         draw.ellipse((x - r, y - r, x + r, y + r), fill=(255, 0, 0, 0))
                    #
                    #     for a, b in EDGES:
                    #         if a not in xys or b not in xys: continue
                    #         ax, ay = xys[a]
                    #         bx, by = xys[b]
                    #         draw.line((ax, ay, bx, by), fill=(0, 0, 255), width=1)
                    #
                    # for pose in outputs:
                    #     draw_pose(pose)





                else:
                    self.result = [0, 0]
                    self.val = ('no model')
                    status = ""

                image.save(img_io, 'JPEG', quality=70)
                stream = img_io
                stream.seek(0)
                frame = stream.read()
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                yield None

