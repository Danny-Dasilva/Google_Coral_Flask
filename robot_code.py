from adafruit_servokit import ServoKit
from time import sleep

kit = ServoKit(channels =16)


while True:

    sleep(2)
    #kit.continuous_servo[0].throttle = 0.05
    kit.servo[0].angle = 0
    print("Stoped")
    sleep(2)
    kit.servo[0].angle = 90
    print("Forward")
    sleep(2)
    kit.servo[0].angle = 0
    print("Back")
