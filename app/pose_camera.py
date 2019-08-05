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

EDGES = (
    ('nose', 'left eye'),
    ('nose', 'right eye'),
    ('nose', 'left ear'),
    ('nose', 'right ear'),
    ('left ear', 'left eye'),
    ('right ear', 'right eye'),
    ('left eye', 'right eye'),
    ('left shoulder', 'right shoulder'),
    ('left shoulder', 'left elbow'),
    ('left shoulder', 'left hip'),
    ('right shoulder', 'right elbow'),
    ('right shoulder', 'right hip'),
    ('left elbow', 'left wrist'),
    ('right elbow', 'right wrist'),
    ('left hip', 'right hip'),
    ('left hip', 'left knee'),
    ('right hip', 'right knee'),
    ('left knee', 'left ankle'),
    ('right knee', 'right ankle'),
)


def shadow_text(dwg, x, y, text, font_size=16):
    dwg.add(dwg.text(text, insert=(x + 1, y + 1), fill='black',
                     font_size=font_size, style='font-family:sans-serif'))
    dwg.add(dwg.text(text, insert=(x, y), fill='white',
                     font_size=font_size, style='font-family:sans-serif'))


def draw_pose(dwg, pose, color='yellow', threshold=0.2):
    xys = {}
    for label, keypoint in pose.keypoints.items():
        if keypoint.score < threshold: continue
        xys[label] = (int(keypoint.yx[1]), int(keypoint.yx[0]))
        dwg.add(dwg.circle(center=(int(keypoint.yx[1]), int(keypoint.yx[0])), r=5,
                           fill='cyan', fill_opacity=keypoint.score, stroke=color))

    for a, b in EDGES:
        if a not in xys or b not in xys: continue
        ax, ay = xys[a]
        bx, by = xys[b]
        dwg.add(dwg.line(start=(ax, ay), end=(bx, by), stroke=color, stroke_width=2))





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
        self.use_appsrc = False

    def render_overlay(self, image):
        global flaskStatus
        #nonlocal n, sum_fps, sum_process_time, sum_inference_time, last_time
        self.start_time = time.monotonic()
        outputs, self.inference_time = self.engine.DetectPosesInImage(image)
        self.end_time = time.monotonic()
        self.n += 1
        self.sum_fps += 1.0 / (self.end_time - self.last_time)
        self.sum_process_time += 1000 * (self.end_time - self.start_time) - self.inference_time
        self.sum_inference_time += self.inference_time
        self.last_time = self.end_time
        text_line = 'PoseNet: %.1fms Frame IO: %.2fms TrueFPS: %.2f Nposes %d' % (
            self.sum_inference_time / self.n, self.sum_process_time / self.n, self.sum_fps / self.n, len(outputs)
        )
        flaskStatus = outputs
        #print(flaskStatus)
        # print(flaskStatus)
        return(flaskStatus)






model = None
def main():
    global model
    model = Model()
class AI():
  def __init__(self):
    self.type = "Pose"
    main()
  def run(self, img):
    if (img != None):
        #s2 = partial(model.render_overlay(img), model.engine)
        #s3 = s2, model.src_size, model.appsink_size, mirror = model.args.mirror, videosrc = model.args.videosrc, h264input = model.args.h264
        mirror = model.args.mirror
        videosrc = model.args.videosrc
        h264input = model.args.h264
        return(model.render_overlay(img), model.engine, model.src_size, model.appsink_size, mirror, videosrc, h264input)

