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

import pywinauto
import time
import wx
import thread
import exceptions
import platform
from const import *

'''
proxy module for pywinauto 
'''


pywinauto.timings.Timings.window_find_timeout = 1            

def resource_path(relative):
    import os
    return os.path.join(
        os.environ.get(
            "_MEIPASS2",
            os.path.abspath(".")
        ),
        relative
    )

class SWAPYObject(object):
    '''
    Base proxy class for pywinauto objects.
    
    '''
    def __init__(self, pwa_obj):
        '''
        Constructor
        '''
        #original pywinauto object
        self.pwa_obj = pwa_obj
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
        children = []
        children += self._get_children()
        for control in children:
            try:
                texts = control.Texts()
            except exceptions.RuntimeError:
                texts = ['Unknow control name2!'] #workaround
            while texts.count(''):
                texts.remove('')
            c_name = ', '.join(texts)
            if not c_name:
                c_name = 'Unknow control name1!'
            c_name_str = unicode(c_name)
            subitems.append((c_name_str, self._get_swapy_object(control)))
        subitems += self._get_additional_children()
        subitems.sort(key=self.subitems_sort_key)
        return subitems
        
    def Exec_action(self, action_id):
        '''
        Execute action on the control
        '''
        action = ACTIONS[action_id]
        #print('self.pwa_obj.'+action+'()')
        exec('self.pwa_obj.'+action+'()')
        return 0
        
    def Get_actions(self):
        '''
        return allowed actions for this object. [(id,action_name),...]
        '''
        allowed_actions = []
        try:
            obj_actions = dir(self.pwa_obj.WrapperObject())
        except:
            obj_actions = dir(self.pwa_obj)
        for id, action in ACTIONS.items():
            if action in obj_actions:
                allowed_actions.append((id,action))
        allowed_actions.sort(key=lambda name: name[1].lower())
        return allowed_actions
        
    def Get_code(self, action_id):
        '''
        Generate code for pywinauto module
        '''
        action = ACTIONS[action_id]
        if self._get_pywinobj_type(self.pwa_obj) == 'window':
            code = "\
w_handle = pywinauto.findwindows.find_windows(title_re=u'"+ self.pwa_obj.WindowText().encode('unicode-escape', 'replace') +"', class_name='"+ self.pwa_obj.Class() +"')[0]\n\
window = pwa_app.window_(handle=w_handle)\n\
window."+action+"()\n\
"
        else:
            code = "\
window['"+self._get_additional_properties()['Access names'][0]+"']."+action+"()\n\
"
        return code
        
    def Highlight_control(self): 
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
        '''
        Get additonal useful properties, like a handle, process ID, etc.
        Can be overridden by derived class
        '''
        additional_properties = {}
        #-----Access names
        try:
            parent_obj = self.pwa_obj.Parent()
        except:
            pass
        else:
            try:
                all_controls = parent_obj.Children()
            except:
                pass
            else:
                access_names = []
                uniq_names = pywinauto.findbestmatch.build_unique_dict(all_controls)
                for uniq_name, obj in uniq_names.items():
                    if uniq_name != '' and obj == self.pwa_obj:
                      access_names.append(uniq_name)
                access_names.sort(key=len)
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
        '''
        Return original pywinauto's object children
        
        '''
        return self.pwa_obj.Children()
        
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
        elif 1==0:
            return 'other'
        else:
            return 'unknown'
        
    def _get_swapy_object(self, pwa_obj):
        pwa_type = self._get_pywinobj_type(pwa_obj)
        #print pwa_type
        if pwa_type == 'smt_NEW':
            return smt_NEW(pwa_obj)
        if pwa_type == 'window':
            return Pwa_window(pwa_obj)
        if pwa_type == 'menu':
            return Pwa_menu(pwa_obj)
        if pwa_type == 'menu_item':
            return Pwa_menu_item(pwa_obj)
        else:
            return SWAPYObject(pwa_obj)
            
    def _highlight_control(self, repeat = 1):
        while repeat > 0:
            repeat -= 1
            self.pwa_obj.DrawOutline('red', thickness=1)
            time.sleep(0.3)
            self.pwa_obj.DrawOutline(colour=0xffffff, thickness=1)
            time.sleep(0.2)
        return 0
        
class PC_system(SWAPYObject):
    handle = 0
    
    def Get_subitems(self):
        '''
        returns [(window_text, swapy_obj),...]
        '''
        windows = []
        app = pywinauto.application.Application()
        handles = pywinauto.findwindows.find_windows(title_re='.*')
        for w_handle in handles:
            wind = app.window_(handle=w_handle)
            texts = wind.Texts()
            while texts.count(''):
              texts.remove('')
            title = ', '.join(texts)
            if not title:
                title = 'Unknow title!'
            title = unicode(title)
            windows.append((title, self._get_swapy_object(wind)))
        windows.sort(key=lambda name: name[0].lower())
        return windows

    def GetProperties(self):
        info = { 'Platform' : platform.platform(), \
                'Processor' : platform.processor(), \
                'PC name' : platform.node() }
                
        return info
        
    def Exec_action(self, action_id):
        '''
        Execute action on the control
        '''
        action = ACTIONS[action_id]
        exec('self.pwa_obj.'+action+'()')
        return 0
        
    def Get_actions(self):
        '''
        No actions for PC_system
        '''
        return []
        
    def Get_code(self, action_id):
        '''
        No code for PC_system
        '''
        return ''
        
    def Highlight_control(self): 
        pass
        return 0

class Pwa_window(SWAPYObject):
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
        
class Pwa_menu(SWAPYObject):

    def _get_additional_children(self):
        '''
        Add submenu object as children
        '''
        #print(dir(self.pwa_obj))
        #print(self.pwa_obj.is_main_menu)
        #print(self.pwa_obj.owner_item)
        
        self.subitems_sort_key = lambda obj: obj[1].pwa_obj.Index() #sorts items by indexes
        additional_children = []
        menu_items = self.pwa_obj.Items()
        for menu_item in menu_items:
            item_text = menu_item.Text()
            if item_text == '':
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
        
    def Get_code(self, action_id):
        '''
        Generate code for pywinauto module
        '''
        action = ACTIONS[action_id]
        code = "\
window.MenuItem(u'"+self.get_menuitems_path().encode('unicode-escape', 'replace')+"')."+action+"()\n\
"
        return code
        
        