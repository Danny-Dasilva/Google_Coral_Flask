#!/usr/bin/env python
#
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

import gstreamer


from PIL import Image
from embedding import kNNEmbeddingEngine
import argparse
import sys
import os
import time
import threading
from collections import deque, Counter
from functools import partial
from multiprocessing import Process
import multiprocessing as mp
import os
import socket

os.environ['XDG_RUNTIME_DIR'] = '/run/user/1000'


flaskImage = None
flaskStatus = None

def detectPlatform():
  try:
    model_info = open("/sys/firmware/devicetree/base/model").read()
    if 'MX8MQ' in model_info:
      print("Detected EdgeTPU dev board.")
      return "devboard"
    return "Unknown"
  except:
    print("Could not detect environment. Assuming generic Linux.")
    return "unknown"


class UI(object):
  """Abstract UI class. Subclassed by specific board implementations."""

  def __init__(self):
   
    current_time = time.time()


class UI(object):
  """Abstract UI class. Subclassed by specific board implementations."""
  def __init__(self):
    self._button_state = [False for _ in self._buttons]
    current_time = time.time()
    self._button_state_last_change = [current_time for _ in self._buttons]
    self._debounce_interval = 0.1 # seconds

  def setOnlyLED(self, index):
    for i in range(len(self._LEDs)): self.setLED(i, False)
    if index is not None: self.setLED(index, True)

  def isButtonPressed(self, index):
    buttons = self.getButtonState()
    return buttons[index]

  def setLED(self, index, state):
    raise NotImplementedError()

  def getButtonState(self):
    raise NotImplementedError()

  def getDebouncedButtonState(self):
    t = time.time()
    for i,new in enumerate(self.getButtonState()):
      if not new:
        self._button_state[i] = False
        continue
      old = self._button_state[i]
      if ((t-self._button_state_last_change[i]) >
             self._debounce_interval) and not old:
        self._button_state[i] = True
      else:
        self._button_state[i] = False
      self._button_state_last_change[i] = t
    return self._button_state

  def testButtons(self):
    while True:
      for i in range(5):
        self.setLED(i, self.isButtonPressed(i))
      print('Buttons: ', ' '.join([str(i) for i,v in
          enumerate(self.getButtonState()) if v]))
      time.sleep(0.01)

  def wiggleLEDs(self, reps=3):
    for i in range(reps):
      for i in range(5):
        self.setLED(i, True)
        time.sleep(0.05)
        self.setLED(i, False)



class UI_EdgeTpuDevBoard(UI):
  def __init__(self):
    super(UI_EdgeTpuDevBoard, self).__init__()

  

class TeachableMachine(object):
  def __init__(self, model_path, ui, kNN=3, buffer_length=4):
    assert os.path.isfile(model_path), 'Model file %s not found' % model_path
    self._engine = kNNEmbeddingEngine(model_path, kNN)
    self._ui = ui

    self._buffer = deque(maxlen=buffer_length)
    self._kNN = kNN
    self._start_time = time.time()
    self._frame_times = deque(maxlen=40)

  def classify(self, img, svg):

    global flaskImage
    global flaskStatus
    flaskImage = img
    # Classify current image and determine
    emb = self._engine.DetectWithImage(img)

    self._buffer.append(self._engine.kNNEmbedding(emb))
    classification = Counter(self._buffer).most_common(1)[0][0]

    # Interpret user button presses (if any)
    debounced_buttons = self._ui.getDebouncedButtonState()
    for i, b in enumerate(debounced_buttons):
      if not b:
        continue
      if i == 0:
        self._engine.clear()  # Hitting button 0 resets
      else:
        # otherwise the button # is the class
        self._engine.addEmbedding(emb, i)

    self._frame_times.append(time.time())
    fps = len(self._frame_times) / \
        float(self._frame_times[-1] - self._frame_times[0] + 0.001)

    # Print/Display results
    self._ui.setOnlyLED(classification)
    classes = ['--', 'One', 'Two', 'Three', 'Four']
    status = 'fps %.1f; #examples: %d; Class % 7s' % (
        fps, self._engine.exampleCount(),
        classes[classification or 0])
    #print(img)
    #print(type(img))
    #print(status)
    print(classes[classification or 0])


    flaskStatus = status
    svg.add(svg.text(status, insert=(26, 26), fill='black', font_size='20'))
    svg.add(svg.text(status, insert=(25, 25), fill='white', font_size='20'))



    
def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', help='File path of Tflite model.',
                        default='mobilenet_quant_v1_224_headless_edgetpu.tflite')
    parser.add_argument('--testui', dest='testui', action='store_true',
                        help='Run test of UI. Ctrl-C to abort.')
    parser.add_argument('--keyboard', dest='keyboard', action='store_true',
                        help='Run test of UI. Ctrl-C to abort.', default='--keyboard')
    args = parser.parse_args()

    # The UI differs a little depending on the system because the GPIOs
    # are a little bit different.
    print('Initialize UI.')
    platform = detectPlatform()
    if args.keyboard:
      ui = UI_Keyboard()
    else:
      if platform == 'devboard':
        ui = UI_EdgeTpuDevBoard()
      else:
        print('No GPIOs detected - falling back to Keyboard input')
        ui = UI_Keyboard()

    print('Initialize Model...')
    teachable = TeachableMachine(args.model, ui,)

    print('Start Pipeline.')
    result = gstreamer.run_pipeline(teachable.classify)
