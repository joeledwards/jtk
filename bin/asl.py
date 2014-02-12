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

asl_path_file = ""
if os.environ.has_key('ASL_UTILITIES_PATH_FILE'):
    asl_path_file = os.path.abspath(os.environ['ASL_UTILITIES_PATH_FILE'])

try:
    home_directory = os.path.abspath(os.environ['HOME'])
except:
    home_directory = os.path.abspath(os.environ['USERPROFILE'])
if not os.path.isfile(asl_path_file):
    asl_path_file = os.path.abspath(home_directory + '/.asl_utilities_path')

if not os.path.isfile(asl_path_file):
    path = os.path.dirname(sys.path[1])
else:
    fh = open(asl_path_file, 'r')
    path = fh.readline().strip()

if not os.path.exists(path):
    print "ASL Utilities directory '%s' does not exist" % path
    sys.exit(1)
if not os.path.isdir(path):
    print "path '%s' exists, but is not a directory" % path
    sys.exit(1)

python_path = os.path.abspath(path + '/lib/python')
if not os.path.exists(python_path):
    python_path = os.path.abspath(path + '/python')

if not os.path.exists(python_path):
    print "Python library '%s' does not exist" % python_path
    sys.exit(1)
if not os.path.isdir(python_path):
    print "path '%s' exists, but is not a directory" % python_path
    sys.exit(1)

if platform.system() == 'Linux':
    if platform.architecture()[0] == '64bit':
        aescrypt_bin = os.path.abspath(path + '/utils/aescrypt/aescrypt.linux64')
    else:
        aescrypt_bin = os.path.abspath(path + '/utils/aescrypt/aescrypt.linux')
elif platform.system() == 'FreeBSD':
    aescrypt_bin = os.path.abspath(path + '/utils/aescrypt/aescrypt.bsd')
else:
    aescrypt_bin = os.path.abspath(path + '/utils/aescrypt/aescrypt.exe')
if not os.path.exists(aescrypt_bin):
    aescrypt_bin = ''

xmax_path = os.path.abspath(path + '/utils/xmax')
if not os.path.exists(xmax_path):
    xmax_path = ''


sys.path.insert(0, python_path)

