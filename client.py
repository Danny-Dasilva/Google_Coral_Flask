import pygame as game
import pygame.camera
import sys
import time
from PIL import Image


port=9012 
address="192.168.100.2" #server's ip
size=width, height=  640, 480
scale=width, height= 40, 10
timer=0

game.init()
game.camera.init()
screen=game.display.set_mode(size)

camera=game.camera.Camera("/dev/video0", size )
camera.start()
time.sleep(1)
while True:
  if timer < 1:
    #connect to the server
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, port))

    #get image
    image=camera.get_image()

    #convert to pill image to scale
    string_image=game.image.tostring(image, "RGBA",False)
    pil_image=Image.fromstring("RGBA",size,string_image)
    pil_image =pil_image.resize(scale)
    buffer=pil_image.tostring()

    #print size of buffer
    print(sys.getsizeof(buffer))
    s.sendall(buffer)
    #time.sleep(0.01)