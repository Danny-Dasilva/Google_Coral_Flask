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
  --model mobilenet_ssd_v2_face_quant_postprocess_edgetpu.tflite

Run coco model:
python3 -m edgetpuvision.detect \
  --model mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite \
  --labels coco_labels.txt
"""
import argparse
import time
import re
import svgwrite
import imp
import os
from edgetpu.detection.engine import DetectionEngine
from app import gstreamer
from random import randrange
flaskImage = None
flaskStatus = None

def load_labels(path):
    p = re.compile(r'\s*(\d+)(.+)')
    with open(path, 'r', encoding='utf-8') as f:
       lines = (p.match(line).groups() for line in f.readlines())
       return {int(num): text.strip() for num, text in lines}

def rand_color():
        color = (randrange(255), randrange(255), randrange(255), 0)
        return color

def Gen_Color(path):
    p = re.compile(r'\s*(\d+)(.+)')
    with open(path, 'r', encoding='utf-8') as f:
       lines = (p.match(line).groups() for line in f.readlines())
       color = {int(num) : rand_color() for num, text in lines}
       return color

class Model():
    def __init__(self):
        default_model_dir = './app/all_models'
        #default_model = 'mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite'
        default_model = 'mobilenet_ssd_v2_face_quant_postprocess_edgetpu.tflite'
        default_labels = 'coco_labels.txt'
        parser = argparse.ArgumentParser()
        parser.add_argument('--model', help='.tflite model path',
                            default=default_model)
        parser.add_argument('--labels', help='label file path',
                            default=default_labels)
        parser.add_argument('--top_k', type=int, default=3,
                            help='number of classes with highest score to display')
        parser.add_argument('--cutoff', type=int, default=50,
                            help='Cutoff for showing objects')

        parser.add_argument('--threshold', type=float, default=0.1,
                            help='class score threshold')
        self.args = parser.parse_args()

        print("Loading %s with %s labels."%(os.path.join(default_model_dir,self.args.model), os.path.join(default_model_dir,self.args.labels)))
        self.engine = DetectionEngine(os.path.join(default_model_dir,self.args.model))
        self.labels = load_labels(os.path.join(default_model_dir,self.args.labels))
        self.color = Gen_Color(os.path.join(default_model_dir,self.args.labels))


        self.last_time = time.monotonic()
    def user_callback(self, image):

      global flaskImage
      global flaskStatus
      global flaskLabel
      global FlaskPercent
      flaskImage = image
      start_time = time.monotonic()
      objs = self.engine.DetectWithImage(image, threshold=self.args.threshold,
                                    keep_aspect_ratio=True, relative_coord=True,
                                    top_k=self.args.top_k)
      end_time = time.monotonic()
      text_lines = [
          'Inference: %.2f ms' %((end_time - start_time) * 1000),
          'FPS: %.2f fps' %(1.0/(end_time - self.last_time)),
      ]
      FlaskInf = ((end_time - start_time) * 1000)
      fps = (1.0/(end_time - self.last_time))
      objBoxes = []
      flaskClass = []
      FlaskPercent = []
      for obj in objs:
          x0, y0, x1, y1 = obj.bounding_box.flatten().tolist()
          percent = int(100 * obj.score)
          label = self.labels[obj.label_id]
          flaskClass.append(label)
          FlaskPercent.append(percent)

          color = self.color[obj.label_id]

          if percent > self.args.cutoff:
            if obj.label_id > 0:
              objBoxes.append([color, label, x0,y0,x1,y1])
            else:
              objBoxes.append([percent, x0,y0,x1,y1])

      self.last_time = end_time

      flaskStatus = objBoxes
     
      return(flaskStatus, FlaskInf, fps, flaskClass, FlaskPercent)

model = None
def main():
    global model
    model = Model()
class AI():
  def __init__(self):
    self.type = "face"
    main()
  def run(self, img):
    if (img != None):
      return(model.user_callback(img))
