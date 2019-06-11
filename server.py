import sys
from PIL import Image
from teachable import main
from multiprocessing import Process
import socket

port=5000
address="192.168.100.2" #server's ip
size=width, height= 640, 480
scale=width, height=40, 10
timer = 0
previousImage = ""
image = ""
message=[]

#establish socket connection
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((address, port))
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


def a():
    connection, addr= s.accept()
    #Recieve data from the server:
    data=connection.recv(1024000)
    print(sys.getsizeof(data))
    #store the previous recieved image incase the client fails to recive all of the data for the new image
    previousImage=image
    try:

        #We turn the data we revieved into a 120x90 PIL image:
        #image = Image.fromstring("RGB",(120,90),data)

        #We resize the image to 640x480:
        pil_image = Image.fromstring("RGBA", size, data)
        pil_image= pil_image.resize(size)
        new_data=pil_image.tostring()
        image=game.image.fromstring(new_data, size, "RGBA")

    except:
        #If we failed to recieve a new image we display the last image we revieved:
        print("falied to recieve image")
        image = previousImage

if __name__ == '__main__':
    global p
    p = Process(target=a)
    p.start()
    sys.exit(main(sys.argv))