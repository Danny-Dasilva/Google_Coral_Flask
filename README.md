## Google Coral Flask Server


# Instructions
clone repository

`git clone https://github.com/Danny-Dasilva/Google-Coral-Flask-Server.git`

Path to folder

`cd Google-Coral-Flask-Server`

install dependencies

`sh install.sh`

run server

`sudo python3 test.py`

# Troubleshooting and additional info 

in server.py

`Image = camera(Image_classify.AI())`

runs the image classify model, returns an overlay with a model trained on 100 labels

`Image = camera(face_detect.AI())`

runs the face detect model

`Image = camera(teach.AI())`

runs the teachable machine model


## Info for changing servos or motors

The adafruit servokit library has 2 methods for doing servos or motors

`kit.continuous_servo[1].throttle = 0.3`
 
 this will set a *motor* to move continuously in a direction
 
 `kit.servo[1].angle = 0`
 
 this will set a *servo* angle 
 
 the number in the brackets [ ] is the pin number on the hat
 
 ## Example of servo movement
 
```python
if(result == "One"):
            print("One")
            kit.servo[0].angle = 0
            sleep(0.4)
            #kit.continuous_servo[1].throttle = 0.3
            kit.servo[1].angle = 0
        elif(result == "Two"):
            print("Two")
            kit.servo[0].angle = 30
            sleep(0.4)
            kit.servo[1].angle = 0
        else:
            kit.servo[1].angle = 17
```

result is the value returned by teachable machine, if you want to add more values the other two are `'Three'` and `'Four'`

## Flask stuff

in order to access the server you need to go to the ip of the Coral and go to the port 5000

### on the Coral

`hostname -I`

### on browser on remote computer

`<IP_Addr>:5000`

### Additional

theres a while loop for the gstreamer thread so in order to stop the program you need to press
<kbd>CTRL</kbd>+<kbd>C</kbd> until it stops

or press <kbd>CTRL</kbd>+<kbd>\
