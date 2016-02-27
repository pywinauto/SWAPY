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

import string
import time
import unittest

from pywinauto import actionlogger
from PIL import ImageGrab

import code_manager
import const
import proxy
from sample_apps import test_app


actionlogger.enable()


class BaseTestCase(unittest.TestCase):

    def setUp(self):

        """
        Since the tests require different apps, use `with` statement instead.
        All setUp actions moved in the test_app contextmanager.
        """

        self.pwa_root = None

    def tearDown(self):

        """
        All app's tearDown moved into the test_app contextmanager.
        """

        code_manager.CodeManager().clear()  # Clear single tone CodeManager
        reload(code_manager)  # Reset class's counters
        reload(proxy)  # Reset class's counters
        del self.pwa_root

    def get_proxy_object(self, path):
        if self.pwa_root is None:
            self.pwa_root = proxy.PC_system(None)

        proxy_object = self.pwa_root
        for target_sub in path:
            subitems = proxy_object.get_subitems()
            if not subitems:
                raise RuntimeError("'%s' cannot be found" % target_sub)
            for name, pwa_object in subitems:
                if target_sub == name:
                    proxy_object = pwa_object
                    break
            else:
                raise RuntimeError("Invalid path, '%s' not found" % target_sub)

        return proxy_object


class ObjectBrowserTestCases(BaseTestCase):

    def tearDown(self):
        # ImageGrab.grab().save("scr%s.jpg" % time.time(), "JPEG")
        super(ObjectBrowserTestCases, self).tearDown()

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
            self.assertRaises(RuntimeError, self.get_proxy_object,
                              indirect_path)

            proxy_obj = self.get_proxy_object(direct_path)
            self.assertEqual(proxy_obj.pwa_obj.elem,
                             app.Dialog.TreeView.GetItem(['Birds']).elem)

    def testNestedTopWindow(self):

        path = (u'About RowList',
                u'RowList Version 1.0',
                )

        with test_app("RowList.exe") as (app, app_path):
            w = app['RowList Sample Application']
            # print time.time()
            w.Wait('ready')
            # print time.time()
            time.sleep(3)
            # print 1, app_path
            # print 2, w._menu_handle()
            # print 3, w.handle
            w.SetFocus()

            app['RowList Sample Application'].MenuItem(
                u'&Help->&About RowList...').Select()  # open About dialog
            try:
                proxy_obj = self.get_proxy_object(path)
            except RuntimeError:
                self.fail("Controls of a nested top window are not accessible")
            self.assertEqual(proxy_obj.pwa_obj.Texts(),
                             [u'RowList Version 1.0'])


class EmptyTextsTestCases(BaseTestCase):

    def testToolbarCode(self):
        expected_code = \
            "from pywinauto.application import Application\n\n" \
            "app = Application().Start(cmd_line=u'{app_path}')\n" \
            "{win_ident} = app[u'RowList Sample Application']\n" \
            "{win_ident}.Wait('ready')\n" \
            "toolbarwindow = {win_ident}[u'4']\n" \
            "toolbar_button = toolbarwindow.Button(9)\n" \
            "toolbar_button.Click()\n\n" \
            "app.Kill_()"

        path = (u'RowList Sample Application',
                u'Toolbar',
                u'button #9',
                )

        with test_app("RowList.exe") as (app, app_path):

            window = app.top_window_()

            class_name = window.GetProperties()['Class']
            crtl_class = filter(lambda c: c in string.ascii_letters,
                                class_name).lower()

            proxy_obj = self.get_proxy_object(path)
            code = proxy_obj.Get_code('Click')

        expected_code = expected_code.format(app_path=app_path,
                                             win_ident=crtl_class)
        self.assertEquals(expected_code, code)


