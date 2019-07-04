from adafruit_servokit import ServoKit
from time import sleep


kit = ServoKit(channels =16)

while True:
    kit.servo[0].angle = 15
    print("zero")
    sleep(3)
#kit.servo[0].angle = 30
#sleep(3)
#kit.servo[0].angle = 0
#sleep(3)
    kit.servo[1].angle = 0
    sleep(3)
    kit.servo[1].angle = 45
    sleep(3)
