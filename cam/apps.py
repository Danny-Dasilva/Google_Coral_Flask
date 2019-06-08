import argparse
import logging
import signal
import cam.utils
import time
from cam.camera import make_camera
from cam.gstreamer import Display, run_gen
from cam.streaming.server import StreamingServer

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


def run_server(render_gen):
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--source',
                        help='/dev/videoN:FMT:WxH:N/D or .mp4 file or image file',
                        default='/dev/video0:YUY2:640x480:30/1')
    parser.add_argument('--bitrate', type=int, default=1000000,
                        help='Video streaming bitrate (bit/s)')
    parser.add_argument('--loop', default=False, action='store_true',
                        help='Loop input video file')

    
    args = parser.parse_args()

    gen = render_gen(args)
    
    camera = make_camera(args.source, next(gen), args.loop)
    assert camera is not None

    with StreamingServer(camera, args.bitrate) as server:
        signal.pause()

