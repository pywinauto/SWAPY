# unit tests for code generator
# Copyright (C) 2015 Matiychuk D.
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

from contextlib import contextmanager
import os
import string
import unittest

from pywinauto.application import Application
from pywinauto.sysinfo import is_x64_Python

import code_manager
import const
import proxy


SAMPLE_APPS_PATH = u"..\\apps\\MFC_samples"


def get_proxy_object(pwa_window, path):
    if not pwa_window:
        proxy_object = proxy.PC_system(None)
    else:
        proxy_object = proxy.Pwa_window(pwa_window)
    for target_sub in path:
        subitems = proxy_object.Get_subitems()
        if not subitems:
            raise RuntimeError("'%s' cannot be found" % target_sub)
        for name, pwa_object in subitems:
            if target_sub == name:
                proxy_object = pwa_object
                break
        else:
            raise RuntimeError("Invalid path, '%s' not found" % target_sub)

    return proxy_object


@contextmanager
def test_app(filename):
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


class BaseTestCase(unittest.TestCase):

    def setUp(self):

        """
        Since the tests require different apps, use `with` statement instead.
        All setUp actions moved in the test_app contextmanager.
        """

        pass

    def tearDown(self):

        """
        All app's tearDown moved into the test_app contextmanager.
        """

        code_manager.CodeManager().clear()  # Clear single tone CodeManager
        reload(code_manager)  # Reset class's counters
        reload(proxy)  # Reset class's counters


class ObjectBrowserTestCases(BaseTestCase):

    def testNestedControl(self):

        direct_path = (u'Common Controls Sample',
                       u'Treeview1, Birds, Eagle, Hummingbird, Pigeon',
                       u'Birds',
                       )

        indirect_path = (u'Common Controls Sample',
                         u'CTreeCtrl',
                         u'Treeview1, Birds, Eagle, Hummingbird, Pigeon',
                         u'Birds',
                         )

        with test_app("CmnCtrl1.exe") as (app, app_path):
            self.assertRaises(RuntimeError, get_proxy_object,
                              None, indirect_path)

            proxy_obj = get_proxy_object(None, direct_path)
            self.assertEqual(proxy_obj.pwa_obj.elem,
                             app.Dialog.TreeView.GetItem(['Birds']).elem)


class EmptyTextsTestCases(BaseTestCase):

    def testToolbarCode(self):
        expected_code = \
            "from pywinauto.application import Application\n\n" \
            "{app_ident}1 = Application().Start(cmd_line=u'{app_path}')\n" \
            "{win_ident}1 = {app_ident}1['RowList Sample Application']\n" \
            "{win_ident}1.Wait('ready')\n" \
            "toolbarwindow1 = {win_ident}1['4']\n" \
            "pwa_toolbar_button1 = toolbarwindow1.Button(9)\n" \
            "pwa_toolbar_button1.Click()\n\n" \
            "{app_ident}1.Kill_()"

        path = (u'RowList Sample Application',
                u'Toolbar',
                u'button #9',
                )

        with test_app("RowList.exe") as (app, app_path):

            window = app.top_window_()

            class_name = window.GetProperties()['Class']
            crtl_class = filter(lambda c: c in string.ascii_letters,
                                class_name).lower()

            proxy_obj = get_proxy_object(None, path)
            code = proxy_obj.Get_code('Click')

        expected_code = expected_code.format(app_ident="app_%s" % crtl_class,
                                             app_path=app_path,
                                             class_name=class_name,
                                             win_ident=crtl_class)
        self.assertEquals(expected_code, code)


