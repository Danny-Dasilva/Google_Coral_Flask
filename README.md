## Google Coral Flask Server

Expose deep learning models and receive data on the Coral usb accelerator and Edge TPU via a Flask app


# Instructions
clone repository

`git clone https://github.com/Danny-Dasilva/Google-Coral-Flask-Server.git`

Path to folder

`cd Google-Coral-Flask-Server`

install dependencies

`sh install.sh`

run server

`sudo python3 test.py`

# Running Models

in test.py

## Empty Feed

`Image = camera(Empty.AI())`

returns a video feed with no model running

## Image Classification

`Image = camera(Classify.AI())`

runs the image classify model, returns an image classification model

![classify](https://media.giphy.com/media/XfyrthymaGNiBV1uBv/giphy.gif)

## Object Detection 

`Image = camera(Detect.AI())`

runs an object detection model detect model

![Detect](https://media.giphy.com/media/cmrryjBDbPpAcmcODv/giphy.gif)

## Teachable Machine

`Image = camera(Teachable.AI())`

runs the teachable machine model

![Teachable](https://media.giphy.com/media/H22nyRM1AibZJPPNor/giphy.gif)

<kbd>1</kbd>, <kbd>2</kbd>, <kbd>3</kbd>, <kbd>4</kbd> add an image to each corresponding class

<kbd>q</kbd> reset current classes

## Pose-Net

`Image = camera(Pose.AI())`


![Pose](https://media.giphy.com/media/fA1OEwxQO0Y1kWF0NI/giphy.gif)

## Anonymizer

`Image = camera(anonymizer.AI())`

example of the pose net model, when you move out of the frame it saves the image backround

![Anonymizer](https://media.giphy.com/media/ZdlHCGdZ4R3GYFQiE5/giphy.gif)

## Music Synthesizer

`Image = camera(synthesizer.AI())`
 
 Three people are given control instrument and octave, the pitch is controlled with their right wrists and the volume with their left wrists.


## Return values

in test.py

```python
def my_function():
    while True:
        sleep(0.01)
        count = Image.numImages
        fps = Image.fps
        Inference = Image.inference
        Class = Image.Class
        Score = Image.Score

        print(fps, Inference, Class, Score, count)
```
For every model your run there are corresponding instance attributes that you can call from the camera class

`fps` returns the frames per second for the camera

`inference` returns the interference rate

`numImages` returns the number of examples for the teacheable machine

`Class` returns the class of the model

`Score` returns the percentage accuracy the model believes the class to be 

### e.g 
`teacheable` returns 'One', 'Two', 'Three', or 'Four'

`classify` returns 'ping-pong ball' or 'spatula'

`detect` returns bounding box 

You can modify `my_function` and add your own python operations

## Args

All normal arguments that each model takes can be applied as long as the right class is being used

eg. 'python 3 test.py --model /<path to my example model>'



## Flask stuff

in order to access the server you need to go to the ip of the Coral and go to the port 5000

### on the Coral

`hostname -I`

### on browser on remote computer

`<IP_Addr>:5000`

### Additional

If you receive a `segmentation fault` error simply rerun the code


If you encounter a gstreamer error 'must write bytes' then simply restart the program

If this problem persists power off plug in the camera again and change the usb C power cable


