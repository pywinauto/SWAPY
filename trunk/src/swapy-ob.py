#!/usr/bin/env python
#Boa:App:BoaApp

import wx

import _mainframe

modules ={'_mainframe': [0, '', '_mainframe.py'], 'proxy': [0, '', 'proxy.py']}

class BoaApp(wx.App):
    def OnInit(self):
        self.main = _mainframe.create(None)
        self.main.Show()
        self.SetTopWindow(self.main)
        return True

def main():
    application = BoaApp(0)
    application.MainLoop()



if __name__ == '__main__':
    main()
