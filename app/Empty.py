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

"""A demo which runs object detection on camera frames.

export TEST_DATA=/usr/lib/python3/dist-packages/edgetpu/test_data

Run face detection model:
python3 -m edgetpuvision.detect \
  --model ${TEST_DATA}/mobilenet_ssd_v2_face_quant_postprocess_edgetpu.tflite

Run coco model:
python3 -m edgetpuvision.detect \
  --model ${TEST_DATA}/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite \
  --labels ${TEST_DATA}/coco_labels.txt
"""
import argparse
import time
import re
import svgwrite
import imp
import os
from edgetpu.detection.engine import DetectionEngine
from app import gstreamer

class Model():
    def __init__(self):
        self.last_time = time.monotonic()

    def user_callback(self, image):
      start_time = time.monotonic()
      end_time = time.monotonic()
      self.last_time = end_time

model = None
def main():
    global model
    model = Model()
class AI():
  def __init__(self):
    self.type = "None"
    main()
  def run(self, img):
    if (img != None):
      return(model.user_callback(img))
