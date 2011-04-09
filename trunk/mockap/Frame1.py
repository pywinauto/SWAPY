#Boa:Frame:Frame1

import wx
import module1

def create(parent):
    return Frame1(parent)

[wxID_FRAME1, wxID_FRAME1BUTTON1, wxID_FRAME1BUTTON2, wxID_FRAME1TEXTCTRL1, 
 wxID_FRAME1TREECTRL1, 
] = [wx.NewId() for _init_ctrls in range(5)]

class Frame1(wx.Frame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_FRAME1, name='', parent=prnt,
              pos=wx.Point(447, 168), size=wx.Size(818, 574),
              style=wx.DEFAULT_FRAME_STYLE | wx.TE_MULTILINE, title='Frame1')
        self.SetClientSize(wx.Size(810, 540))
        self.Bind(wx.EVT_CLOSE, self.OnFrame1Close)

        self.treeCtrl1 = wx.TreeCtrl(id=wxID_FRAME1TREECTRL1, name='treeCtrl1',
              parent=self, pos=wx.Point(16, 16), size=wx.Size(256, 384),
              style=wx.TR_HAS_BUTTONS)
        self.treeCtrl1.AddRoot('root')
        self.treeCtrl1.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK,
              self.OnTreeCtrl1TreeItemRightClick, id=wxID_FRAME1TREECTRL1)

        self.button1 = wx.Button(id=wxID_FRAME1BUTTON1, label='button1',
              name='button1', parent=self, pos=wx.Point(24, 424),
              size=wx.Size(75, 23), style=0)
        self.button1.Bind(wx.EVT_BUTTON, self.OnButton1Button,
              id=wxID_FRAME1BUTTON1)

        self.textCtrl1 = wx.TextCtrl(id=wxID_FRAME1TEXTCTRL1, name='textCtrl1',
              parent=self, pos=wx.Point(328, 24), size=wx.Size(432, 392),
              style=0, value='textCtrl1')

        self.button2 = wx.Button(id=wxID_FRAME1BUTTON2, label='button2',
              name='button2', parent=self, pos=wx.Point(24, 456),
              size=wx.Size(75, 23), style=0)
        self.button2.Bind(wx.EVT_BUTTON, self.OnButton2Button,
              id=wxID_FRAME1BUTTON2)

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.obj_brows = module1.Obj_browser()

    def OnButton1Button(self, event):
        pass

    def OnButton2Button(self, event):        
        proc_list = self.obj_brows.get_process()
        for proc in proc_list:
            item_data = wx.TreeItemData()
            item_data.SetData(proc)
            self.treeCtrl1.AppendItem(self.treeCtrl1.GetRootItem(),proc['name'],data = item_data)
            del item_data



    def OnTreeCtrl1TreeItemRightClick(self, event):
        self.textCtrl1.AppendText(str(self.treeCtrl1.GetItemData(self.treeCtrl1.GetSelection()).GetData()))

    def OnFrame1Close(self, event):
        del self.obj_brows
        self.Destroy()


