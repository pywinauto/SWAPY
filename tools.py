# SWAPY's tools set.
# Copyright (C) 2016 Matiychuk D.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
#    Free Software Foundation, Inc.,
#    59 Temple Place,
#    Suite 330,
#    Boston, MA 02111-1307 USA

"""SWAPY's tools set."""


import exceptions
import os.path
import sys
import traceback

import wx


def show_error_message(msg_type='ERROR', text="Something went wrong"):
    """
    Show a msgbox with traceback in non debug mode.

    Raise the original exception if debug.
    """
    if __debug__:
        raise

    else:
        frame = wx.GetApp().GetTopWindow()
        if msg_type == 'ERROR':
            dlg = wx.MessageDialog(frame, text, 'Error!',
                                   wx.OK | wx.ICON_ERROR)
        elif msg_type == 'WARNING':
            dlg = wx.MessageDialog(frame, traceback.format_exc(5),
                                   'Warning!', wx.OK | wx.ICON_WARNING)
        else:
            dlg = wx.MessageDialog(frame, text,
                                   'Unknown error - %s!' % msg_type,
                                   wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()

        if msg_type == 'ERROR':
            # close main window
            frame.Destroy()


def object_to_text(obj):
    """
    Convert any object to srting or unicode.

    The problem details:
    https://bugs.python.org/issue5876
    https://github.com/pywinauto/SWAPY/issues/78
    """
    # TODO: it's time to upgrade to Python 3!

    if isinstance(obj, basestring):
        # do not convert if string or unicode
        obj_text = obj
    else:
        # list, set, object or something else
        try:
            obj_text = str(obj)
        except exceptions.UnicodeEncodeError:
            # convert items manually.

            # a dict values lost in this case
            obj_text = str([unicode(item) for item in obj])

    return obj_text


def resource_path(filename):
    """
    Compose a resource path.

    Depending of the run type:
    - PyInstaller version >= 1.6
    - PyInstaller version < 1.6
    - direct run
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller >= 1.6
        filename = os.path.join(sys._MEIPASS, filename)
    elif '_MEIPASS2' in os.environ:
        # PyInstaller < 1.6 (tested on 1.5 only)
        filename = os.path.join(os.environ['_MEIPASS2'], filename)
    else:
        filename = os.path.join(os.path.dirname(sys.argv[0]), filename)
    return filename
