import sys
from PIL import Image
from teachable import main
from multiprocessing import Process
import socket
from time import sleep

from flask import Flask, render_template

app = Flask(__name__)

s = socket.socket()        
  
# Define the port on which you want to connect 
port = 14445                
  

@app.route('/test')
def test():
    s.connect(('127.0.0.1', port)) 
    print( s.recv(1024) )
    return s.recv(1024)
    
def a():
    app.run(host='0.0.0.0', debug=False)


# def a():
#     print( s.recv(1024) )
#     s.close()

if __name__ == '__main__':
    global p
    p = Process(target=a)
    p.start()
    sys.exit(main(sys.argv))




