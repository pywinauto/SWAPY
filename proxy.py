# GUI object/properties browser. 
# Copyright (C) 2011 Matiychuk D.
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

import exceptions
import platform
import os
import sys
import string
import time
import thread
import warnings

import pywinauto

from code_manager import CodeGenerator, check_valid_identifier
from const import *

'''
proxy module for pywinauto 
'''


pywinauto.timings.Timings.window_find_timeout = 1


def resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller >= 1.6
        ###os.chdir(sys._MEIPASS)
        filename = os.path.join(sys._MEIPASS, filename)
    elif '_MEIPASS2' in os.environ:
        # PyInstaller < 1.6 (tested on 1.5 only)
        ###os.chdir(os.environ['_MEIPASS2'])
        filename = os.path.join(os.environ['_MEIPASS2'], filename)
    else:
        ###os.chdir(sys.path.dirname(sys.argv[0]))
        filename = os.path.join(os.path.dirname(sys.argv[0]), filename)
    return filename


class PwaWrapper(object):

    """
    Base proxy class for pywinauto objects.
    """

    def __init__(self, pwa_obj, parent=None):
        '''
        Constructor
        '''
        #original pywinauto object
        self.pwa_obj = pwa_obj
        self.parent = parent
        default_sort_key = lambda name: name[0].lower()
        self.subitems_sort_key = default_sort_key

    def GetProperties(self):
        '''
        Return dict of original + additional properies
        Can be owerridden for non pywinauto obects
        '''
        properties = {}
        properties.update(self._get_properies())
        properties.update(self._get_additional_properties())
        return properties
        
    def Get_subitems(self):
        '''
        Return list of children - [(control_text, swapy_obj),...]
        Can be owerridden for non pywinauto obects
        '''
        subitems = []

        subitems += self._get_children()
        subitems += self._get_additional_children()

        subitems.sort(key=self.subitems_sort_key)
        #encode names
        subitems_encoded = []
        for (name, obj) in subitems:
            #name = name.encode('cp1251', 'replace')
            subitems_encoded.append((name, obj))
        return subitems_encoded
        
    def Exec_action(self, action):
        '''
        Execute action on the control
        '''
        #print('self.pwa_obj.'+action+'()')
        exec('self.pwa_obj.'+action+'()')
        return 0
        
    def Get_actions(self):

        """
        return allowed actions for this object. [(id,action_name),...]
        """

        allowed_actions = []
        try:
            obj_actions = dir(self.pwa_obj.WrapperObject())
        except:
            obj_actions = dir(self.pwa_obj)
        for _id, action in ACTIONS.items():
            if action in obj_actions:
                allowed_actions.append((_id, action))
        allowed_actions.sort(key=lambda name: name[1].lower())
        return allowed_actions

    def Get_extended_actions(self):

        """
        Extended actions
        """

        return []

    def Highlight_control(self): 
        if self._check_visibility():
          thread.start_new_thread(self._highlight_control,(3,))
        return 0

    def _get_properies(self):
        '''
        Get original pywinauto's object properties
        '''
        #print type(self.pwa_obj)
        try:
            properties = self.pwa_obj.GetProperties()
        except exceptions.RuntimeError:
            properties = {} #workaround
        return properties
        
    def _get_additional_properties(self):

        """
        Get additonal useful properties, like a handle, process ID, etc.
        Can be overridden by derived class
        """

        additional_properties = {}

        #-----Access names
        access_names = [name for name, obj in self.__get_uniq_names(target_control=self.pwa_obj)]
        if access_names:
            additional_properties.update({'Access names' : access_names})
        #-----
        
        #-----pwa_type
        additional_properties.update({'pwa_type' : str(type(self.pwa_obj))})
        #---
        
        #-----handle
        try:
            additional_properties.update({'handle' : str(self.pwa_obj.handle)})
        except:
            pass
        #---
        return additional_properties
        
    def _get_children(self):

        """
        Return original pywinauto's object children & names
        [(control_text, swapy_obj),...]
        """

        if self.pwa_obj.Parent():
            # Hide children of the non top level window control.
            # Expect all the children are accessible from the top level window.
            return []

        u_names = None
        children = []
        children_controls = self.pwa_obj.Children()
        for child_control in children_controls:
            try:
                texts = child_control.Texts()
            except exceptions.WindowsError:
                # texts = ['Unknown control name2!'] #workaround for
                # WindowsError: [Error 0] ...
                texts = None
            except exceptions.RuntimeError:
                # texts = ['Unknown control name3!'] #workaround for
                # RuntimeError: GetButtonInfo failed for button
                # with command id 256
                texts = None

            if texts:
                texts = filter(bool, texts)  # filter out '' and None items

            if texts:  # check again after the filtering
                title = ', '.join(texts)
            else:
                # .Texts() does not have a useful title, trying get it
                # from the uniqnames
                if u_names is None:
                    # init unames list
                    u_names = self.__get_uniq_names()

                child_uniq_name = [u_name for u_name, obj in u_names
                                   if obj.WrapperObject() == child_control]

                if child_uniq_name:
                    title = child_uniq_name[-1]
                else:
                    # uniqnames has no useful title
                    title = 'Unknown control name1!'
            children.append((title, self._get_swapy_object(child_control)))

        return children

    def _get_additional_children(self):
        '''
        Get additonal children, like for a menu, submenu, subtab, etc.
        Should be owerriden in derived classes of non standart pywinauto object
        '''
        return []
        
    def _get_pywinobj_type(self, obj):
        '''
        Check self pywinauto object type
        '''
        if type(obj) == pywinauto.application.WindowSpecification:
            return 'window'
        elif type(obj) == pywinauto.controls.menuwrapper.Menu:
            return 'menu'
        elif type(obj) == pywinauto.controls.menuwrapper.MenuItem:
            return 'menu_item'
        elif type(obj) == pywinauto.controls.win32_controls.ComboBoxWrapper:
            return 'combobox'
        elif type(obj) == pywinauto.controls.common_controls.ListViewWrapper:
            return 'listview'
        elif type(obj) == pywinauto.controls.common_controls.TabControlWrapper:
            return 'tab'
        elif type(obj) == pywinauto.controls.common_controls.ToolbarWrapper:
            return 'toolbar'
        elif type(obj) == pywinauto.controls.common_controls._toolbar_button:
            return 'toolbar_button'
        elif type(obj) == pywinauto.controls.common_controls.TreeViewWrapper:
            return 'tree_view'
        elif type(obj) == pywinauto.controls.common_controls._treeview_element:
            return 'tree_item'
        else:
            return 'unknown'
        
    def _get_swapy_object(self, pwa_obj):
        pwa_type = self._get_pywinobj_type(pwa_obj)
        #print pwa_type
        if pwa_type == 'window':
            return Pwa_window(pwa_obj, self)
        if pwa_type == 'menu':
            return Pwa_menu(pwa_obj, self)
        if pwa_type == 'menu_item':
            return Pwa_menu_item(pwa_obj, self)
        if pwa_type == 'combobox':
            return Pwa_combobox(pwa_obj, self)
        if pwa_type == 'listview':
            return Pwa_listview(pwa_obj, self)
        if pwa_type == 'tab':
            return Pwa_tab(pwa_obj, self)
        if pwa_type == 'toolbar':
            return Pwa_toolbar(pwa_obj, self)
        if pwa_type == 'toolbar_button':
            return Pwa_toolbar_button(pwa_obj, self)
        if pwa_type == 'tree_view':
            return Pwa_tree(pwa_obj, self)
        if pwa_type == 'tree_item':
            return Pwa_tree_item(pwa_obj, self)
        else:
            return SWAPYObject(pwa_obj, self)

    def _highlight_control(self, repeat = 1):
        while repeat > 0:
            repeat -= 1
            self.pwa_obj.DrawOutline('red', thickness=1)
            time.sleep(0.3)
            self.pwa_obj.DrawOutline(colour=0xffffff, thickness=1)
            time.sleep(0.2)
        return 0
        
    def _check_visibility(self):
        '''
        Check control/window visibility.
        Return pwa.IsVisible() or False if fails
        '''
        is_visible = False
        try:
            is_visible = self.pwa_obj.IsVisible()
        except:
            pass
        return is_visible
        
    def _check_actionable(self):
        '''
        Check control/window Actionable.
        Return True or False if fails
        '''
        try:
            self.pwa_obj.VerifyActionable()
        except:
            is_actionable = False
        else:
            is_actionable = True
        return is_actionable
        
    def _check_existence(self):
        '''
        Check control/window Exists.
        Return True or False if fails
        '''

        try:
            handle_ = self.pwa_obj.handle
            obj = pywinauto.application.WindowSpecification({'handle': handle_})
        except:
            is_exist = False
        else:
            is_exist = obj.Exists()
        return is_exist

    def __get_uniq_names(self, target_control=None):

        """
        Return uniq_names of the control
        [(uniq_name, obj), ]
        If target_control specified, apply additional filtering for obj == target_control
        """

        # TODO: cache this method

        pwa_app = pywinauto.application.Application()  # TODO: do not call .Application() everywhere.

        try:
            parent_obj = self.pwa_obj.TopLevelParent()
        except pywinauto.controls.HwndWrapper.InvalidWindowHandle:
            #For non visible windows
            #...
            #InvalidWindowHandle: Handle 0x262710 is not a vaild window handle
            parent_obj = self.pwa_obj
        except AttributeError:
            return []

        visible_controls = [pwa_app.window_(handle=ch) for ch in
                            pywinauto.findwindows.find_windows(parent=parent_obj.handle, top_level_only=False)]
        uniq_names_obj = [(uniq_name, obj) for uniq_name, obj
                      in pywinauto.findbestmatch.build_unique_dict(visible_controls).items()
                      if uniq_name != '' and (not target_control or obj.WrapperObject() == target_control)]
        return sorted(uniq_names_obj, key=lambda name_obj: len(name_obj[0]))  # sort by name


