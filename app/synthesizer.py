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
import itertools

import numpy as np
from PIL import Image
import svgwrite
from app import gstreamer
from app.pose_engine import PoseEngine

import fluidsynth

OCTAVE = 12
FIFTH = 7
MINOR_THIRD = 3
CIRCLE_OF_FIFTHS = tuple((i * FIFTH) % OCTAVE
                         for i in range(OCTAVE))

# first 5 fifths in order, e.g. C G D A E => C D E G A
MAJOR_PENTATONIC = tuple(sorted(CIRCLE_OF_FIFTHS[:5]))

# same as pentatonic major but starting at 9
# e.g. C D E G A = 0 2 4 7 9 => 3 5 7 10 0 = C D E G A => A C D E G
MINOR_PENTATONIC = tuple(sorted((i + MINOR_THIRD) % OCTAVE
                                for i in MAJOR_PENTATONIC))

SCALE = MAJOR_PENTATONIC

# General Midi ids
OVERDRIVEN_GUITAR = 30
ELECTRIC_BASS_FINGER = 34
VOICE_OOHS = 54

CHANNELS = (OVERDRIVEN_GUITAR, ELECTRIC_BASS_FINGER, VOICE_OOHS)

class Identity:
    def __init__(self, color, base_note, instrument, extent=2*OCTAVE):
        self.color = color
        self.base_note = base_note
        self.channel = CHANNELS.index(instrument)
        self.extent = extent


IDENTITIES = (
    Identity('cyan', 24, OVERDRIVEN_GUITAR),
    Identity('magenta', 12, ELECTRIC_BASS_FINGER),
    Identity('yellow', 36, VOICE_OOHS),
)


class Pose:
    def __init__(self, pose, threshold):
        self.pose = pose
        self.id = None
        self.keypoints = {label: k for label, k in pose.keypoints.items()
                          if k.score > threshold}
        self.center = (np.mean([k.yx for k in self.keypoints.values()], axis=0)
                       if self.keypoints else None)

    def quadrance(self, other):
        d = self.center - other.center
        return d.dot(d)


class PoseTracker:
    def __init__(self):
        self.prev_poses = []
        self.next_pose_id = 0

    def assign_pose_ids(self, poses):
        """copy nearest pose ids from previous frame to current frame"""
        all_pairs = sorted(itertools.product(poses, self.prev_poses),
                           key=lambda pair: pair[0].quadrance(pair[1]))
        used_ids = set()
        for pose, prev_pose in all_pairs:
            if pose.id is None and prev_pose.id not in used_ids:
                pose.id = prev_pose.id
                used_ids.add(pose.id)

        for pose in poses:
            if pose.id is None:
                pose.id = self.next_pose_id
                self.next_pose_id += 1

        self.prev_poses = poses




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

        # break
        self.pose_tracker = PoseTracker()
        self.synth = fluidsynth.Synth()

        self.synth.start('alsa')
        soundfont_id = self.synth.sfload('/usr/share/sounds/sf2/FluidR3_GM.sf2')
        for channel, instrument in enumerate(CHANNELS):
            self.synth.program_select(channel, soundfont_id, 0, instrument)

        self.prev_notes = set()

    def render_overlay(self, image):

        outputs, inference_time = self.engine.DetectPosesInImage(image)

        poses = [pose for pose in (Pose(pose, 0.2) for pose in outputs)
                 if pose.keypoints]
        self.pose_tracker.assign_pose_ids(poses)

        velocities = {}
        for pose in poses:
            left = pose.keypoints.get('left wrist')
            right = pose.keypoints.get('right wrist')
            if not (left and right): continue

            self.identity = IDENTITIES[pose.id % len(IDENTITIES)]
            left = 1 - left.yx[0] / self.engine.image_height
            right = 1 - right.yx[0] / self.engine.image_height
            velocity = int(left * 100)
            i = int(right * self.identity.extent)
            note = (self.identity.base_note
                    + OCTAVE * (i // len(SCALE))
                    + SCALE[i % len(SCALE)])
            velocities[(self.identity.channel, note)] = velocity

        for note in self.prev_notes:
            if note not in velocities: self.synth.noteoff(*note)
        for note, velocity in velocities.items():
            if note not in self.prev_notes: self.synth.noteon(*note, velocity)
        self.prev_notes = velocities.keys()

        for i, pose in enumerate(poses):
            self.identity = IDENTITIES[pose.id % len(IDENTITIES)]

        flaskStatus = outputs
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

