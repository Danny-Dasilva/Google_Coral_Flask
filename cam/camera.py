import os
import threading

import gstreamer
import pipelines

from gst import *

class Camera:
    def __init__(self, render_size, inference_size, loop):
        self._layout = gstreamer.make_layout(inference_size, render_size)
        
        self._loop = loop
        self._thread = None
        self.render_overlay = None

    @property
    def resolution(self):
        return self._layout.render_size

    def request_key_frame(self):
        pass

    def start_recording(self, obj, format, profile, inline_headers, bitrate, intra_period):
        def on_buffer(data, _):
            obj.write(data)
        signals = {
          'h264sink': {'new-sample': gstreamer.new_sample_callback(on_buffer)},
        }

        pipeline = self.make_pipeline(format, profile, inline_headers, bitrate, intra_period)

        self._thread = threading.Thread(target=gstreamer.run_pipeline,
                                        args=(pipeline, self._layout, self._loop, gstreamer.Display.NONE,
                                              False, signals))                  
        self._thread.start()

    def stop_recording(self):
        gstreamer.quit()
        self._thread.join()

    def make_pipeline(self, fmt, profile, inline_headers, bitrate, intra_period):
        raise NotImplemented

class FileCamera(Camera):
    def __init__(self, filename, inference_size, loop):
        info = gstreamer.get_video_info(filename)
        super().__init__((info.get_width(), info.get_height()), inference_size,
                          loop=loop)
        self._filename = filename

    def make_pipeline(self, fmt, profile, inline_headers, bitrate, intra_period):
        return pipelines.video_streaming_pipeline(self._filename, self._layout)

class DeviceCamera(Camera):
    def __init__(self, fmt, inference_size):
        super().__init__(fmt.size, inference_size, loop=False)
        self._fmt = fmt

    def make_pipeline(self, fmt, profile, inline_headers, bitrate, intra_period):
        return pipelines.camera_streaming_pipeline(self._fmt, profile, bitrate, self._layout)

def make_camera(source, inference_size, loop):
    fmt = parse_format(source)
    if fmt:
        return DeviceCamera(fmt, inference_size)

    filename = os.path.expanduser(source)
    if os.path.isfile(filename):
        return FileCamera(filename, inference_size, loop)

    return None
