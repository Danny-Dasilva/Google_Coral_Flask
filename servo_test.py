from adafruit_servokit import ServoKit
import time

kit = ServoKit(channels=16)

kit.servo[0].angle = 30

#time.sleep(2)

#kit.servo[0].angle = 15
