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
flaskImage = None
flaskStatus = None
def load_labels(path):
    p = re.compile(r'\s*(\d+)(.+)')
    with open(path, 'r', encoding='utf-8') as f:
       lines = (p.match(line).groups() for line in f.readlines())
       return {int(num): text.strip() for num, text in lines}

def shadow_text(dwg, x, y, text, font_size=20):
    dwg.add(dwg.text(text, insert=(x+1, y+1), fill='black', font_size=font_size))
    dwg.add(dwg.text(text, insert=(x, y), fill='white', font_size=font_size))

def generate_svg(dwg, objs, labels, text_lines):
    width, height = dwg.attribs['width'], dwg.attribs['height']
    for y, line in enumerate(text_lines):
        shadow_text(dwg, 10, y*20, line)
    for obj in objs:
        x0, y0, x1, y1 = obj.bounding_box.flatten().tolist()
        x, y, w, h = x0, y0, x1 - x0, y1 - y0
        x, y, w, h = int(x * width), int(y * height), int(w * width), int(h * height)
        percent = int(100 * obj.score)
        label = '%d%% %s' % (percent, labels[obj.label_id])
        shadow_text(dwg, x, y - 5, label)
        dwg.add(dwg.rect(insert=(x,y), size=(w, h),
                        fill='red', fill_opacity=0.3, stroke='white'))

class Model():
    def __init__(self):
        default_model_dir = './app/all_models'
        default_model = 'mobilenet_ssd_v2_face_quant_postprocess_edgetpu.tflite'
        default_labels = 'coco_labels.txt'
        parser = argparse.ArgumentParser()
        parser.add_argument('--model', help='.tflite model path',
                            default=os.path.join(default_model_dir,default_model))
        parser.add_argument('--labels', help='label file path',
                            default=os.path.join(default_model_dir, default_labels))
        parser.add_argument('--top_k', type=int, default=3,
                            help='number of classes with highest score to display')
        parser.add_argument('--threshold', type=float, default=0.1,
                            help='class score threshold')
        self.args = parser.parse_args()

        print("Loading %s with %s labels."%(self.args.model, self.args.labels))
        self.engine = DetectionEngine(self.args.model)
        self.labels = load_labels(self.args.labels)

        self.last_time = time.monotonic()
    def user_callback(self, image):

      #added
      global flaskImage
      global flaskStatus
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
      objBoxes = []
      for obj in objs:
          x0, y0, x1, y1 = obj.bounding_box.flatten().tolist()
          percent = int(100 * obj.score)
          #print(percent)
          objBoxes.append([percent, x0,y0,x1,y1])


      self.last_time = end_time


      flaskStatus = objBoxes
      return(flaskStatus)

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
