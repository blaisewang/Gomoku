from gomoku import user_interface

import wx

if __name__ == '__main__':
    app = wx.App(False)
    user_interface.GomokuFrame()
    app.MainLoop()
