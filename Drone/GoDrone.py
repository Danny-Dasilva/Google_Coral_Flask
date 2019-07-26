import socket
import time
import serial
from threading import Thread
import math

class drone:

    def __init__(self):
        print("UDPServer Waiting for client on port 6666")
        self.channels = []
        self.timeSent = 0
        self.port = "/dev/ttymxc0"
        self.ultrasound_port = "/dev/ttymxc2"
        self.baudRate = 100000
        self.ultrasound_baudrate = 9600
        self.ser = serial.Serial(port=self.port, baudrate=self.baudRate, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_TWO)
        self.ultrasound_ser = serial.Serial(port=self.ultrasound_port, baudrate=self.ultrasound_baudrate)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(('', 6666))
        self.align = False
        self.count = 0
        self.newChannels = [1024] * 16
        self.height = 0

        self.throttle_min = 900
        self.throttle_max = 2000
        self.throttle_up = 1660
        self.throttle_down = 1620
        self.throttle_baseline = 1640
        self.current_throttle = self.throttle_min
        self.throttle_delta = 1
        self.is_hovering = False
        self.hover = 5
        self.throttle = 2
        self.target_height = 300
        self.throttle_p = .75
        self.throttle_i = 0
        self.throttle_d = 0
        self.total_error = 0
        self.min_error = 50

        self.takeoff = 6
        self.takeoff_count = 0
        self.takeoff_flag = False
        self.land = 7
        self.landing_count = 0
        self.landing_flag = False
        self.is_airborne = False

        self.gaz = 8

        self.throttle_override = 9

        t2 = Thread(target=self.updateHeight)
        t2.daemon = True
        t2.start()

        t1 = Thread(target=self.updateData)
        t1.daemon = True
        t1.start()


    def updateData(self):
        while True:
            # Update joystick data
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

                if(checksum1 == dataFromClient[36] and checksum2 == dataFromClient[37]):
                    self.channels = dataFromClient[4:36]
                    chan = []
                    for i in range(0,len(self.channels),2):
                        LSB = self.channels[i]
                        MSB = self.channels[i+1] << 8
                        num = int(LSB + MSB)
                        chan.append(num)

                    self.channels = chan
#                    print(self.channels)

                    # Hover command
                    if(self.channels[self.hover] > 1000 and not self.is_hovering):
                        self.is_hovering = True
                        self.target_height = self.height
                    elif(self.channels[self.hover] < 1000 and self.is_hovering):
                        self.is_hovering = False
                        self.total_error = 0

                    # Takeoff command
                    if(self.channels[self.takeoff] > 1000 and not self.is_airborne and not self.takeoff_flag):
#                        self.channels[self.throttle] = self.throttle_baseline
                        self.takeoff_flag = True

                    # Increment throttle until takeoff
                    if(self.takeoff_flag):
                        print("Taking off...")
                        if(self.current_throttle < self.throttle_up):
                            self.current_throttle += 15
                        else:
                            self.current_throttle = self.throttle_up
                            self.takeoff_count += 1

                            if(self.takeoff_count > 10):
                                print("Took off")
                                self.current_throttle = self.throttle_baseline
                                self.takeoff_flag = False
                                self.takeoff_count = 0
                                self.is_airborne = True

                    # Land command
                    if(self.channels[self.land] > 1000 and self.is_airborne):
                        self.current_throttle = self.throttle_down
                        self.is_airborne = False
                        self.landing_flag = True

                    if(self.landing_flag):
                        if(self.height < 350):
                            if(self.landing_count > 10):
                                self.current_throttle = self.throttle_min
                                self.landing_flag = False
                                self.landing_count = 0
                            self.landing_count += 1

#                    if(self.is_hovering):
#                        if(math.fabs(error) > self.min_error):
#                            self.current_throttle = self.throttle_baseline + self.throttle_p * error + self.total_error * self.throttle_i
#                            self.channels[self.throttle] = self.throttle_baseline

#                        self.channels[self.throttle] = self.clip(self.current_throttle, 900, 1100)
#                        print(self.current_throttle)
#                        self.channels[self.throttle] = 500

                    # Gaz logic
                    if(self.is_airborne):
                        self.target_height += 2 * (self.channels[self.gaz] - 500) / 500.0
                        self.target_height = self.clip(self.target_height, 300, 1000)

                    error = self.target_height - self.height

                    # Hovering logic
                    if(self.is_airborne):
                        if(error > self.min_error):
                            self.current_throttle += self.throttle_delta
                        elif(error < -self.min_error):
                            self.current_throttle -= self.throttle_delta
#                    else:
#                        self.current_throttle = self.channels[self.throttle]

                    # Clip the throttle
                    if(self.is_airborne):
                        self.current_throttle = self.clip(self.current_throttle, self.throttle_down, self.throttle_up)

                    # Throttle override
                    if(self.channels[self.throttle_override] > 1800):
                        self.current_throttle = self.throttle_up
                    elif(self.channels[self.throttle_override] < 1200):
                        self.current_throttle = self.throttle_down

                    self.channels[self.throttle] = self.current_throttle

                    print(self.channels[self.throttle], self.height, self.target_height)

                    for i in range(len(self.channels)):
                        self.update_channel(i, self.channels[i])
                    time.sleep(0.02)
                    #print(self.newChannels)

                    self.ser.write(self.create_SBUS(self.newChannels))
                    self.newChannels = [1024] * 16

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
        print("Done")

    def updateHeight(self):
        while True:
           try:
                current_reading = self.ultrasound_ser.read(6)
                current_reading = current_reading[1:5]
                self.height = int(current_reading)
                #print(self.height)
           except:
                pass


    def bit_not(self, n, numbits=8):
        return (1 << numbits) - 1 - n


    def create_SBUS(self, chan):
        data = bytearray(25)

        data[0] = 0x0f  # start byte

        current_byte = 1
        available_bits = 8

        for ch in chan:
            ch &= 0x7ff
            remaining_bits = 11
            while remaining_bits:
                mask = self.bit_not(0xffff >> available_bits << available_bits, 16)
                enc = (ch & mask) << (8 - available_bits)
                data[current_byte] |= enc

                encoded_bits = 0
                if remaining_bits < available_bits:
                    encoded_bits = remaining_bits
                else:
                    encoded_bits = available_bits

                remaining_bits -= encoded_bits
                available_bits -= encoded_bits
                ch >>= encoded_bits

                if available_bits == 0:
                    current_byte += 1
                    available_bits = 8

        data[23] = 0
        data[24] = 0
        return data

    def set_channel(self, chan, data):
        self.newChannels[chan] = data & 0x07ff

    def update_channel(self, chan, value):
        self.set_channel(chan, self.mapData(value))

    def mapData(self, n):
        return int((819 * ((n - 1500) / 500)) + 992)

    def sendSBUSData(self, chan):
        if (time.time() - self.timeSent < 1):
            time.sleep(0.05)
            self.ser.write(self.create_SBUS(self.newChannels))
            self.newChannels = [1024] * 16

        else:
            None

    def clip(self, num, min, max):
        if(num < min):
            return min
        if(num > max):
            return max
        return num
