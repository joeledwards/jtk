#!/usr/bin/env python
import os
import platform
import sys

try:
    import pygtk
    pygtk.require('2.0')
    import gtk
    import gobject
    GTK = True
    default_interp = gtk.gdk.INTERP_HYPER
except:
    GTK = False
    default_interp = None

icons = {}

def new_icon_gtk(id, enone=False):
    image_file = os.path.abspath('%s/icons/%s.png' % (path, id))
    # Is this icon already in the buffer
    if not icons.has_key(id):
        if os.path.exists(image_file):
            # Create a new icon
            img = gtk.Image()
            img.set_from_file(image_file)
            # Add the new icon to the buffer
            icons[id] = img.get_pixbuf()
            return icons[id]
    else:
        # If we have this icon buffered, return its reference
        return icons[id]

    if not enone:
        try:
            if not icons.has_key('file_broken'):
                img = gtk.Image()
                img.set_from_file(image_file)
                # Add the new icon to the buffer
                icons['file_broken'] = img.get_pixbuf()
                return icons['file_broken']
            else:
                return icons['file_broken']
        except:
            pass
    return None

def new_icon_none(id):
    return None

def scale_pixbuf_gtk(pix, width=None, height=None, lock=True, interp_type=default_interp):
    if (not width) or (not height):
        old_width = pix.get_width()
        old_height = pix.get_height()
        if width:
            if lock:
                height = width * old_height / old_width
            else:
                height = old_height
        elif height:
            if lock:
                width = height * old_width / old_height
            else:
                width = old_width
        else:
            return None
    return pix.scale_simple(width, height, interp_type)

def scale_pixbuf_none(pix, height=None, width=None, lock=True, interp_type=None):
    return None

# Point the function to a stub if we don't have GTK support
if GTK:
    new_icon = new_icon_gtk
    scale_pixbuf = scale_pixbuf_gtk
else:
    new_icon = new_icon_none
    scale_pixbuf = scale_pixbuf_none

sys.path.insert(0, "..")

