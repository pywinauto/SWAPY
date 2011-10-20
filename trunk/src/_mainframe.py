#Boa:Frame:MainFrame

import wx
import proxy
import exceptions

def create(parent):
    return Frame1(parent)

[wxID_FRAME1, wxID_FRAME1LISTBOX_PROPERTIES, wxID_FRAME1STATICBOX_EDITOR, 
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
              title='SWAPY - Simple Windows Automation on Python')
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
        self.Bind(wx.EVT_MENU, self.make_action) # - make action
        #self.treeCtrl_ObjectsBrowser.SetLabel('Shows windows, controls hierarchy')

        self.textCtrl_Editor = wx.TextCtrl(id=wxID_FRAME1TEXTCTRL_EDITOR,
              name='textCtrl_Editor', parent=self, pos=wx.Point(360, 20),
              size=wx.Size(330, 270), style=0, value='')
        
        #self.textCtrl_Editor.SetLabel('Code editor')

        self.listBox_Properties = wx.ListBox(choices=[],
              id=wxID_FRAME1LISTBOX_PROPERTIES, name='listBox_Properties',
              parent=self, pos=wx.Point(360, 320), size=wx.Size(330, 270),
              style=0)
        self.listBox_Properties.Bind(wx.EVT_LISTBOX_DCLICK, self.OnlistBox_Properties,
              id=wxID_FRAME1LISTBOX_PROPERTIES)
        #self.listBox_Properties.SetLabel('Object properties')

    def __init__(self, parent):
        self._init_ctrls(parent)
        self._refresh_windows_tree()        
        
    def OnlistBox_Properties(self, event):
        #event.Skip()
        print('test')
        self._refresh_windows_tree()
        
    def OnTreeCtrl1TreeSelChanged(self, event):
        the_root = self.treeCtrl_ObjectsBrowser.GetRootItem()
        tree_item = event.GetItem()
        parent_item = self.treeCtrl_ObjectsBrowser.GetItemParent(tree_item)
        parent_obj = self.treeCtrl_ObjectsBrowser.GetItemData(parent_item).GetData()
        obj = self.treeCtrl_ObjectsBrowser.GetItemData(tree_item).GetData()
        self._set_prorerties(parent_obj, obj)
        self._add_subitems(tree_item, obj)        
                    
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
        
    def make_action(self, event):
        tree_item = self.treeCtrl_ObjectsBrowser.GetSelection()
        obj = self.treeCtrl_ObjectsBrowser.GetItemData(tree_item).GetData()
        proxy.exec_action(obj, event.Id)
        
    def _refresh_windows_tree(self):
        self.treeCtrl_ObjectsBrowser.DeleteAllItems()
        #item_data = wx.TreeItemData()
        #item_data.SetData('root')
        #self.treeCtrl_ObjectsBrowser.AddRoot('PC name', data = item_data)
        self.treeCtrl_ObjectsBrowser.AddRoot('PC name')
        #del item_data
        the_root = self.treeCtrl_ObjectsBrowser.GetRootItem()
        for (w_title, w_obj) in proxy._get_windows():
            item_data = wx.TreeItemData()
            item_data.SetData(w_obj)
            self.treeCtrl_ObjectsBrowser.AppendItem(the_root,w_title,data = item_data)
            del item_data
        self.treeCtrl_ObjectsBrowser.Expand(self.treeCtrl_ObjectsBrowser.GetRootItem())
            
    def _set_prorerties(self, parent_obj, obj):
        self.listBox_Properties.Clear()        
        properties = proxy._get_properties(obj)
        properties.update(proxy._get_additional_properties(parent_obj, obj))
        param_names = properties.keys()
        param_names.sort(key=lambda name: name.lower())
        #print len(param_names)
        for p_name in param_names:
            p_name_str = str(p_name)
            try:
              p_values_str = str(properties[p_name])
            except exceptions.UnicodeEncodeError:
                p_values_str = properties[p_name].encode('unicode-escape', 'replace')
            item = '{0:30} {1:*^1} {2:30}'.format(p_name_str, ':',p_values_str)
            #item = '{0:30} {1:*^1} {2:30}'.format(str(p_name), ':',str(properties[p_name]))
            self.listBox_Properties.Append(item)
        
    def _add_subitems(self, tree_item, obj):
        self.treeCtrl_ObjectsBrowser.DeleteChildren(tree_item)
        subitems = proxy._get_subitems(obj)
        for i_name, i_obj in subitems:
            item_data = wx.TreeItemData()
            item_data.SetData(i_obj)
            self.treeCtrl_ObjectsBrowser.AppendItem(tree_item,i_name,data = item_data)  
            del item_data


