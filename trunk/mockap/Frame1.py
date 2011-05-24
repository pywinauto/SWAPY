#Boa:Frame:Frame1

import wx
import module1

def create(parent):
    return Frame1(parent)

[wxID_FRAME1, wxID_FRAME1BUTTON1, wxID_FRAME1BUTTON2, wxID_FRAME1STATICTEXT1, 
 wxID_FRAME1TEXTCTRL1, wxID_FRAME1TREECTRL1, 
] = [wx.NewId() for _init_ctrls in range(6)]

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
              name='button1', parent=self, pos=wx.Point(288, 24),
              size=wx.Size(75, 23), style=0)
        self.button1.Bind(wx.EVT_BUTTON, self.OnButton1Button,
              id=wxID_FRAME1BUTTON1)

        self.textCtrl1 = wx.TextCtrl(id=wxID_FRAME1TEXTCTRL1, name='textCtrl1',
              parent=self, pos=wx.Point(384, 16), size=wx.Size(416, 392),
              style=wx.TE_MULTILINE, value='textCtrl1')

        self.button2 = wx.Button(id=wxID_FRAME1BUTTON2, label='button2',
              name='button2', parent=self, pos=wx.Point(288, 56),
              size=wx.Size(75, 23), style=0)
        self.button2.Bind(wx.EVT_BUTTON, self.OnButton2Button,
              id=wxID_FRAME1BUTTON2)

        self.staticText1 = wx.StaticText(id=wxID_FRAME1STATICTEXT1,
              label='staticText1', name='staticText1', parent=self,
              pos=wx.Point(16, 408), size=wx.Size(256, 128), style=0)

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.obj_brows = module1.Obj_browser()

    def OnButton1Button(self, event):
        item_type = self.treeCtrl1.GetItemData(self.treeCtrl1.GetSelection()).GetData()['type']
        if item_type == 'proc':
            handle = self.treeCtrl1.GetItemData(self.treeCtrl1.GetSelection()).GetData()['data']['handle']
            self.textCtrl1.AppendText(str(self.obj_brows.get_children_list(handle)))
        else:
            pass
            
    def OnButton2Button(self, event):        
        proc_list = self.obj_brows.get_process()
        for proc in proc_list:
            item_data = wx.TreeItemData()
            item_data.SetData({'type' : 'proc', 'data' : proc})
            self.treeCtrl1.AppendItem(self.treeCtrl1.GetRootItem(),proc['name'],data = item_data)
            del item_data



    def OnTreeCtrl1TreeItemRightClick(self, event):
#        self.textCtrl1.AppendText(str(self.treeCtrl1.GetItemData(self.treeCtrl1.GetSelection()).GetData()))
 #       self.textCtrl1.AppendText(str(self.treeCtrl1.GetItemData(event.GetItem()).GetData()))
        tree_item = event.GetItem()
        item_type = self.treeCtrl1.GetItemData(tree_item).GetData()['type']
        if item_type == 'proc':
            handle = self.treeCtrl1.GetItemData(tree_item).GetData()['data']['handle']
            children = self.obj_brows.get_children_list(handle)        
            self.treeCtrl1.DeleteChildren(tree_item) #clear old
            for child in children:
                item_data = wx.TreeItemData()
                item_data.SetData({'type' : 'ctrl', 'data' : {'ctrl_handle':child['handle']}})
                self.treeCtrl1.AppendItem(tree_item,'%s - %.40s' % (str(child['wrap_name']),str(child['texts'])),data = item_data)
        else:
            ctrl_handle = self.treeCtrl1.GetItemData(tree_item).GetData()['data']['ctrl_handle']
            #prnt_handle = self.treeCtrl1.GetItemData(self.treeCtrl1.GetItemParent(tree_item)).GetData()['data']['handle']
            properties = self.obj_brows.get_properties(ctrl_handle)
            self.textCtrl1.AppendText(str(properties))

    def OnFrame1Close(self, event):
        del self.obj_brows
        self.Destroy()