class SWAPYObject(PwaWrapper, CodeGenerator):

    """
    Mix the pywinauto wrapper and the codegenerator
    """

    code_self_pattern_attr = "{var} = {parent_var}.{access_name}"
    code_self_pattern_item = "{var} = {parent_var}['{access_name}']"
    code_action_pattern = "{var}.{action}()"
    main_parent_type = None

    def __init__(self, *args, **kwargs):
        super(SWAPYObject, self).__init__(*args, **kwargs)
        self.code_parents = self.get_code_parents()

    def get_code_parents(self):

        """
        Collect a list of all parents needed to access the control.
        Some parents may be excluded regarding to the `self.main_parent_type` parameter.
        """

        grab_all = True if not self.main_parent_type else False
        code_parents = []
        parent = self.parent
        while parent:
            if not grab_all and isinstance(parent, self.main_parent_type):
                grab_all = True

            if grab_all:
                code_parents.append(parent)
            parent = parent.parent
        return code_parents

    @property
    def _code_self(self):

        """
        Default _code_self.
        """
        #print self._get_additional_properties()
        access_name = self.GetProperties()['Access names'][0]
        if check_valid_identifier(access_name):
            # A valid identifier
            code = self.code_self_pattern_attr.format(access_name=access_name,
                                                      parent_var="{parent_var}",
                                                      var="{var}")
        else:
            #Not valid, encode and use as app's item.
            access_name = access_name.encode('unicode-escape', 'replace')
            code = self.code_self_pattern_item.format(access_name=access_name,
                                                      parent_var="{parent_var}",
                                                      var="{var}")
        return code

    @property
    def _code_action(self):

        """
        Default _code_action.
        """
        code = self.code_action_pattern
        return code

    @property
    def _code_close(self):

        """
        Default _code_close.
        """
        return ""

    @property
    def code_var_pattern(self):

        """
        Compose variable prefix, based on the control Class or SWAPY wrapper class name.
        """

        var_prefix = self.__class__.__name__.lower()
        if 'Class' in self.GetProperties():
            crtl_class = filter(lambda c: c in string.ascii_letters, self.GetProperties()['Class']).lower()
            if crtl_class:
                var_prefix = crtl_class

        return "{var_prefix}{id}".format(var_prefix=var_prefix,
                                         id="{id}")

    def SetCodestyle(self, extended_action_id):

        """
        Switch a control codestyle regarding extended_action_id
        """

        pass


