import collections
import contextlib
import enum
import fcntl
import functools
import os
import pathlib
import shutil
import queue
import signal
import sys
import termios
import threading
import time

import numpy as np

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GLib', '2.0')
gi.require_version('GObject', '2.0')
gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
gi.require_version('GstPbutils', '1.0')
from gi.repository import GLib, GObject, Gst, GstBase, Gtk


global ls

GObject.threads_init()
Gst.init([])
Gtk.init([])

from gi.repository import GstPbutils  # Must be called after Gst.init().

from PIL import Image

from gst_native import set_display_contexts
from pipelines import *

COMMAND_SAVE_FRAME = ' '
COMMAND_SAVE_FRAME_1 = '1'
DELETEFILES = 'd'
COMMAND_PRINT_INFO = 'p'
COMMAND_QUIT       = 'q'
WINDOW_TITLE       = 'Coral'

class Display(enum.Enum):
    FULLSCREEN = 'fullscreen'
    WINDOW = 'window'
    NONE = 'none'

    def __str__(self):
        return self.value

@contextlib.contextmanager
def nonblocking(fd):
    os.set_blocking(fd, False)
    try:
        yield
    finally:
        os.set_blocking(fd, True)

@contextlib.contextmanager
def term_raw_mode(fd):
    old = termios.tcgetattr(fd)
    new = termios.tcgetattr(fd)
    new[3] = new[3] & ~(termios.ICANON | termios.ECHO)
    termios.tcsetattr(fd, termios.TCSANOW, new)
    try:
        yield
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, old)

@contextlib.contextmanager
def Commands():
    commands = queue.Queue()

    def on_keypress(fd, flags):
        for ch in sys.stdin.read():
            commands.put(ch)
        return True

    def get_nowait():
        try:
            return commands.get_nowait()
        except queue.Empty:
            return None

    if sys.stdin.isatty():
        fd = sys.stdin.fileno()
        GLib.io_add_watch(fd, GLib.IO_IN, on_keypress)
        with term_raw_mode(fd), nonblocking(fd):
            yield get_nowait
    else:
        yield lambda: None

@contextlib.contextmanager
def Worker(process, maxsize=0):
    commands = queue.Queue(maxsize)

    def run():
        while True:
            args = commands.get()
            if args is None:
                break
            process(*args)
            commands.task_done()

    thread = threading.Thread(target=run)
    thread.start()
    try:
        yield commands
    finally:
        commands.put(None)
        thread.join()

def save_frame(del_files, cmd, rgb, size, overlay=None, ext='png'):
    print(cmd)
    tag = '%010d' % int(time.monotonic() * 1000)
    img = Image.frombytes('RGB', size, rgb, 'raw')
    img_pth = cmd
  
    name = img_pth + 'img-%s.%s' % (tag, ext)
    img.save(name)
    # check directory and save file 
    list = os.listdir(img_pth) # dir is your directory path
    number_files = len(list)
    print(number_files)
    if number_files <= 600:
        img.save(name)
    print('Frame saved as "%s"' % name)

    #deleting files command
    if del_files == 1:
        shutil.rmtree("image_folder/object_1/") 
        shutil.rmtree("image_folder/object_2/") 
        os.mkdir("image_folder/object_1/")
        os.mkdir("image_folder/object_2/")
        print("FILES_DELETED")
    if overlay:
        name = 'overlay/img-%s.svg' % tag
        with open(name, 'w') as f:
            f.write(overlay)
        print('Overlay saved as "%s"' % name)
    
    print('Overlay saved as "%s"' % name)



Layout = collections.namedtuple('Layout', ('size', 'window', 'inference_size', 'render_size'))

def make_layout(inference_size, render_size):
    inference_size = Size(*inference_size)
    print(inference_size)
    render_size = Size(*render_size)
    print(render_size)
    size = min_outer_size(inference_size, render_size)
    window = center_inside(render_size, size)
    return Layout(size=size, window=window,
                  inference_size=inference_size, render_size=render_size)

def caps_size(caps):
    structure = caps.get_structure(0)
    return Size(structure.get_value('width'),
                structure.get_value('height'))

def get_video_info(filename):
    uri = pathlib.Path(filename).absolute().as_uri()
    discoverer = GstPbutils.Discoverer()
    info = discoverer.discover_uri(uri)

    streams = info.get_video_streams()
    assert len(streams) == 1
    return streams[0]

def is_seekable(element):
    query = Gst.Query.new_seeking(Gst.Format.TIME)
    if element.query(query):
        _,  seekable, _, _ = query.parse_seeking()
        return seekable
    return False

@contextlib.contextmanager
def pull_sample(sink):
    sample = sink.emit('pull-sample')
    buf = sample.get_buffer()

    result, mapinfo = buf.map(Gst.MapFlags.READ)
    if result:
        yield sample, mapinfo.data
    buf.unmap(mapinfo)

def new_sample_callback(process):
    def callback(sink, pipeline):
        with pull_sample(sink) as (sample, data):
            process(data, caps_size(sample.get_caps()))
        return Gst.FlowReturn.OK
    return callback

def on_bus_message(bus, message, pipeline, loop):
    if message.type == Gst.MessageType.EOS:
        if loop and is_seekable(pipeline):
            flags = Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT
            if not pipeline.seek_simple(Gst.Format.TIME, flags, 0):
                Gtk.main_quit()
        else:
            Gtk.main_quit()
    elif message.type == Gst.MessageType.WARNING:
        err, debug = message.parse_warning()
        sys.stderr.write('Warning: %s: %s\n' % (err, debug))
    elif message.type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        sys.stderr.write('Error: %s: %s\n' % (err, debug))
        Gtk.main_quit()