class CodeGeneratorTestCases(BaseTestCase):

    def testInitAllParents(self):
        expected_code = \
            "from pywinauto.application import Application\n\n" \
            "app_pwa_window1 = Application().Start(cmd_line=u'{app_path}')\n" \
            "pwa_window1 = app_pwa_window1.Dialog\n" \
            "pwa_window1.Wait('ready')\n" \
            "systreeview1 = pwa_window1.TreeView\n" \
            "pwa_tree_item1 = systreeview1.GetItem(['Birds'])\n" \
            "pwa_tree_item1.Expand()\n\n" \
            "app_pwa_window1.Kill_()"

        path = (u'Common Controls Sample',
                u'Treeview1, Birds, Eagle, Hummingbird, Pigeon',
                u'Birds',
                )

        with test_app("CmnCtrl1.exe") as (app, app_path):
            proxy_obj = get_proxy_object(None, path)
            code = proxy_obj.Get_code('Expand')

        expected_code = expected_code.format(app_path=app_path)
        self.assertEquals(expected_code, code)

    def testReuseVariable(self):
        expected_code = \
            "from pywinauto.application import Application\n\n" \
            "app_pwa_window1 = Application().Start(cmd_line=u'{app_path}')\n" \
            "pwa_window1 = app_pwa_window1.Dialog\n" \
            "pwa_window1.Wait('ready')\n" \
            "systreeview1 = pwa_window1.TreeView\n" \
            "pwa_tree_item1 = systreeview1.GetItem(['Birds'])\n" \
            "pwa_tree_item1.Expand()\n" \
            "pwa_tree_item1.Click()\n\n" \
            "app_pwa_window1.Kill_()"

        path = (u'Common Controls Sample',
                u'Treeview1, Birds, Eagle, Hummingbird, Pigeon',
                u'Birds',
                )

        with test_app("CmnCtrl1.exe") as (app, app_path):
            proxy_obj = get_proxy_object(None, path)
            proxy_obj.Get_code('Expand')  # First call
            code = proxy_obj.Get_code('Click')

        expected_code = expected_code.format(app_path=app_path)
        self.assertEquals(expected_code, code)
        
    def testChangeCodeStyle(self):

        expected_code_connect = \
            "from pywinauto.application import Application\n\n" \
            "app_pwa_window1 = Application().Connect(title=u'Common " \
            "Controls Sample', class_name='#32770')\n" \
            "pwa_window1 = app_pwa_window1.Dialog\n" \
            "systreeview1 = pwa_window1.TreeView\n" \
            "pwa_tree_item1 = systreeview1.GetItem(['Birds'])\n" \
            "pwa_tree_item1.Expand()\n\n"

        expected_code_start = \
            "from pywinauto.application import Application\n\n" \
            "app_pwa_window1 = Application().Start(cmd_line=u'{app_path}')\n" \
            "pwa_window1 = app_pwa_window1.Dialog\n" \
            "pwa_window1.Wait('ready')\n" \
            "systreeview1 = pwa_window1.TreeView\n" \
            "pwa_tree_item1 = systreeview1.GetItem(['Birds'])\n" \
            "pwa_tree_item1.Expand()\n\n" \
            "app_pwa_window1.Kill_()"

        control_path = (u'Common Controls Sample',
                        u'Treeview1, Birds, Eagle, Hummingbird, Pigeon',
                        u'Birds',
                        )

        with test_app("CmnCtrl1.exe") as (app, app_path):
            proxy_obj = get_proxy_object(None, control_path)
            window_obj = proxy_obj.parent.parent

            # Default code style
            code_default = proxy_obj.Get_code('Expand')
            expected_code_start = expected_code_start.format(
                app_path=app_path)
            self.assertEquals(expected_code_start, code_default)

            # Switch to Connect
            window_obj.SetCodestyle(
                [menu_id for menu_id, command in const.EXTENDED_ACTIONS.items()
                 if command == 'Application.Connect'][0])
            code_connect = proxy_obj.Get_code()
            self.assertEquals(expected_code_connect, code_connect)

            # Switch back to Start
            window_obj.SetCodestyle(
                [menu_id for menu_id, command in const.EXTENDED_ACTIONS.items()
                 if command == 'Application.Start'][0])
            code_start = proxy_obj.Get_code()
            expected_code_start = expected_code_start.format(
                app_path=app_path)
            self.assertEquals(expected_code_start, code_start)