class VirtualSWAPYObject(SWAPYObject):
    def __init__(self, parent, index):
        self.parent = parent
        self.index = index
        self.pwa_obj = self
        self._check_visibility = self.parent._check_visibility
        self._check_actionable = self.parent._check_actionable
        self._check_existence = self.parent._check_existence
        self.code_parents = self.get_code_parents()

    code_action_pattern = "{parent_var}.{action}({index})"

    @property
    def _code_self(self):

        """
        Rewrite default behavior.
        """
        return ""

    @property
    def _code_action(self):
        index = self.index
        if isinstance(index, unicode):
            index = "'%s'" % index.encode('unicode-escape', 'replace')
        code = self.code_action_pattern.format(index=index,
                                               action="{action}",
                                               var="{var}",
                                               parent_var="{parent_var}")
        return code

    @property
    def code_var_pattern(self):
        raise Exception('Must not be used "code_var_pattern" prop for a VirtualSWAPYObject')
        
    def Select(self):
        self.parent.pwa_obj.Select(self.index)

    def _get_properies(self):
        return {}
    
    def Get_subitems(self):
        return []
        
    def Highlight_control(self): 
        pass
        return 0

    
class PC_system(SWAPYObject):
    handle = 0

    # code_self_pattern = "{var} = pywinauto.application.Application()\n"

    @property
    def _code_self(self):
        # code = self.code_self_pattern.format(var="{var}")
        # return code
        return "from pywinauto.application import Application"
    #
    # @property
    # def code_var_pattern(self):
    #     return "app{id}".format(id="{id}")

    def Get_subitems(self):
        '''
        returns [(window_text, swapy_obj),...]
        '''
        #windows--------------------
        windows = []
        try_count = 3
        app = pywinauto.application.Application()
        for i in range(try_count):
          try:
            handles = pywinauto.findwindows.find_windows()
          except exceptions.OverflowError: # workaround for OverflowError: array too large
            time.sleep(1)
          except exceptions.MemoryError:# workaround for MemoryError
            time.sleep(1)
          else:
            break
        else:
          #TODO: add swapy exception: Could not get windows list
          handles = []
        #we have to find taskbar in windows list
        warnings.filterwarnings("ignore", category=FutureWarning) #ignore future warning in taskbar module
        from pywinauto import taskbar
        taskbar_handle = taskbar.TaskBarHandle()
        for w_handle in handles:
            wind = app.window_(handle=w_handle)
            if w_handle == taskbar_handle:
                title = 'TaskBar'
            else:
                texts = wind.Texts()
                texts = filter(bool, texts)  # filter out '' and None items
                if not texts:
                    title = 'Window#%s' % w_handle
                else:
                    title = ', '.join(texts)
            windows.append((title, self._get_swapy_object(wind)))
        windows.sort(key=lambda name: name[0].lower())
        #-----------------------
        
        #smt new----------------
        #------------------------
        return windows

    def _get_properies(self):
        info = {'Platform' : platform.platform(), \
                'Processor' : platform.processor(), \
                'PC name' : platform.node() }
                
        return info
        
    def Get_actions(self):
        '''
        No actions for PC_system
        '''
        return []

    def Highlight_control(self): 
        pass
        return 0
        
    def _check_visibility(self):
        return True
        
    def _check_actionable(self):
        return True
        
    def _check_existence(self):
        return True


