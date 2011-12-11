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

#Boa:Frame:MainFrame

import wx
import proxy
import exceptions
import const

def create(parent):
    return Frame1(parent)

[wxID_FRAME1, wxID_FRAME1LISTCTRL1_PROPERTIES, wxID_FRAME1STATICBOX_EDITOR, 
 wxID_FRAME1STATICBOX_OBJECTSBROWSER, wxID_FRAME1STATICBOX_PROPRTIES, 
 wxID_FRAME1TEXTCTRL_EDITOR, wxID_FRAME1TREECTRL_OBJECTSBROWSER
] = [wx.NewId() for _init_ctrls in range(7)]

class Frame1(wx.Frame):
    """
    Main application frame
    """
        
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_FRAME1, name='', parent=prnt,
              pos=wx.Point(563, 129), size=wx.Size(708, 634),
              style=wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN,
              title='SWAPY - Simple Windows Automation on Python. v %s' % const.VERSION)
        self.SetIcon(wx.Icon(proxy.resource_path("swapy_dog_head.ico"),
              wx.BITMAP_TYPE_ICO))
        self.SetClientSize(wx.Size(700, 600))

        self.staticBox_ObjectsBrowser = wx.StaticBox(id=wxID_FRAME1STATICBOX_OBJECTSBROWSER,
              label='Objects browser', name='staticBox_ObjectsBrowser',
              parent=self, pos=wx.Point(5, 5), size=wx.Size(340, 590), style=0)

        self.staticBox_Editor = wx.StaticBox(id=wxID_FRAME1STATICBOX_EDITOR,
              label='Editor', name='staticBox_Editor', parent=self,
              pos=wx.Point(355, 5), size=wx.Size(340, 290), style=0)

        self.staticBox_Proprties = wx.StaticBox(id=wxID_FRAME1STATICBOX_PROPRTIES,
              label='Properties', name='staticBox_Proprties', parent=self,
              pos=wx.Point(355, 305), size=wx.Size(340, 290), style=0)

        self.treeCtrl_ObjectsBrowser = wx.TreeCtrl(id=wxID_FRAME1TREECTRL_OBJECTSBROWSER,
              name='treeCtrl_ObjectsBrowser', parent=self, pos=wx.Point(10, 20),
              size=wx.Size(330, 570), style=wx.TR_HAS_BUTTONS)
        self.treeCtrl_ObjectsBrowser.Bind(wx.EVT_TREE_SEL_CHANGED,
              self.OnTreeCtrl1TreeSelChanged, id=wxID_FRAME1TREECTRL_OBJECTSBROWSER)
        self.treeCtrl_ObjectsBrowser.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.ObjectsBrowserRight_Click)
        self.Bind(wx.EVT_MENU, self.menu_action) # - make action
        #self.treeCtrl_ObjectsBrowser.SetLabel('Shows windows, controls hierarchy')

        self.textCtrl_Editor = wx.TextCtrl(id=wxID_FRAME1TEXTCTRL_EDITOR,
              name='textCtrl_Editor', parent=self, pos=wx.Point(360, 20),
              size=wx.Size(330, 270), style=wx.TE_MULTILINE | wx.TE_READONLY, value='')
        
        #self.textCtrl_Editor.SetLabel('Code editor')

        self.listCtrl_Properties = wx.ListCtrl(id=wxID_FRAME1LISTCTRL1_PROPERTIES, name='listCtrl1_Properties',
              parent=self, pos=wx.Point(360, 320), size=wx.Size(330, 270),
              style=wx.LC_REPORT)
        self.listCtrl_Properties.InsertColumn(col=0, format=wx.LIST_FORMAT_LEFT,
              heading='Property', width=-1)
        self.listCtrl_Properties.InsertColumn(col=1, format=wx.LIST_FORMAT_LEFT,
              heading='Value', width=-1)
        self.listCtrl_Properties.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK,
              self.OnlistCtrl_PropertiesListItemRightClick, id=wxID_FRAME1LISTCTRL1_PROPERTIES)
        self.listCtrl_Properties.Bind(wx.EVT_LEFT_DCLICK, self.Fefresh, id=wxID_FRAME1LISTCTRL1_PROPERTIES)

    def __init__(self, parent):
        self._init_ctrls(parent)
        self._refresh_windows_tree()   
        self.textCtrl_Editor.AppendText('import pywinauto\n\n')
        self.textCtrl_Editor.AppendText('pwa_app = pywinauto.application.Application()\n')
        

    def OnTreeCtrl1TreeSelChanged(self, event):
        #the_root = self.treeCtrl_ObjectsBrowser.GetRootItem()
        tree_item = event.GetItem()
        #parent_item = self.treeCtrl_ObjectsBrowser.GetItemParent(tree_item)
        #parent_obj = self.treeCtrl_ObjectsBrowser.GetItemData(parent_item).GetData()
        obj = self.treeCtrl_ObjectsBrowser.GetItemData(tree_item).GetData()
        #self._set_prorerties(parent_obj, obj)
        self._set_prorerties(obj)
        if type(obj) != proxy.SysInfo:            #should be removed windows are children of the PC item!
            self._add_subitems(tree_item, obj)
            proxy.highlight_control(obj)
                    
    def ObjectsBrowserRight_Click(self, event):
        menu = wx.Menu()
        #tree_item = self.treeCtrl_ObjectsBrowser.GetSelection()
        tree_item = event.GetItem()
        self.treeCtrl_ObjectsBrowser.SelectItem(tree_item)
        obj = self.treeCtrl_ObjectsBrowser.GetItemData(tree_item).GetData()
        for id, action_name in proxy._get_actions(obj):
            menu.Append(id, action_name)
        self.PopupMenu(menu)     
        menu.Destroy() 
    
    def OnlistCtrl_PropertiesListItemRightClick(self, event):
        self.GLOB_prop_item_index = event.GetIndex()
        menu = wx.Menu()
        menu.Append(201, 'Copy all')
        menu.AppendSeparator()
        menu.Append(202, 'Copy property')
        menu.Append(203, 'Copy value')
        self.PopupMenu(menu)     
        menu.Destroy() 
    
    def Fefresh(self, event):
        self._refresh_windows_tree()
    
    def menu_action(self, event):
        id = event.Id
        #print id
        if 99 < id < 200:
            #object browser menu
            self.make_action(id)
        elif 199 < id < 300:
            #properties viewer menu
            self.clipboard_action(id)
        else:
            #Unknown menu id
            pass
    
    def clipboard_action(self, menu_id):
        item = self.GLOB_prop_item_index
        clipdata = wx.TextDataObject()
        if menu_id == 201:
            all_texts = ''
            items_count = self.listCtrl_Properties.GetItemCount()
            for i in range(items_count):
                prop_name = self.listCtrl_Properties.GetItem(i, 0).GetText()
                val_name = self.listCtrl_Properties.GetItem(i, 1).GetText()
                all_texts += '%s : %s' % (prop_name, val_name) + '\n'
            clipdata.SetText(all_texts)
        elif menu_id == 202:
            property = self.listCtrl_Properties.GetItem(item,0).GetText()
            clipdata.SetText(property)
        elif menu_id == 203:
            value = self.listCtrl_Properties.GetItem(item,1).GetText()
            clipdata.SetText(value)
        else:
            #Unknow id
            pass
        self.GLOB_prop_item_index = None
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipdata)
        wx.TheClipboard.Close()
    
    
    def make_action(self, menu_id):
        tree_item = self.treeCtrl_ObjectsBrowser.GetSelection()
        obj = self.treeCtrl_ObjectsBrowser.GetItemData(tree_item).GetData()
        self.textCtrl_Editor.AppendText(proxy.get_code(obj, menu_id))
        proxy.exec_action(obj, menu_id)
        
    def _refresh_windows_tree(self):
        self.treeCtrl_ObjectsBrowser.DeleteAllItems()
        item_data = wx.TreeItemData()
        item_data.SetData(proxy.SysInfo())
        self.treeCtrl_ObjectsBrowser.AddRoot(proxy.SysInfo().GetProperties()['PC name'], data = item_data)
        #self.treeCtrl_ObjectsBrowser.AddRoot('PC name')
        del item_data
        the_root = self.treeCtrl_ObjectsBrowser.GetRootItem()
        for (w_title, w_obj) in proxy._get_windows():
            #print w_title
            sub_item_data = wx.TreeItemData()
            sub_item_data.SetData(w_obj)
            self.treeCtrl_ObjectsBrowser.AppendItem(the_root,w_title,data = sub_item_data)
            #self.textCtrl_Editor.AppendText(w_title)
            del sub_item_data
        self.treeCtrl_ObjectsBrowser.Expand(self.treeCtrl_ObjectsBrowser.GetRootItem())
            
    def _set_prorerties(self, obj):
        #self.listBox_Properties.Clear()
        self.listCtrl_Properties.DeleteAllItems()
        properties = proxy._get_properties(obj)
        properties.update(proxy._get_additional_properties(obj))
        param_names = properties.keys()
        param_names.sort(key=lambda name: name.lower(), reverse=True)
        #print len(param_names)
        for p_name in param_names:
            p_name_str = str(p_name)
            #if type(properties[p_name]) == list:
            #    p_values_str = unicode(', '.join(map(unicode ,properties[p_name])))
            #else:
            p_values_str = unicode(properties[p_name])
             
            '''
            try:
              p_values_str = str(properties[p_name])
            except exceptions.UnicodeEncodeError:
                p_values_str = properties[p_name].encode('', 'replace')
            '''
            index = self.listCtrl_Properties.InsertStringItem(0, p_name_str)
            self.listCtrl_Properties.SetStringItem(index, 1, p_values_str)
            #self.textCtrl_Editor.AppendText(p_values_str)
        
    def _add_subitems(self, tree_item, obj):
        self.treeCtrl_ObjectsBrowser.DeleteChildren(tree_item)
        subitems = proxy._get_subitems(obj)
        for i_name, i_obj in subitems:
            item_data = wx.TreeItemData()
            item_data.SetData(i_obj)
            self.treeCtrl_ObjectsBrowser.AppendItem(tree_item,i_name,data = item_data)  
            del item_data


