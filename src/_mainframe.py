#Boa:Frame:MainFrame

import wx

def create(parent):
    return Frame1(parent)

[wxID_FRAME1, wxID_FRAME1LISTBOX_PROPERTIES, wxID_FRAME1STATICBOX_EDITOR, 
 wxID_FRAME1STATICBOX_OBJECTSBROWSER, wxID_FRAME1STATICBOX_PROPRTIES, 
 wxID_FRAME1TEXTCTRL_EDITOR, wxID_FRAME1TREECTRL_OBJECTSBROWSER, 
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
        #self.treeCtrl_ObjectsBrowser.SetLabel('Shows windows, controls hierarchy')

        self.textCtrl_Editor = wx.TextCtrl(id=wxID_FRAME1TEXTCTRL_EDITOR,
              name='textCtrl_Editor', parent=self, pos=wx.Point(360, 20),
              size=wx.Size(330, 270), style=0, value='')
        #self.textCtrl_Editor.SetLabel('Code editor')

        self.listBox_Properties = wx.ListBox(choices=[],
              id=wxID_FRAME1LISTBOX_PROPERTIES, name='listBox_Properties',
              parent=self, pos=wx.Point(360, 320), size=wx.Size(330, 270),
              style=0)
        #self.listBox_Properties.SetLabel('Object properties')

    def __init__(self, parent):
        self._init_ctrls(parent)