class Pwa_window(SWAPYObject):
    code_self_pattern_attr = "{var} = app_{var}.{access_name}"
    code_self_pattern_item = "{var} = app_{var}['{access_name}']"
    code_self_close = "app_{var}.Kill_()"

    def __init__(self, *args, **kwargs):
        # Set default style
        self.code_self_style = self.__code_self_start
        self.code_close_style = self.__code_close_start
        return super(Pwa_window, self).__init__(*args, **kwargs)

    def __code_self_connect(self):
        title = self.pwa_obj.WindowText().encode('unicode-escape')
        cls_name = self.pwa_obj.Class()
        code = "\napp_{var} = Application().Connect(title=u'{title}', " \
               "class_name='{cls_name}')\n".format(title=title,
                                                   cls_name=cls_name,
                                                   var="{var}")
        return code

    def __code_self_start(self):
        target_pid = self.pwa_obj.ProcessID()
        cmd_line = None
        process_modules = pywinauto.application._process_get_modules_wmi()
        for pid, name, process_cmdline in process_modules:
            if pid == target_pid:
                cmd_line = os.path.normpath(process_cmdline)
                cmd_line = cmd_line.encode('unicode-escape')
                break
        code = "\napp_{var} = Application().Start(cmd_line=u'{cmd_line}')\n"\
            .format(cmd_line=cmd_line, var="{var}")
        return code

    def __code_close_connect(self):
        return ""

    def __code_close_start(self):
        return self.code_self_close.format(var="{var}")

    @property
    def _code_self(self):
        code = ""
        if not self._get_additional_properties()['Access names']:
            raise NotImplementedError
        else:
            code += self.code_self_style()
            code += super(Pwa_window, self)._code_self
            if self.code_self_style == self.__code_self_start:
                code += "\n{var}.Wait('ready')"

        return code

    @property
    def _code_close(self):

        """
        Rewrite default behavior.
        """

        code = self.code_close_style()

        return code

    def _get_additional_children(self):
        '''
        Add menu object as children
        '''
        additional_children = []
        menu = self.pwa_obj.Menu()
        if menu:
            menu_child = [('!Menu', self._get_swapy_object(menu))]
            additional_children += menu_child
        return additional_children

    def _get_additional_properties(self):
        '''
        Get additonal useful properties, like a handle, process ID, etc.
        Can be overridden by derived class
        '''
        additional_properties = {}
        pwa_app = pywinauto.application.Application()
        #-----Access names

        access_names = [name for name in pywinauto.findbestmatch.build_unique_dict([self.pwa_obj]).keys() if name != '']
        access_names.sort(key=len)
        additional_properties.update({'Access names': access_names})
        #-----

        #-----pwa_type
        additional_properties.update({'pwa_type': str(type(self.pwa_obj))})
        #---

        #-----handle
        try:
            additional_properties.update({'handle': str(self.pwa_obj.handle)})
        except:
            pass
        #---
        return additional_properties

    def Get_extended_actions(self):

        """
        Extended actions
        """

        return [(_id, action) for _id, action in EXTENDED_ACTIONS.items()]

    def SetCodestyle(self, extended_action_id):

        """
        Switch to `Start` or `Connect` code
        """

        if extended_action_id == 301:  # Start
            self.code_self_style = self.__code_self_start
            self.code_close_style = self.__code_close_start
        elif extended_action_id == 302:  # Connect
            self.code_self_style = self.__code_self_connect
            self.code_close_style = self.__code_close_connect
        else:
            raise RuntimeError("Unknown menu id - %s" % extended_action_id)

        if self.code_snippet is not None:
            # Refresh self code after the changing of the code style
            own_code_self = self.get_code_self()
            own_close_code = self.get_code_close()
            self.code_snippet.update(init_code=own_code_self,
                                     close_code=own_close_code)


