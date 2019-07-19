from adafruit_servokit import ServoKit
from time import sleep

kit = ServoKit(channels = 16)

kit.continuous_servo[4].throttle = .5

sleep(2)

#kit.continuous_servo[4].throttle = -.25

#sleep(2)

kit.continuous_servo[4].throttle = .05
