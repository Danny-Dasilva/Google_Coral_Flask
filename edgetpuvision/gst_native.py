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

import cairo
import contextlib
import ctypes
import threading

import gi
gi.require_version('Gdk', '3.0')
gi.require_version('GObject', '2.0')
gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gdk, GObject, Gst, GstBase, GstVideo

Gdk.init([])

# Gst.Buffer.map(Gst.MapFlags.WRITE) is broken, this is a workaround. See
# http://lifestyletransfer.com/how-to-make-gstreamer-buffer-writable-in-python/
# https://gitlab.gnome.org/GNOME/gobject-introspection/issues/69
class GstMapInfo(ctypes.Structure):
    _fields_ = [('memory', ctypes.c_void_p),                # GstMemory *memory
                ('flags', ctypes.c_int),                    # GstMapFlags flags
                ('data', ctypes.POINTER(ctypes.c_byte)),    # guint8 *data
                ('size', ctypes.c_size_t),                  # gsize size
                ('maxsize', ctypes.c_size_t),               # gsize maxsize
                ('user_data', ctypes.c_void_p * 4),         # gpointer user_data[4]
                ('_gst_reserved', ctypes.c_void_p * 4)]     # GST_PADDING

# ctypes imports for missing or broken introspection APIs.
libgst = ctypes.CDLL('libgstreamer-1.0.so.0')
libgst.gst_context_writable_structure.restype = ctypes.c_void_p
libgst.gst_context_writable_structure.argtypes = [ctypes.c_void_p]
libgst.gst_structure_set.restype = ctypes.c_void_p
libgst.gst_structure_set.argtypes = [ctypes.c_void_p, ctypes.c_char_p,
        ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p]
GST_MAP_INFO_POINTER = ctypes.POINTER(GstMapInfo)
libgst.gst_buffer_map.argtypes = [ctypes.c_void_p, GST_MAP_INFO_POINTER, ctypes.c_int]
libgst.gst_buffer_map.restype = ctypes.c_int
libgst.gst_buffer_unmap.argtypes = [ctypes.c_void_p, GST_MAP_INFO_POINTER]
libgst.gst_buffer_unmap.restype = None
libgst.gst_mini_object_is_writable.argtypes = [ctypes.c_void_p]
libgst.gst_mini_object_is_writable.restype = ctypes.c_int

libgdk = ctypes.CDLL('libgdk-3.so.0')
libgdk.gdk_wayland_window_get_wl_surface.restype = ctypes.c_void_p
libgdk.gdk_wayland_window_get_wl_surface.argtypes = [ctypes.c_void_p]
libgdk.gdk_wayland_display_get_wl_display.restype = ctypes.c_void_p
libgdk.gdk_wayland_display_get_wl_display.argtypes = [ctypes.c_void_p]

libcairo = ctypes.CDLL('libcairo.so.2')
libcairo.cairo_image_surface_create_for_data.restype = ctypes.c_void_p
libcairo.cairo_image_surface_create_for_data.argtypes = [ctypes.c_void_p,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
libcairo.cairo_surface_flush.restype = None
libcairo.cairo_surface_flush.argtypes = [ctypes.c_void_p]
libcairo.cairo_surface_destroy.restype = None
libcairo.cairo_surface_destroy.argtypes = [ctypes.c_void_p]
libcairo.cairo_format_stride_for_width.restype = ctypes.c_int
libcairo.cairo_format_stride_for_width.argtypes = [ctypes.c_int, ctypes.c_int]
libcairo.cairo_create.restype = ctypes.c_void_p
libcairo.cairo_create.argtypes = [ctypes.c_void_p]
libcairo.cairo_destroy.restype = None
libcairo.cairo_destroy.argtypes = [ctypes.c_void_p]

librsvg = ctypes.CDLL('librsvg-2.so.2')
librsvg.rsvg_handle_new_from_data.restype = ctypes.c_void_p
librsvg.rsvg_handle_new_from_data.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_void_p]
librsvg.rsvg_handle_render_cairo.restype = ctypes.c_bool
librsvg.rsvg_handle_render_cairo.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
librsvg.rsvg_handle_close.restype = ctypes.c_bool
librsvg.rsvg_handle_close.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

libgobject = ctypes.CDLL('libgobject-2.0.so.0')
libgobject.g_object_unref.restype = None
libgobject.g_object_unref.argtypes = [ctypes.c_void_p]

def set_display_contexts(sink, widget):
    handle = libgdk.gdk_wayland_window_get_wl_surface(hash(widget.get_window()))
    sink.set_window_handle(handle)

    wl_display = libgdk.gdk_wayland_display_get_wl_display(hash(Gdk.Display.get_default()))
    context = Gst.Context.new('GstWaylandDisplayHandleContextType', True)
    structure = libgst.gst_context_writable_structure(hash(context))
    libgst.gst_structure_set(structure, ctypes.c_char_p('display'.encode()),
            hash(GObject.TYPE_POINTER), wl_display, 0)
    sink.set_context(context)

@contextlib.contextmanager
def _gst_buffer_map(buffer, flags):
    ptr = hash(buffer)
    if flags & Gst.MapFlags.WRITE and libgst.gst_mini_object_is_writable(ptr) == 0:
        raise ValueError('Buffer not writable')

    mapping = GstMapInfo()
    success = libgst.gst_buffer_map(ptr, mapping, flags)
    if not success:
        raise RuntimeError('gst_buffer_map failed')
    try:
        yield ctypes.cast(mapping.data, ctypes.POINTER(ctypes.c_byte * mapping.size)).contents
    finally:
        libgst.gst_buffer_unmap(ptr, mapping)