class Pwa_menu(SWAPYObject):

    def _check_visibility(self):
        is_visible = False
        try:
            is_visible = self.pwa_obj.ctrl.IsVisible()
        except AttributeError:
            pass
        return is_visible
        
    def _check_actionable(self):
        if self.pwa_obj.accessible:
            return True
        else:
            return False
        
    def _check_existence(self):
        try:
            self.pwa_obj.ctrl.handle
        except:
            return False
        else:
            return True

    def _get_additional_children(self):
        '''
        Add submenu object as children
        '''
        #print(dir(self.pwa_obj))
        #print(self.pwa_obj.is_main_menu)
        #print(self.pwa_obj.owner_item)
        
        self.subitems_sort_key = lambda obj: obj[1].pwa_obj.Index() #sorts items by indexes

        if not self.pwa_obj.accessible:
            return []

        additional_children = []
        menu_items = self.pwa_obj.Items()
        for menu_item in menu_items:
            item_text = menu_item.Text()
            if not item_text:
                if menu_item.Type() == 2048:
                    item_text = '-----Separator-----'
                else:
                    item_text = 'Index: %d' % menu_item.Index()
            menu_item_child = [(item_text, self._get_swapy_object(menu_item))]
            additional_children += menu_item_child
        return additional_children
        
    def _get_children(self):
        '''
        Return original pywinauto's object children
        
        '''
        return []
        
    def Highlight_control(self): 
        pass
        return 0