class CodeGeneratorTestCases(BaseTestCase):

    def testInitAllParents(self):

        """
        all parents are inited after Get_code on a sub child.
        """

        expected_code = \
            "from pywinauto.application import Application\n\n" \
            "app = Application().Start(cmd_line=u'{app_path}')\n" \
            "window = app.Dialog\n" \
            "window.Wait('ready')\n" \
            "systreeview = window.TreeView\n" \
            "tree_item = systreeview.GetItem([u'Birds'])\n" \
            "tree_item.Expand()\n\n" \
            "app.Kill_()"

        path = (u'Common Controls Sample',
                u'Treeview1, Birds, Eagle, Hummingbird, Pigeon',
                u'Birds',
                )

        with test_app("CmnCtrl1.exe") as (app, app_path):
            proxy_obj = self.get_proxy_object(path)
            code = proxy_obj.Get_code('Expand')

        expected_code = expected_code.format(app_path=app_path)
        self.assertEquals(expected_code, code)

    def testChangeCodeStyle(self):

        """
        code style of a top window may be changed on fly
        """

        expected_code_connect = \
            "from pywinauto.application import Application\n\n" \
            "app = Application().Connect(title=u'Common Controls Sample', " \
            "class_name='#32770')\n" \
            "window = app.Dialog\n" \
            "systreeview = window.TreeView\n" \
            "tree_item = systreeview.GetItem([u'Birds'])\n" \
            "tree_item.Expand()\n\n"

        expected_code_start = \
            "from pywinauto.application import Application\n\n" \
            "app = Application().Start(cmd_line=u'{app_path}')\n" \
            "window = app.Dialog\n" \
            "window.Wait('ready')\n" \
            "systreeview = window.TreeView\n" \
            "tree_item = systreeview.GetItem([u'Birds'])\n" \
            "tree_item.Expand()\n\n" \
            "app.Kill_()"

        control_path = (u'Common Controls Sample',
                        u'Treeview1, Birds, Eagle, Hummingbird, Pigeon',
                        u'Birds',
                        )

        with test_app("CmnCtrl1.exe") as (app, app_path):
            proxy_obj = self.get_proxy_object(control_path)
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

    def testSecondAppCounter(self):

        """
        app counter increased for another window
        """

        expected_code_1app = \
            "from pywinauto.application import Application\n\n" \
            "app = Application().Start(cmd_line=u'{app_path1}')\n" \
            "window = app.Dialog\n" \
            "window.Wait('ready')\n" \
            "systreeview = window.TreeView\n" \
            "tree_item = systreeview.GetItem([u'Birds'])\n" \
            "tree_item.Expand()\n\n" \
            "app.Kill_()"

        expected_code_2apps = \
            "from pywinauto.application import Application\n\n" \
            "app = Application().Start(cmd_line=u'{app_path1}')\n" \
            "window = app.Dialog\n" \
            "window.Wait('ready')\n" \
            "systreeview = window.TreeView\n" \
            "tree_item = systreeview.GetItem([u'Birds'])\n" \
            "tree_item.Expand()\n\n" \
            "app2 = Application().Start(cmd_line=u'{app_path2}')\n" \
            "window2 = app2.Dialog\n" \
            "window2.Wait('ready')\n" \
            "menu_item = window2.MenuItem(u'&Help->&About mymenu...')\n" \
            "menu_item.Click()\n\n" \
            "app2.Kill_()\n" \
            "app.Kill_()"

        control_path_app1 = (u'Common Controls Sample',
                             u'Treeview1, Birds, Eagle, Hummingbird, Pigeon',
                             u'Birds',
                             )
        control_path_app2 = (u'BCDialogMenu',
                             u'!Menu',
                             u'&Help',
                             u'&Help submenu',
                             u'&About mymenu...'
                             )

        with test_app("CmnCtrl1.exe") as (app1, app_path1), \
                test_app("BCDialogMenu.exe") as (app2, app_path2):
            proxy_obj_app1 = self.get_proxy_object(control_path_app1)
            code_1app = proxy_obj_app1.Get_code('Expand')

            proxy_obj_app2 = self.get_proxy_object(control_path_app2)
            code_2apps = proxy_obj_app2.Get_code('Click')

        expected_code_1app = expected_code_1app.format(app_path1=app_path1)
        self.assertEquals(expected_code_1app, code_1app)

        expected_code_2apps = expected_code_2apps.format(app_path1=app_path1,
                                                         app_path2=app_path2)
        self.assertEquals(expected_code_2apps, code_2apps)


