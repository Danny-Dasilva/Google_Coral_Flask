# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
from functools import partial
import re
import time

import numpy as np
from PIL import Image
import svgwrite
from app import gstreamer
from app.pose_engine import PoseEngine






class Model():
    def __init__(self):
        self.last_time = time.monotonic()
        self.n = 0
        self.sum_fps = 0
        self.sum_process_time = 0
        self.sum_inference_time = 0
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--mirror', help='flip video horizontally', action='store_true')
        parser.add_argument('--model', help='.tflite model path.', required=False)
        parser.add_argument('--res', help='Resolution', default='640x480',
                            choices=['480x360', '640x480', '1280x720'])
        parser.add_argument('--videosrc', help='Which video source to use', default='/dev/video0')
        parser.add_argument('--h264', help='Use video/x-h264 input', action='store_true')
        self.args = parser.parse_args()

        default_model = './app/all_models/posenet_mobilenet_v1_075_%d_%d_quant_decoder_edgetpu.tflite'
        if self.args.res == '480x360':
            self.src_size = (640, 480)
            self.appsink_size = (480, 360)
            model = args.model or default_model % (353, 481)
        elif self.args.res == '640x480':
            self.src_size = (640, 480)
            self.appsink_size = (640, 480)
            model = self.args.model or default_model % (481, 641)
        elif self.args.res == '1280x720':
            self.src_size = (1280, 720)
            self.appsink_size = (1280, 720)
            model = args.model or default_model % (721, 1281)

        self.engine = PoseEngine(model, mirror=self.args.mirror)
        self.use_appsrc = True
        self.background_image = None
        self.timer_time = time.monotonic()



    def render_overlay(self, image):
        global flaskStatus
        #nonlocal timer_time, background_image
        outputs, inference_time = self.engine.DetectPosesInImage(image)
        now_time = time.monotonic()
        BACKGROUND_DELAY = 2

        action = "none"
        if self.background_image is None:
            if outputs:  # frame still has people in it, restart timer
                action = 'Waiting for everyone to leave the frame...'
                print('Waiting for everyone to leave the frame...')
                self.timer_time = now_time
            elif now_time > self.timer_time + BACKGROUND_DELAY:  # frame has been empty long enough
                self.background_image = image
                action = 'Background set.'
                print('Background set.')

        # else:
        #     image = self.background_image

        flaskStatus = outputs
        #print(flaskStatus)
        return flaskStatus, self.background_image, action







model = None
def main():
    global model
    model = Model()
class AI():
  def __init__(self):
    self.type = "Anonymizer"
    main()
  def run(self, img):
    if (img != None):
        #s2 = partial(model.render_overlay(img), model.engine)
        #s3 = s2, model.src_size, model.appsink_size, mirror = model.args.mirror, videosrc = model.args.videosrc, h264input = model.args.h264
        mirror = model.args.mirror
        videosrc = model.args.videosrc
        h264input = model.args.h264
        return(model.render_overlay(img), model.engine, model.src_size, model.appsink_size, mirror, videosrc, h264input)

