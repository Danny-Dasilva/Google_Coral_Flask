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

"""A demo which runs object classification on camera frames."""
import argparse
import time
import re
import svgwrite
import imp
import os
from edgetpu.classification.engine import ClassificationEngine
from app import gstreamer
flaskImage = None
flaskStatus = None
def load_labels(path):
    p = re.compile(r'\s*(\d+)(.+)')
    with open(path, 'r', encoding='utf-8') as f:
       lines = (p.match(line).groups() for line in f.readlines())
       return {int(num): text.strip() for num, text in lines}

def generate_svg(dwg, text_lines):
    for y, line in enumerate(text_lines):
      dwg.add(dwg.text(line, insert=(11, y*20+1), fill='black', font_size='20'))
      dwg.add(dwg.text(line, insert=(10, y*20), fill='white', font_size='20'))

class Model():
    def __init__(self):
        default_model_dir = "./app/all_models"
        default_model = 'mobilenet_v2_1.0_224_quant_edgetpu.tflite'
        #default_model = 'model_edgetpu.tflite'
        default_labels = 'imagenet_labels.txt'
        parser = argparse.ArgumentParser()
        parser.add_argument('--model', help='.tflite model path',
                            default=default_model)
        parser.add_argument('--labels', help='label file path',
                            default=default_labels)
        parser.add_argument('--top_k', type=int, default=1,
                            help='number of classes with highest score to display')
        parser.add_argument('--threshold', type=float, default=0.1,
                            help='class score threshold')
        self.args = parser.parse_args()

        print("Loading %s with %s labels."%(os.path.join(default_model_dir, self.args.model), os.path.join(default_model_dir, self.args.labels)))
        self.engine = ClassificationEngine(os.path.join(default_model_dir, self.args.model))
        self.labels = load_labels(os.path.join(default_model_dir, self.args.labels))


        self.last_time = time.monotonic()

    def user_callback(self,image):


      global flaskImage
      global flaskStatus
      flaskImage = image
      
      
      start_time = time.monotonic()
      results = self.engine.ClassifyWithImage(image, threshold=self.args.threshold, top_k=self.args.top_k)
      end_time = time.monotonic()
      text_lines = [
          'Inference: %.2f ms' %((end_time - start_time) * 1000),
          (1.0/(end_time - self.last_time)),
      ]
      for index, score in results:
        #text_lines.append('score=%.2f: %s' % (score, self.labels[index]))
        labels = [score, self.labels[index]]
        text_lines.extend(labels)
        
      # if(len(text_lines) > 2):
      #   status = [text_lines[1], text_lines[2], ""]
      # else:
      #     status = [text_lines[1], "", ""]
      self.last_time = end_time
 
      flaskData = text_lines
      return(flaskData)

model = None
def main():
    global model
    model = Model()
class AI():
  def __init__(self):
    self.type = "objClass"
    main()
  def run(self, img):
    if (img != None):
      return(model.user_callback(img))