class VariableReuseTestCases(BaseTestCase):

    def testReuseVariable(self):

        """
        an object variable used again for a new action
        """

        expected_code = \
            "from pywinauto.application import Application\n\n" \
            "app = Application().Start(cmd_line=u'{app_path}')\n" \
            "window = app.Dialog\n" \
            "window.Wait('ready')\n" \
            "systreeview = window.TreeView\n" \
            "tree_item = systreeview.GetItem([u'Birds'])\n" \
            "tree_item.Expand()\n" \
            "tree_item.Click()\n\n" \
            "app.Kill_()"

        path = (u'Common Controls Sample',
                u'Treeview1, Birds, Eagle, Hummingbird, Pigeon',
                u'Birds',
                )

        with test_app("CmnCtrl1.exe") as (app, app_path):
            proxy_obj = self.get_proxy_object(path)
            proxy_obj.Get_code('Expand')  # First call
            code = proxy_obj.Get_code('Click')

        expected_code = expected_code.format(app_path=app_path)
        self.assertEquals(expected_code, code)

    def testSameAppAfterRefresh(self):

        """
        app & window counters do not increase after refresh for the same window
        """

        expected_code = \
            "from pywinauto.application import Application\n\n" \
            "app = Application().Start(cmd_line=u'{app_path}')\n" \
            "window = app.Dialog\n" \
            "window.Wait('ready')\n" \
            "window.Click()\n" \
            "window.Click()\n\n" \
            "app.Kill_()"

        control_path = (u'Common Controls Sample',
                        )

        with test_app("CmnCtrl1.exe") as (app, app_path):
            proxy_obj_before = self.get_proxy_object(control_path)
            _ = proxy_obj_before.Get_code('Click')

            # rebuild elements tree (refresh)
            proxy_obj_after = self.get_proxy_object(control_path)

            code = proxy_obj_after.Get_code('Click')

        self.assertTrue(proxy_obj_before is proxy_obj_after)

        expected_code = expected_code.format(app_path=app_path)
        self.assertEquals(expected_code, code)

    def testSameAppSecondWindow(self):

        """
        variable app reused for both windows of the same process
        """

        expected_code = \
            "from pywinauto.application import Application\n\n" \
            "app = Application().Start(cmd_line=u'{app_path}')\n" \
            "{win_ident} = app[u'RowList Sample Application']\n" \
            "{win_ident}.Wait('ready')\n" \
            "menu_item = {win_ident}.MenuItem(u'&Help->&About RowList...')\n" \
            "menu_item.Click()\n" \
            "window = app.Dialog\n" \
            "button = window.OK\n" \
            "button.Click()\n\n" \
            "app.Kill_()"

        path_main_window = (u'RowList Sample Application',

                            u'!Menu',
                            u'&Help',
                            u'&Help submenu',
                            u'&About RowList...',
                            )

        path_about_window = (u'About RowList',

                             u'OK',
                             )

        with test_app("RowList.exe") as (app, app_path):

            window = app.top_window_()
            class_name = window.GetProperties()['Class']
            crtl_class = filter(lambda c: c in string.ascii_letters,
                                class_name).lower()

            proxy_obj_main_window = self.get_proxy_object(path_main_window)
            proxy_obj_main_window.pwa_obj.Click()  # Click menu
            _ = proxy_obj_main_window.Get_code('Click')

            # new window
            proxy_obj_about_window = self.get_proxy_object(path_about_window)
            code = proxy_obj_about_window.Get_code('Click')

        expected_code = expected_code.format(app_path=app_path,
                                             win_ident=crtl_class)
        self.assertEquals(expected_code, code)


