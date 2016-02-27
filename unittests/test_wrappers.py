# unit tests for SWAPY wrappers.
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


import unittest
import pywinauto
from sample_apps import test_app
import proxy


class WrappersTestCase(unittest.TestCase):

    def test_window(self):
        with test_app("CmnCtrl1.exe") as (app, app_path):
            obj = app.Dialog
            wrapper = proxy.SWAPYWrapper(obj, None)
        self.assertTrue(isinstance(wrapper, proxy.Pwa_window))
        self.assertTrue(issubclass(wrapper.__class__, proxy.SWAPYWrapper))
        self.assertTrue(isinstance(
                wrapper.pwa_obj,
                pywinauto.application.WindowSpecification))

    def test_menu(self):
        with test_app("BCDialogMenu.exe") as (app, app_path):
            obj = app.Dialog.Menu()
            wrapper = proxy.SWAPYWrapper(obj, None)
        self.assertTrue(isinstance(wrapper, proxy.Pwa_menu))
        self.assertTrue(issubclass(wrapper.__class__, proxy.SWAPYWrapper))
        self.assertTrue(isinstance(
                wrapper.pwa_obj,
                pywinauto.controls.menuwrapper.Menu))

    def test_menu_item(self):
        with test_app("BCDialogMenu.exe") as (app, app_path):
            obj = app.Dialog.MenuItem(u'&File')
            wrapper = proxy.SWAPYWrapper(obj, None)
        self.assertTrue(isinstance(wrapper, proxy.Pwa_menu_item))
        self.assertTrue(issubclass(wrapper.__class__, proxy.Pwa_menu))
        self.assertTrue(isinstance(
                wrapper.pwa_obj,
                pywinauto.controls.menuwrapper.MenuItem))

    def test_combobox(self):
        with test_app("CmnCtrl3.exe") as (app, app_path):
            obj = app.Dialog.ComboBox.Click()
            wrapper = proxy.SWAPYWrapper(obj, None)
        self.assertTrue(isinstance(wrapper, proxy.Pwa_combobox))
        self.assertTrue(issubclass(wrapper.__class__, proxy.SWAPYWrapper))
        self.assertTrue(isinstance(
                wrapper.pwa_obj,
                pywinauto.controls.win32_controls.ComboBoxWrapper))

    def test_listbox(self):
        with test_app("CmnCtrl3.exe") as (app, app_path):
            app.Dialog.TabControl.Select('CSplitButton')  # open needed tab
            obj = app.Dialog.ListBox.Click()
            wrapper = proxy.SWAPYWrapper(obj, None)
        self.assertTrue(isinstance(wrapper, proxy.Pwa_listbox))
        self.assertTrue(issubclass(wrapper.__class__, proxy.SWAPYWrapper))
        self.assertTrue(isinstance(
                wrapper.pwa_obj,
                pywinauto.controls.win32_controls.ListBoxWrapper))

    def test_listview(self):
        with test_app("RowList.exe") as (app, app_path):
            obj = app[u'RowList Sample Application'][u'1'].Click()
            wrapper = proxy.SWAPYWrapper(obj, None)
        self.assertTrue(isinstance(wrapper, proxy.Pwa_listview))
        self.assertTrue(issubclass(wrapper.__class__, proxy.SWAPYWrapper))
        self.assertTrue(isinstance(
                wrapper.pwa_obj,
                pywinauto.controls.common_controls.ListViewWrapper))

    def test_tab(self):
        with test_app("CmnCtrl1.exe") as (app, app_path):
            obj = app.Dialog.TabControl.Click()
            wrapper = proxy.SWAPYWrapper(obj, None)
        self.assertTrue(isinstance(wrapper, proxy.Pwa_tab))
        self.assertTrue(issubclass(wrapper.__class__, proxy.SWAPYWrapper))
        self.assertTrue(isinstance(
                wrapper.pwa_obj,
                pywinauto.controls.common_controls.TabControlWrapper))

    def test_toolbar(self):
        with test_app("RowList.exe") as (app, app_path):
            obj = app[u'RowList Sample Application'][u'4'].Click()
            wrapper = proxy.SWAPYWrapper(obj, None)
        self.assertTrue(isinstance(wrapper, proxy.Pwa_toolbar))
        self.assertTrue(issubclass(wrapper.__class__, proxy.SWAPYWrapper))
        self.assertTrue(isinstance(
                wrapper.pwa_obj,
                pywinauto.controls.common_controls.ToolbarWrapper))

    def test_toolbar_button(self):
        with test_app("RowList.exe") as (app, app_path):
            obj = app[u'RowList Sample Application'][u'4'].Button(0)
            wrapper = proxy.SWAPYWrapper(obj, None)
        self.assertTrue(isinstance(wrapper, proxy.Pwa_toolbar_button))
        self.assertTrue(issubclass(wrapper.__class__, proxy.SWAPYWrapper))
        self.assertTrue(isinstance(
                wrapper.pwa_obj,
                pywinauto.controls.common_controls._toolbar_button))

    def test_tree_view(self):
        with test_app("CmnCtrl1.exe") as (app, app_path):
            obj = app.Dialog.TreeView.Click()
            wrapper = proxy.SWAPYWrapper(obj, None)
        self.assertTrue(isinstance(wrapper, proxy.Pwa_tree))
        self.assertTrue(issubclass(wrapper.__class__, proxy.SWAPYWrapper))
        self.assertTrue(isinstance(
                wrapper.pwa_obj,
                pywinauto.controls.common_controls.TreeViewWrapper))

    def test_tree_item(self):
        with test_app("CmnCtrl1.exe") as (app, app_path):
            obj = app.Dialog.TreeView.GetItem([u'Birds'])
            wrapper = proxy.SWAPYWrapper(obj, None)
        self.assertTrue(isinstance(wrapper, proxy.Pwa_tree_item))
        self.assertTrue(issubclass(wrapper.__class__, proxy.SWAPYWrapper))
        self.assertTrue(isinstance(
                wrapper.pwa_obj,
                pywinauto.controls.common_controls._treeview_element))

    def test_unknown(self):
        with test_app("CmnCtrl1.exe") as (app, app_path):
            obj = app.Dialog[u'#32770'].Click()
            wrapper = proxy.SWAPYWrapper(obj, None)
        self.assertTrue(isinstance(wrapper, proxy.NativeObject))
        self.assertTrue(issubclass(wrapper.__class__, proxy.SWAPYWrapper))
        self.assertTrue(isinstance(
                wrapper.pwa_obj,
                pywinauto.controls.HwndWrapper.HwndWrapper))