class Pwa_menu_item(Pwa_menu):

    main_parent_type = Pwa_window
    code_self_pattern = "{var} = {main_parent_var}.MenuItem(u'{menu_path}')"

    @property
    def _code_self(self):
        menu_path = self.get_menuitems_path().encode('unicode-escape', 'replace')
        code = self.code_self_pattern.format(menu_path=menu_path,
                                             main_parent_var="{main_parent_var}",
                                             var="{var}")
        return code

    def _check_actionable(self):
        if self.pwa_obj.State() == 3: #grayed
            is_actionable = False
        else:
            is_actionable = True
        return is_actionable

    def _get_additional_children(self):
        '''
        Add submenu object as children
        '''
        #print(dir(self.pwa_obj))
        #print(self.pwa_obj.menu)
        #print self.get_menuitems_path()
        
        additional_children = []
        submenu = self.pwa_obj.SubMenu()
        if submenu:
            submenu_child = [(self.pwa_obj.Text()+' submenu', self._get_swapy_object(submenu))]
            additional_children += submenu_child
        return additional_children
        
    def get_menuitems_path(self):
        '''
        Compose menuitems_path for GetMenuPath. Example "#0 -> Save As", "Tools -> #0 -> Configure"
        '''
        path = []
        owner_item = self.pwa_obj
        
        while owner_item:
            text = owner_item.Text()
            if not text:
                text = '#%d' % owner_item.Index()
            path.append(text)
            menu = owner_item.menu
            owner_item = menu.owner_item
        return '->'.join(path[::-1])


class Pwa_combobox(SWAPYObject):

    def _get_additional_children(self):
        '''
        Add ComboBox items as children
        '''
        additional_children = []
        for i, text in enumerate(self.pwa_obj.ItemTexts()):
            if not text:
                text = "option #%s" % i
                additional_children.append((text,
                                            virtual_combobox_item(self, i)))
            else:
                additional_children.append((text,
                                            virtual_combobox_item(self, text)))
        return additional_children


class virtual_combobox_item(VirtualSWAPYObject):

    def _get_properies(self):
        index = None
        text = self.index
        for i, name in enumerate(self.parent.pwa_obj.ItemTexts()):
            if name == text:
                index = i
                break
        return {'Index': index, 'Text': text}


class Pwa_listview(SWAPYObject):
    def _get_additional_children(self):
        '''
        Add SysListView32 items as children
        '''
        additional_children = []
        for index in range(self.pwa_obj.ItemCount()):
            item = self.pwa_obj.GetItem(index)
        # for item in self.pwa_obj.Items():
        # Wait for the fix https://github.com/pywinauto/pywinauto/issues/97
            text = item['text']
            if not text:
                text = "option #%s" % index
            additional_children += [(text, listview_item(item, self))]
        return additional_children


class listview_item(SWAPYObject):

    code_self_pattern = "{var} = {parent_var}.GetItem('{index}')"

    @property
    def _code_self(self):
        code = self.code_self_pattern.format(index=self.pwa_obj.ItemData()['text'],
                                             parent_var="{parent_var}",
                                             var="{var}")
        return code

    def _get_properies(self):
        item_properties = {'index': self.pwa_obj.item_index}
        item_properties.update(self.pwa_obj.ItemData())
        return item_properties

    def _check_visibility(self):
        return True

    def _check_actionable(self):
        return True

    def _check_existence(self):
        return True

    def Get_subitems(self):
        return []

    def Highlight_control(self):
        pass
        return 0


class Pwa_tab(SWAPYObject):
    def _get_additional_children(self):

        """
        Add TabControl items as children
        """

        additional_children = []
        for index in range(self.pwa_obj.TabCount()):
            text = self.pwa_obj.GetTabText(index)
            if not text:
                text = "tab #%s" % index
            additional_children += [(text, virtual_tab_item(self, index))]
        return additional_children


class virtual_tab_item(VirtualSWAPYObject):

    @property
    def _code_action(self):
        index = self.parent.pwa_obj.GetTabText(self.index)
        if isinstance(index, unicode):
            index = "'%s'" % index.encode('unicode-escape', 'replace')
        code = self.code_action_pattern.format(index=index,
                                               action="{action}",
                                               var="{var}",
                                               parent_var="{parent_var}")
        return code

    def _get_properies(self):
        item_properties = {'Index' : self.index,
                           'Texts': self.parent.pwa_obj.GetTabText(self.index)}
        return item_properties