class OverlaySource(GstBase.BaseSrc):
    __gstmetadata__ = ('<longname>', '<class>', '<description>', '<author>')
    __gsttemplates__ = (Gst.PadTemplate.new('src',
                                               Gst.PadDirection.SRC,
                                               Gst.PadPresence.ALWAYS,
                                               Gst.Caps.from_string(
                                                'video/x-raw,format=BGRA,framerate=0/1'
                                                )))

    @staticmethod
    def _plugin_init(plugin):
        gtype = GObject.type_register(OverlaySource)
        Gst.Element.register(plugin, 'overlaysrc', 0, gtype)
        return True

    @staticmethod
    def plugin_register():
        version = Gst.version()
        Gst.Plugin.register_static(
            version[0], version[1],         # GStreamer version
            '',                             # name
            '',                             # description
            OverlaySource._plugin_init,     # init_func
            '',                             # version
            'unknown',                      # license
            '',                             # source
            '',                             # package
            ''                              # origin
        )

    def __init__(self):
        GstBase.BaseSrc.__init__(self)
        self.set_format(Gst.Format.TIME)
        self.set_do_timestamp(False)
        self.set_live(True)
        self.cond = threading.Condition()
        self.width = 0
        self.height = 0
        self.min_stride = 0
        self.flushing = False
        self.eos = False
        self.svg = None
        self.pts = 0


    def do_decide_allocation(self, query):
        if query.get_n_allocation_pools() > 0:
            pool, size, min_buffers, max_buffers = query.parse_nth_allocation_pool(0)
            query.set_nth_allocation_pool(0, pool, size, min_buffers, min(max_buffers, 3))
        return GstBase.BaseSrc.do_decide_allocation(self, query)

    def do_event(self, event):
        if event.type == Gst.EventType.SEEK:
            _, _, flags, _, _, _, _ = event.parse_seek()
            if flags | Gst.SeekFlags.FLUSH:
                self.send_event(Gst.Event.new_flush_start())
                self.send_event(Gst.Event.new_flush_stop(True))
            return True
        return GstBase.BaseSrc.do_event(self, event)

    def set_eos(self):
        with self.cond:
            self.eos = True

    def do_start (self):
        self.set_svg(None, 0)
        return True

    def do_stop (self):
        self.set_svg(None, 0)
        return True

    def set_svg(self, svg, pts):
        with self.cond:
            self.svg = svg
            self.pts = pts
            self.eos = False
            self.cond.notify_all()

    def set_flushing(self, flushing):
        with self.cond:
            self.flushing = flushing
            self.cond.notify_all()

    def do_set_caps(self, caps):
        structure = caps.get_structure(0)
        self.width = structure.get_value('width')
        self.height = structure.get_value('height')
        self.min_stride = libcairo.cairo_format_stride_for_width(
                int(cairo.FORMAT_ARGB32), self.width)
        return True

    def do_unlock(self):
        self.set_flushing(True)
        return True

    def do_unlock_stop(self):
        self.set_flushing(False)
        return True

    def get_flow_return_locked(self, default=None):
        if self.eos:
            self.eos = False
            self.svg = None
            return Gst.FlowReturn.EOS
        if self.flushing:
            return Gst.FlowReturn.FLUSHING
        return default

    def do_fill(self, offset, size, buf):
        with self.cond:
            result = self.get_flow_return_locked()
            if result:
                return result

            while self.svg is None:
                self.cond.wait()
                result = self.get_flow_return_locked()
                if result:
                    return result

            assert self.svg is not None
            svg = self.svg
            pts = self.pts
            self.svg = None

        self.render_svg(svg, buf)
        buf.pts = pts

        with self.cond:
            return self.get_flow_return_locked(Gst.FlowReturn.OK)

    def render_svg(self, svg, buf):
        meta = GstVideo.buffer_get_video_meta(buf)
        if meta:
            assert meta.n_planes == 1
            assert meta.width == self.width
            assert meta.height == self.height
            assert meta.stride[0] >= self.min_stride
            stride = meta.stride[0]
        else:
            stride = self.min_stride

        with _gst_buffer_map(buf, Gst.MapFlags.WRITE) as mapped:
            assert len(mapped) >= stride * self.height

            # Fill with transparency.
            ctypes.memset(ctypes.addressof(mapped), 0, ctypes.sizeof(mapped))

            # If svg is '' (can't be None here) we return 100% transparency.
            if not svg:
                return

            surface = libcairo.cairo_image_surface_create_for_data(
                    ctypes.addressof(mapped),
                    int(cairo.FORMAT_ARGB32),
                    self.width,
                    self.height,
                    stride)

            # Render the SVG overlay.
            data = svg.encode('utf-8')
            context = libcairo.cairo_create(surface)
            handle = librsvg.rsvg_handle_new_from_data(data, len(data), 0)
            librsvg.rsvg_handle_render_cairo(handle, context)
            librsvg.rsvg_handle_close(handle, 0)
            libgobject.g_object_unref(handle)
            libcairo.cairo_surface_flush(surface)
            libcairo.cairo_surface_destroy(surface)
            libcairo.cairo_destroy(context)

OverlaySource.plugin_register()