class ClearCommandsTestCases(BaseTestCase):

    def testClearLastCommand(self):

        """
        last command is cleared
        """

        expected_code_full = \
            "from pywinauto.application import Application\n\n" \
            "app = Application().Start(cmd_line=u'{app_path}')\n" \
            "window = app.Dialog\n" \
            "window.Wait('ready')\n" \
            "systabcontrol = window.TabControl\n" \
            "systabcontrol.Select(u'CTreeCtrl')\n\n" \
            "app.Kill_()"

        expected_code_cleared = \
            "from pywinauto.application import Application\n\n" \
            "app = Application().Start(cmd_line=u'{app_path}')\n" \
            "window = app.Dialog\n" \
            "window.Wait('ready')\n" \
            "systabcontrol = window.TabControl\n\n" \
            "app.Kill_()"

        path = (u'Common Controls Sample',

                u'CTreeCtrl, CAnimateCtrl, CToolBarCtrl, CDateTimeCtrl, '
                u'CMonthCalCtrl',

                u'CTreeCtrl',
                )

        with test_app("CmnCtrl1.exe") as (app, app_path):
            proxy_obj = self.get_proxy_object(path)
            code_full = proxy_obj.Get_code('Select')

            cm = code_manager.CodeManager()
            cm.clear_last()
            code_cleared = cm.get_full_code()

        expected_code_full = expected_code_full.format(app_path=app_path)
        self.assertEquals(expected_code_full, code_full)

        expected_code_cleared = expected_code_cleared.format(app_path=app_path)
        self.assertEquals(expected_code_cleared, code_cleared)

    def testClear2LastCommand(self):

        """
        last two commands are cleared
        """

        expected_code_full = \
            "from pywinauto.application import Application\n\n" \
            "app = Application().Start(cmd_line=u'{app_path}')\n" \
            "window = app.Dialog\n" \
            "window.Wait('ready')\n" \
            "systabcontrol = window.TabControl\n" \
            "systabcontrol.Select(u'CTreeCtrl')\n\n" \
            "app.Kill_()"

        expected_code_cleared = \
            "from pywinauto.application import Application\n\n" \
            "app = Application().Start(cmd_line=u'{app_path}')\n" \
            "window = app.Dialog\n" \
            "window.Wait('ready')\n\n" \
            "app.Kill_()"

        path = (u'Common Controls Sample',

                u'CTreeCtrl, CAnimateCtrl, CToolBarCtrl, CDateTimeCtrl, '
                u'CMonthCalCtrl',

                u'CTreeCtrl',
                )

        with test_app("CmnCtrl1.exe") as (app, app_path):
            proxy_obj = self.get_proxy_object(path)
            code_full = proxy_obj.Get_code('Select')

            cm = code_manager.CodeManager()
            cm.clear_last()
            cm.clear_last()
            code_cleared = cm.get_full_code()

        expected_code_full = expected_code_full.format(app_path=app_path)
        self.assertEquals(expected_code_full, code_full)

        expected_code_cleared = expected_code_cleared.format(app_path=app_path)
        self.assertEquals(expected_code_cleared, code_cleared)

    def testClearAll(self):

        """
        clear all the code
        """

        expected_code_full = \
            "from pywinauto.application import Application\n\n" \
            "app = Application().Start(cmd_line=u'{app_path}')\n" \
            "window = app.Dialog\n" \
            "window.Wait('ready')\n" \
            "systabcontrol = window.TabControl\n" \
            "systabcontrol.Select(u'CTreeCtrl')\n\n" \
            "app.Kill_()"

        path = (u'Common Controls Sample',

                u'CTreeCtrl, CAnimateCtrl, CToolBarCtrl, CDateTimeCtrl, '
                u'CMonthCalCtrl',

                u'CTreeCtrl',
                )

        with test_app("CmnCtrl1.exe") as (app, app_path):
            proxy_obj = self.get_proxy_object(path)
            code_full = proxy_obj.Get_code('Select')

            cm = code_manager.CodeManager()
            cm.clear()
            code_cleared = cm.get_full_code()

        expected_code_full = expected_code_full.format(app_path=app_path)
        self.assertEquals(expected_code_full, code_full)

        self.assertEquals("", code_cleared)

    def testReleaseVariable(self):

        """
        variable released while the clear and used again by other object
        """

        expected_code_button1 = \
            "from pywinauto.application import Application\n\n" \
            "app = Application().Start(cmd_line=u'{app_path}')\n" \
            "window = app.Dialog\n" \
            "window.Wait('ready')\n" \
            "button = window.CheckBox8\n" \
            "button.Click()\n\n" \
            "app.Kill_()"

        expected_code_button2 = \
            "from pywinauto.application import Application\n\n" \
            "app = Application().Start(cmd_line=u'{app_path}')\n" \
            "window = app.Dialog\n" \
            "window.Wait('ready')\n" \
            "button = window.CheckBox5\n" \
            "button.Click()\n\n" \
            "app.Kill_()"

        path_button1 = (u'Common Controls Sample',
                        u'TVS_CHECKBOXES',
                        )

        path_button2 = (u'Common Controls Sample',
                        u'TVS_DISABLEDRAGDROP',
                        )

        with test_app("CmnCtrl1.exe") as (app, app_path):
            proxy_obj_button1 = self.get_proxy_object(path_button1)
            code_button1 = proxy_obj_button1.Get_code('Click')

            cm = code_manager.CodeManager()
            cm.clear_last()

            proxy_obj_button2 = self.get_proxy_object(path_button2)
            code_button2 = proxy_obj_button2.Get_code('Click')

        expected_code_button1 = expected_code_button1.format(app_path=app_path)
        self.assertEquals(expected_code_button1, code_button1)

        expected_code_button2 = expected_code_button2.format(app_path=app_path)
        self.assertEquals(expected_code_button2, code_button2)


