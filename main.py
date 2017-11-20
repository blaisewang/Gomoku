import wx

import gomoku.user_interface

if __name__ == '__main__':
    app = wx.App(False)
    gomoku.user_interface.GomokuFrame()
    app.MainLoop()
