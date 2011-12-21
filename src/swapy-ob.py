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

#Boa:App:BoaApp

import wx

import _mainframe

modules ={'_mainframe': [0, '', '_mainframe.py'], 'proxy': [0, '', 'proxy.py']}

class BoaApp(wx.App):
    def OnInit(self):
        self.main = _mainframe.create(None)
        self.main.Center()
        self.main.Show()
        self.SetTopWindow(self.main)
        return True

def main():
    application = BoaApp(0)
    application.MainLoop()



if __name__ == '__main__':
    main()
