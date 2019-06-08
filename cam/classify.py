

import argparse
import collections
import itertools
import time
import logging



import utils
#from apps import run_app

logger = logging.getLogger(__name__)


    
        

def render_gen(args):
    fps_counter = utils.avg_fps_counter(30)
    draw_overlay = True
    yield utils.input_image_size()
    while True:
        #tensor, layout, command = (yield output)
        
        inference_rate = next(fps_counter)
        if draw_overlay:
            start = time.monotonic()
       
        else:
            output = None

    


