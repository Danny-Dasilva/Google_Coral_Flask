
import serial
import time
port = "/dev/ttymxc2"
baudRate = 9600
ser = serial.Serial(port=port, baudrate=baudRate)
while True:
    print(ser.read(6))
    time.sleep(0.1)

"""
import time
from periphery import GPIO

trig = GPIO(138, "out")
echo = GPIO(140, "in")

trig.write(False)
print("Waiting for sensor to settle")
time.sleep(1)

while True:
    trig.write(True)
    time.sleep(0.00001)
    trig.write(False)

    while(echo.read() == 0):
        pulse_start = time.time()

    while(echo.read() == 1):
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start

    distance = pulse_duration * 17150
    distance = round(distance, 2)

    print("Distance (cm)", distance)
    time.sleep(.1)

trig.close()
echo.close()
"""