# tools for unit tests.
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

"""tools for unit tests."""


from contextlib import contextmanager
import os

from pywinauto.application import Application
from pywinauto.sysinfo import is_x64_Python


SAMPLE_APPS_PATH = u"..\\apps\\MFC_samples"


@contextmanager
def test_app(filename):
    """Context manager for sample apps."""
    mfc_samples_folder = os.path.join(os.path.dirname(__file__),
                                      SAMPLE_APPS_PATH)
    if is_x64_Python():
        sample_exe = os.path.join(mfc_samples_folder, "x64", filename)
    else:
        sample_exe = os.path.join(mfc_samples_folder, filename)

    app = Application().start(sample_exe, timeout=3)
    app_path = os.path.normpath(sample_exe).encode('unicode-escape')
    try:
        yield app, app_path
    except:
        # Re-raise AssertionError and others
        raise
    finally:
        app.kill_()
