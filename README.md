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

### Empty Feed

`Image = camera(Empty.AI())`

returns a video feed with no model running

### Image Classification

`Image = camera(Classify.AI())`

runs the image classify model, returns an image classification model

![classify](https://media.giphy.com/media/XfyrthymaGNiBV1uBv/giphy.gif)

### Object Detection 

`Image = camera(Detect.AI())`

runs an object detection model detect model

![Detect](https://media.giphy.com/media/cmrryjBDbPpAcmcODv/giphy.gif)

### Teachable Machine

`Image = camera(Teachable.AI())`

runs the teachable machine model

![Teachable](https://media.giphy.com/media/H22nyRM1AibZJPPNor/giphy.gif)

<kbd>1</kbd>, <kbd>2</kbd>, <kbd>3</kbd>, <kbd>4</kbd> are the class categories

<kbd>q</kbd> reset current classes

### Pose-Net

`Image = camera(Pose.AI())`

runs the Pose-Net model 

![Pose](https://media.giphy.com/media/fA1OEwxQO0Y1kWF0NI/giphy.gif)

### Anonymizer

`Image = camera(anonymizer.AI())`

example of the pose net model, when you move out of the frame it saves the image backround

![Anonymizer](https://media.giphy.com/media/ZdlHCGdZ4R3GYFQiE5/giphy.gif)

### Music Synthesizer

`Image = camera(synthesizer.AI())`
 
 People are given control instrument and octave, the pitch is controlled with their right wrists and the volume with their left wrists.



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
