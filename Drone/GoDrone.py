import socket
import time
import serial
from threading import Thread
class drone:

    def __init__(self):
        print("UDPServer Waiting for client on port 6666")
        self.channels = []
        self.timeSent = 0
        self.port = "/dev/ttymxc0"
        self.baudRate = 100000
        self.ser = serial.Serial(port=self.port, baudrate=self.baudRate, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_TWO)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(('', 6666))
        self.align = False
        self.count = 0
        t1 = Thread(target=self.updateData)
        t1.daemon = True
        t1.start()

    def updateData(self):
        while True:
            dataFromClient, address = self.server_socket.recvfrom(256)
            global timeSent
            self.timeSent = time.time()
            cmd = ""
            for i in range(0,4):
                cmd += chr(dataFromClient[i])
            if(cmd == "SBUS"):
                checksum1 = 0
                for byte in dataFromClient:
                    checksum1 = checksum1 ^ byte
                checksum1 = checksum1 & 0xFE
                checksum2 = (~checksum1) & 0xFE
                if(checksum1 == dataFromClient[30] and checksum2 == dataFromClient[29]):
                    self.channels = dataFromClient[4:29]
                    #print(self.channels)
            elif(cmd == "BEAT"):
                print("BEAT")
            elif(cmd == "HAND"):
                self.server_socket.sendto(b"HAND",(address[0],address[1]))
            elif (cmd == "FACE"):
                if(self.count == 0):
                    self.align = True
                    self.server_socket.sendto(b"FACE", (address[0], address[1]))
                    self.count = 1
                elif(self.count == 1):
                    self.align = False
                    self.server_socket.sendto(b"FACE", (address[0], address[1]))
                    self.count = 0
    def sendSBUSData(self, chan):
        if (time.time() - self.timeSent < 1):
            time.sleep(0.05)
            self.ser.write(chan)
        else:
            None
            
    def sendFaceData(self, pos):
        print(pos)
        #self.server_socket.sendto(bytearray[pos], (address[0], address[1]))