class ControlsCodeTestCases(BaseTestCase):

    def testComboBoxCode(self):
        expected_code = \
            "from pywinauto.application import Application\n\n" \
            "app = Application().Start(cmd_line=u'{app_path}')\n" \
            "window = app.Dialog\n" \
            "window.Wait('ready')\n" \
            "combobox = window.ComboBox\n" \
            "combobox.Select(u'Gray')\n\n" \
            "app.Kill_()"

        path = (u'Common Controls Sample',
                u'Gray, Gray, White, Black',
                u'Gray',
                )

        with test_app("CmnCtrl3.exe") as (app, app_path):
            proxy_obj = self.get_proxy_object(path)
            code = proxy_obj.Get_code('Select')

        expected_code = expected_code.format(app_path=app_path)
        self.assertEquals(expected_code, code)

    def testListBoxCode(self):
        expected_code = \
            "from pywinauto.application import Application\n\n" \
            "app = Application().Start(cmd_line=u'{app_path}')\n" \
            "window = app.Dialog\n" \
            "window.Wait('ready')\n" \
            "listbox = window.ListBox\n" \
            "listbox.Select(u'BCSS_IMAGE')\n\n" \
            "app.Kill_()"

        path = (u'Common Controls Sample',
                u'BCSS_NOSPLIT, BCSS_STRETCH, BCSS_ALIGNLEFT, BCSS_IMAGE',
                u'BCSS_IMAGE',
                )

        with test_app("CmnCtrl3.exe") as (app, app_path):
            app.Dialog.TabControl.Select('CSplitButton')  # open needed tab
            proxy_obj = self.get_proxy_object(path)
            code = proxy_obj.Get_code('Select')

        expected_code = expected_code.format(app_path=app_path)
        self.assertEquals(expected_code, code)

    def testMenuCode(self):
        expected_code = \
            "from pywinauto.application import Application\n\n" \
            "app = Application().Start(cmd_line=u'{app_path}')\n" \
            "window = app.Dialog\n" \
            "window.Wait('ready')\n" \
            "menu_item = window.MenuItem" \
            "(u'&Help->&About mymenu...')\n" \
            "menu_item.Click()\n\n" \
            "app.Kill_()"

        path = (u'BCDialogMenu',
                u'!Menu',
                u'&Help',
                u'&Help submenu',
                u'&About mymenu...'
                )

        with test_app("BCDialogMenu.exe") as (app, app_path):
            proxy_obj = self.get_proxy_object(path)
            code = proxy_obj.Get_code('Click')

        expected_code = expected_code.format(app_path=app_path)
        self.assertEquals(expected_code, code)

    def testSysListView32Code(self):
        expected_code = \
            "from pywinauto.application import Application\n\n" \
            "app = Application().Start(cmd_line=u'{app_path}')\n" \
            "{win_ident} = app[u'RowList Sample Application']\n" \
            "{win_ident}.Wait('ready')\n" \
            "syslistview = {win_ident}[u'1']\n" \
            "listview_item = syslistview.GetItem(u'Gray')\n" \
            "listview_item.Click()\n\n" \
            "app.Kill_()"

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

            proxy_obj = self.get_proxy_object(path)
            self.assertEquals(len(proxy_obj.pwa_obj.listview_ctrl.Items()), 56)
            code = proxy_obj.Get_code('Click')

        expected_code = expected_code.format(app_path=app_path,
                                             win_ident=crtl_class)
        self.assertEquals(expected_code, code)

    def testSysTabControl32Code(self):
        expected_code = \
            "from pywinauto.application import Application\n\n" \
            "app = Application().Start(cmd_line=u'{app_path}')\n" \
            "window = app.Dialog\n" \
            "window.Wait('ready')\n" \
            "systabcontrol = window.TabControl\n" \
            "systabcontrol.Select(u'CTreeCtrl')\n\n" \
            "app.Kill_()"

        path = (u'Common Controls Sample',

                u'CTreeCtrl, CAnimateCtrl, CToolBarCtrl, CDateTimeCtrl, '
                u'CMonthCalCtrl',

                u'CTreeCtrl',
                )

        with test_app("CmnCtrl1.exe") as (app, app_path):
            proxy_obj = self.get_proxy_object(path)
            code = proxy_obj.Get_code('Select')

        expected_code = expected_code.format(app_path=app_path)
        self.assertEquals(expected_code, code)

    def testToolbarWindow32Code(self):
        expected_code = \
            "from pywinauto.application import Application\n\n" \
            "app = Application().Start(cmd_line=u'{app_path}')\n" \
            "window = app.Dialog\n" \
            "window.Wait('ready')\n" \
            "toolbarwindow = window.Toolbar2\n" \
            "toolbar_button = toolbarwindow.Button(u'Line')\n" \
            "toolbar_button.Click()\n\n" \
            "app.Kill_()"

        path = (u'Common Controls Sample',

                u'Erase, Pencil, Select, Brush, Airbrush, Fill, Line, Select '
                u'Color, Magnify, Rectangle, Round Rect, Ellipse',

                u'Line',
                )

        with test_app("CmnCtrl1.exe") as (app, app_path):
            app.Dialog.TabControl.Select('CToolBarCtrl')  # open needed tab
            proxy_obj = self.get_proxy_object(path)
            code = proxy_obj.Get_code('Click')

        expected_code = expected_code.format(app_path=app_path)
        self.assertEquals(expected_code, code)
