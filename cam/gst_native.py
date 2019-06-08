import cairo
import contextlib
import ctypes

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
libcairo.cairo_surface_status.restype = ctypes.c_int
libcairo.cairo_surface_status.argtypes = [ctypes.c_void_p]
libcairo.cairo_format_stride_for_width.restype = ctypes.c_int
libcairo.cairo_format_stride_for_width.argtypes = [ctypes.c_int, ctypes.c_int]
libcairo.cairo_create.restype = ctypes.c_void_p
libcairo.cairo_create.argtypes = [ctypes.c_void_p]
libcairo.cairo_destroy.restype = None
libcairo.cairo_destroy.argtypes = [ctypes.c_void_p]
libcairo.cairo_scale.restype = None
libcairo.cairo_scale.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_double]

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

# GStreamer Element that attaches VideoOverlayComposition to buffers passing by.
class OverlayInjector(GstBase.BaseTransform):
    __gstmetadata__ = ('<longname>', '<class>', '<description>', '<author>')
    __gsttemplates__ = (Gst.PadTemplate.new('src',
                                               Gst.PadDirection.SRC,
                                               Gst.PadPresence.ALWAYS,
                                               Gst.Caps.new_any()),
                        Gst.PadTemplate.new('sink',
                                               Gst.PadDirection.SINK,
                                               Gst.PadPresence.ALWAYS,
                                               Gst.Caps.new_any()))

    @staticmethod
    def _plugin_init(plugin):
        gtype = GObject.type_register(OverlayInjector)
        Gst.Element.register(plugin, 'overlayinjector', 0, gtype)
        return True

    @staticmethod
    def plugin_register():
        version = Gst.version()
        Gst.Plugin.register_static(
            version[0], version[1],         # GStreamer version
            '',                             # name
            '',                             # description
            OverlayInjector._plugin_init,   # init_func
            '',                             # version
            'unknown',                      # license
            '',                             # source
            '',                             # package
            ''                              # origin
        )

    def __init__(self):
        GstBase.BaseTransform.__init__(self)
        GstBase.BaseTransform.set_in_place(self, True)
        self.render_size = None
        self.svg = None
        self.rendered_svg = None
        self.composition = None
        self.scale_factor = 0.75

    def set_svg(self, svg, render_size):
        self.svg = svg
        self.render_size = render_size

    def do_transform_ip(self, frame_buf):
        self.render()
        if self.composition:
            # Note: Buffer IS writable (ref is 1 in native land). However gst-python
            # took an additional ref so it's now 2 and gst_buffer_is_writable
            # returns false. We can't modify the buffer without fiddling with refcount.
            if frame_buf.mini_object.refcount != 2:
                return Gst.FlowReturn.ERROR
            frame_buf.mini_object.refcount -= 1
            GstVideo.buffer_add_video_overlay_composition_meta(frame_buf, self.composition)
            frame_buf.mini_object.refcount += 1
        return Gst.FlowReturn.OK


    def render(self):
        if not self.svg:
            self.composition = None
            self.rendered_svg = None
            return

        if self.svg == self.rendered_svg:
            return

        overlay_size = self.render_size * self.scale_factor
        stride = libcairo.cairo_format_stride_for_width(
                int(cairo.FORMAT_ARGB32), overlay_size.width)
        overlay_buffer = Gst.Buffer.new_allocate(None,
                stride * overlay_size.height)
        with _gst_buffer_map(overlay_buffer, Gst.MapFlags.WRITE) as mapped:
            # Fill with transparency and create surface from buffer.
            ctypes.memset(ctypes.addressof(mapped), 0, ctypes.sizeof(mapped))
            surface = libcairo.cairo_image_surface_create_for_data(
                    ctypes.addressof(mapped),
                    int(cairo.FORMAT_ARGB32),
                    overlay_size.width,
                    overlay_size.height,
                    stride)

            # Render the SVG overlay.
            data = self.svg.encode('utf-8')
            context = libcairo.cairo_create(surface)
            libcairo.cairo_scale(context, self.scale_factor, self.scale_factor)
            handle = librsvg.rsvg_handle_new_from_data(data, len(data), 0)
            librsvg.rsvg_handle_render_cairo(handle, context)
            librsvg.rsvg_handle_close(handle, 0)
            libgobject.g_object_unref(handle)
            libcairo.cairo_surface_flush(surface)
            libcairo.cairo_surface_destroy(surface)
            libcairo.cairo_destroy(context)

            # Attach overlay to VideoOverlayComposition.
            GstVideo.buffer_add_video_meta(overlay_buffer,
                    GstVideo.VideoFrameFlags.NONE, GstVideo.VideoFormat.BGRA,
                    overlay_size.width, overlay_size.height)
            rect = GstVideo.VideoOverlayRectangle.new_raw(overlay_buffer,
                    0, 0, self.render_size.width, self.render_size.height,
                    GstVideo.VideoOverlayFormatFlags.PREMULTIPLIED_ALPHA)
            self.composition = GstVideo.VideoOverlayComposition.new(rect)
            self.rendered_svg = self.svg

OverlayInjector.plugin_register()