class ControlsCodeTestCases(BaseTestCase):

    def testComboBoxCode(self):
        expected_code = \
            "from pywinauto.application import Application\n\n" \
            "app_pwa_window1 = Application().Start(cmd_line=u'{app_path}')\n" \
            "pwa_window1 = app_pwa_window1.Dialog\n" \
            "pwa_window1.Wait('ready')\n" \
            "combobox1 = pwa_window1.ComboBox\n" \
            "combobox1.Select('Gray')\n\n" \
            "app_pwa_window1.Kill_()"

        path = (u'Common Controls Sample',
                u'Gray, Gray, White, Black',
                u'Gray',
                )

        with test_app("CmnCtrl3.exe") as (app, app_path):
            proxy_obj = get_proxy_object(None, path)
            code = proxy_obj.Get_code('Select')

        expected_code = expected_code.format(app_path=app_path)
        self.assertEquals(expected_code, code)

    def testMenuCode(self):
        expected_code = \
            "from pywinauto.application import Application\n\n" \
            "app_pwa_window1 = Application().Start(cmd_line=u'{app_path}')\n" \
            "pwa_window1 = app_pwa_window1.Dialog\n" \
            "pwa_window1.Wait('ready')\n" \
            "pwa_menu_item1 = pwa_window1.MenuItem" \
            "(u'&Help->&About mymenu...')\n" \
            "pwa_menu_item1.Click()\n\n" \
            "app_pwa_window1.Kill_()"

        path = (u'BCDialogMenu',
                u'!Menu',
                u'&Help',
                u'&Help submenu',
                u'&About mymenu...'
                )

        with test_app("BCDialogMenu.exe") as (app, app_path):
            proxy_obj = get_proxy_object(None, path)
            code = proxy_obj.Get_code('Click')

        expected_code = expected_code.format(app_path=app_path)
        self.assertEquals(expected_code, code)

    def testSysListView32Code(self):
        expected_code = \
            "from pywinauto.application import Application\n\n" \
            "{app_ident}1 = Application().Start(cmd_line=u'{app_path}')\n" \
            "{win_ident}1 = {app_ident}1['RowList Sample Application']\n" \
            "{win_ident}1.Wait('ready')\n" \
            "syslistview1 = {win_ident}1['1']\n" \
            "listview_item1 = syslistview1.GetItem('Gray')\n" \
            "listview_item1.Click()\n\n" \
            "{app_ident}1.Kill_()"

        path = (u'RowList Sample Application',

                u'Yellow, 255, 255, 0, 40, 240, 120, Neutral, Red, 255, 0, 0, '
                u'0, 240, 120, Warm, Green, 0, 255, 0, 80, 240, 120, Cool, '
                u'Magenta, 255, 0, 255, 200, 240, 120, Warm, Cyan, 0, 255, '
                u'255, 120, 240, 120, Cool, Blue, 0, 0, 255, 160, 240, 120, '
                u'Cool, Gray, 192, 192, 192, 160, 0, 181, Neutral',

                u'Gray',
                )

        with test_app("RowList.exe") as (app, app_path):

            window = app.top_window_()

            class_name = window.GetProperties()['Class']
            crtl_class = filter(lambda c: c in string.ascii_letters,
                                class_name).lower()

            proxy_obj = get_proxy_object(None, path)
            code = proxy_obj.Get_code('Click')

        expected_code = expected_code.format(app_ident="app_%s" % crtl_class,
                                             app_path=app_path,
                                             class_name=class_name,
                                             win_ident=crtl_class)
        self.assertEquals(expected_code, code)

    def testSysTabControl32Code(self):
        expected_code = \
            "from pywinauto.application import Application\n\n" \
            "app_pwa_window1 = Application().Start(cmd_line=u'{app_path}')\n" \
            "pwa_window1 = app_pwa_window1.Dialog\n" \
            "pwa_window1.Wait('ready')\n" \
            "systabcontrol1 = pwa_window1.TabControl\n" \
            "systabcontrol1.Select('CTreeCtrl')\n\n" \
            "app_pwa_window1.Kill_()"

        path = (u'Common Controls Sample',

                u'CTreeCtrl, CAnimateCtrl, CToolBarCtrl, CDateTimeCtrl, '
                u'CMonthCalCtrl',

                u'CTreeCtrl',
                )

        with test_app("CmnCtrl1.exe") as (app, app_path):
            proxy_obj = get_proxy_object(None, path)
            code = proxy_obj.Get_code('Select')

        expected_code = expected_code.format(app_path=app_path)
        self.assertEquals(expected_code, code)

    def testToolbarWindow32Code(self):
        expected_code = \
            "from pywinauto.application import Application\n\n" \
            "app_pwa_window1 = Application().Start(cmd_line=u'{app_path}')\n" \
            "pwa_window1 = app_pwa_window1.Dialog\n" \
            "pwa_window1.Wait('ready')\n" \
            "toolbarwindow1 = pwa_window1.Toolbar2\n" \
            "pwa_toolbar_button1 = toolbarwindow1.Button('Line')\n" \
            "pwa_toolbar_button1.Click()\n\n" \
            "app_pwa_window1.Kill_()"

        path = (u'Common Controls Sample',

                u'Erase, Pencil, Select, Brush, Airbrush, Fill, Line, Select '
                u'Color, Magnify, Rectangle, Round Rect, Ellipse',

                u'Line',
                )

        with test_app("CmnCtrl1.exe") as (app, app_path):
            app.Dialog.TabControl.Select('CToolBarCtrl')  # open needed tab
            proxy_obj = get_proxy_object(None, path)
            code = proxy_obj.Get_code('Click')

        expected_code = expected_code.format(app_path=app_path)
        self.assertEquals(expected_code, code)
