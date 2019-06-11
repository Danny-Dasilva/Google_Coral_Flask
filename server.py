import sys
from PIL import Image
from teachable import main
from multiprocessing import Process
import socket

s = socket.socket()        
  
# Define the port on which you want to connect 
port = 14445                
  
# connect to the server on local computer 
s.connect(('127.0.0.1', port)) 

def a():
    print( s.recv(1024) )
    s.close()

if __name__ == '__main__':
    global p
    p = Process(target=a)
    p.start()
    sys.exit(main(sys.argv))