class Pwa_toolbar(SWAPYObject):

    def _get_additional_children(self):
        '''
        Add button objects as children
        '''
        additional_children = []
        buttons_count = self.pwa_obj.ButtonCount()
        for button_index in range(buttons_count):
            try:
                button = self.pwa_obj.Button(button_index)
                button_text = button.info.text
                if not button_text:
                    button_text = "button #%s" % button_index
                button_object = self._get_swapy_object(button)
            except exceptions.RuntimeError:
                #button_text = ['Unknown button name1!'] #workaround for RuntimeError: GetButtonInfo failed for button with index 0
                pass #ignore the button
            else:
                button_item = [(button_text, button_object)]
                additional_children += button_item
        return additional_children
        
    def _get_children(self):
        '''
        Return original pywinauto's object children
        
        '''
        return []


class Pwa_toolbar_button(SWAPYObject):

    code_self_pattern = "{var} = {parent_var}.Button({index})"

    @property
    def _code_self(self):
        text = self.pwa_obj.info.text
        if not text:
            index = self.pwa_obj.index
        else:
            index = text
        if isinstance(index, unicode):
            index = "'%s'" % index.encode('unicode-escape', 'replace')

        code = self.code_self_pattern.format(index=index,
                                             action="{action}",
                                             var="{var}",
                                             parent_var="{parent_var}")
        return code

    def _check_visibility(self):
        is_visible = False
        try:
            is_visible = self.pwa_obj.toolbar_ctrl.IsVisible()
        except:
            pass
        return is_visible
        
    def _check_actionable(self):
        try:
            self.pwa_obj.toolbar_ctrl.VerifyActionable()
        except:
            is_actionable = False
        else:
            is_actionable = True
        return is_actionable
        
    def _check_existence(self):
        try:
            handle_ = self.pwa_obj.toolbar_ctrl.handle
            obj = pywinauto.application.WindowSpecification({'handle': handle_})
        except:
            is_exist = False
        else:
            is_exist = obj.Exists()
        return is_exist
        
    def _get_children(self):
        return []
        
    def _get_properies(self):
        o = self.pwa_obj
        props = {'IsCheckable': o.IsCheckable(),
                 'IsChecked': o.IsChecked(),
                 'IsEnabled': o.IsEnabled(),
                 'IsPressable': o.IsPressable(),
                 'IsPressed': o.IsPressed(),
                 'Rectangle': o.Rectangle(),
                 'State': o.State(),
                 'Style': o.Style(),
                 'index': o.index,
                 'text': o.info.text}
        return props
        
    def Highlight_control(self): 
        pass
        return 0

        
class Pwa_tree(SWAPYObject):

    def _get_additional_children(self):
        '''
        Add roots object as children
        '''
        
        additional_children = []
        roots = self.pwa_obj.Roots()
        for root in roots:
            root_text = root.Text()
            obj = self._get_swapy_object(root)
            obj.path = [root_text]
            root_item = [(root_text, obj)]
            additional_children += root_item
        return additional_children
        
    def Highlight_control(self): 
        pass
        return 0


class Pwa_tree_item(SWAPYObject):

    main_parent_type = Pwa_tree
    code_self_pattern = "{var} = {main_parent_var}.GetItem({path})"

    @property
    def _code_self(self):
        path = self.path
        for i in range(len(path)):
            if isinstance(path[i], unicode):
                path[i] = '%s' % path[i].encode('unicode-escape', 'replace')

        code = self.code_self_pattern.format(path=path,
                                             var="{var}",
                                             main_parent_var="{main_parent_var}")
        return code

    def _get_properies(self):
        o = self.pwa_obj
        props = {'Rectangle' : o.Rectangle(),
                 'State' : o.State(),
                 'Text' : o.Text(),}
        return props

    def _check_visibility(self):
        return True
        # TODO: It seems like pywinauto bug
        #return self.pwa_obj.EnsureVisible()
        
    def _check_existence(self):
        return True
        
    def _check_actionable(self):
        if self.parent.pwa_obj != self.pwa_obj.tree_ctrl:
            # the parent is also tree item
            return self.parent.pwa_obj.IsExpanded()
        else:
            return True
        
    def _get_children(self):
        return []
        
    def Highlight_control(self): 
        pass
        return 0
    
    def _get_additional_children(self):
        '''
        Add sub tree items object as children
        '''
        
        additional_children = []
        sub_items = self.pwa_obj.Children()
        for item in sub_items:
            item_text = item.Text()
            obj = self._get_swapy_object(item)
            obj.path = self.path + [item_text]
            sub_item = [(item_text, obj)]
            additional_children += sub_item
        return additional_children