def on_new_sample(sink, pipeline, layout, images, get_command):
    
    with pull_sample(sink) as (sample, data):
        custom_command = None
        save_frame = False
        del_files = 0
        command = get_command()
        if command == COMMAND_SAVE_FRAME:
            cmd = "image_folder/object_1/"
            save_frame = True
        
        if command == DELETEFILES:
            cmd = "image_folder/object_1/"
            del_files = 1
            save_frame = True
        
        if command == COMMAND_SAVE_FRAME_1:
            cmd = "image_folder/object_2/"
            save_frame = True
        
        elif command == COMMAND_PRINT_INFO:
            print('Timestamp: %.2f' % time.monotonic())
            print('Render size: %d x %d' % layout.render_size)
            print('Inference size: %d x %d' % layout.inference_size)
        elif  command == COMMAND_QUIT:
            Gtk.main_quit()
        else:
            custom_command = command

        
      
        if save_frame:
            images.put((del_files, cmd, data, layout.inference_size))
         
        
        

    return Gst.FlowReturn.OK

def run_gen(render_overlay_gen, *, source, downscale, loop, display):
    inference_size = render_overlay_gen.send(None)  # Initialize.
    return run(inference_size,
        lambda tensor, layout, command:
            render_overlay_gen.send((tensor, layout, command)),
        source=source,
        downscale=downscale,
        loop=loop,
        display=display)

def run(inference_size, render_overlay, *, source, downscale, loop, display):
    result = get_pipeline(source, inference_size, downscale, display)
    if result:
        layout, pipeline = result
        run_pipeline(pipeline, layout, loop, display)
        #render_overlay, display)
        return True

    return False

def get_pipeline(source, inference_size, downscale, display):
    fmt = parse_format(source)
    if fmt:
        layout = make_layout(inference_size, fmt.size)
        return layout, camera_pipeline(fmt, layout, display)

    filename = os.path.expanduser(source)
    if os.path.isfile(filename):
        info = get_video_info(filename)
        render_size = Size(info.get_width(), info.get_height()) / downscale
        layout = make_layout(inference_size, render_size)
        return layout, file_pipline(info.is_image(), filename, layout, display)

    return None

def camera_pipeline(fmt, layout, display):
    if display is Display.NONE:
        return camera_headless_pipeline(fmt, layout)
    else:
        return camera_display_pipeline(fmt, layout)

def file_pipline(is_image, filename, layout, display):
    if display is Display.NONE:
        if is_image:
            return image_headless_pipeline(filename, layout)
        else:
            return video_headless_pipeline(filename, layout)
    else:
        fullscreen = display is Display.FULLSCREEN
        if is_image:
            return image_display_pipeline(filename, layout)
        else:
            return video_display_pipeline(filename, layout)

def quit():
    Gtk.main_quit()

def run_pipeline(pipeline, layout, loop, display, handle_sigint=True, signals=None):
    
    # Create pipeline
    pipeline = describe(pipeline)
    print(pipeline)
    pipeline = Gst.parse_launch(pipeline)

    if display is not Display.NONE:
        # Workaround for https://gitlab.gnome.org/GNOME/gtk/issues/844 in gtk3 < 3.24.
        widget_draws = 123
        def on_widget_draw(widget, cairo):
            nonlocal widget_draws
            if widget_draws:
                 widget.queue_draw()
                 widget_draws -= 1
            return False

        # Needed to account for window chrome etc.
        def on_widget_configure(widget, event, glsink):
            allocation = widget.get_allocation()
            glsink.set_render_rectangle(allocation.x, allocation.y,
                    allocation.width, allocation.height)
            return False

        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_title(WINDOW_TITLE)
        window.set_default_size(layout.render_size.width, layout.render_size.height)
        if display is Display.FULLSCREEN:
            window.fullscreen()

        drawing_area = Gtk.DrawingArea()
        window.add(drawing_area)
        drawing_area.realize()

        glsink = pipeline.get_by_name('glsink')
        set_display_contexts(glsink, drawing_area)
        drawing_area.connect('draw', on_widget_draw)
        drawing_area.connect('configure-event', on_widget_configure, glsink)
        window.connect('delete-event', Gtk.main_quit)
        window.show_all()

    with Worker(save_frame) as images, Commands() as get_command:
        signals = {'appsink':
            {'new-sample': functools.partial(on_new_sample,
                layout=layout,
                images=images,
                get_command=get_command)},
            **(signals or {})
        }
        
        for name, signals in signals.items():
            component = pipeline.get_by_name(name)
            if component:
                for signal_name, signal_handler in signals.items():
                    component.connect(signal_name, signal_handler, pipeline)

        # Set up a pipeline bus watch to catch errors.
        bus = pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message', on_bus_message, pipeline, loop)

        # Handle signals.
        if handle_sigint:
            GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit)

        # Run pipeline.
        pipeline.set_state(Gst.State.PLAYING)
        try:
            Gtk.main()
        except KeyboardInterrupt:
            pass
        finally:
            pipeline.set_state(Gst.State.NULL)

        # Process all pending MainContext operations.
        while GLib.MainContext.default().iteration(False):
            pass
