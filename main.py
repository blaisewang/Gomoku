import gomoku

import wx

if __name__ == '__main__':
    app = wx.App(False)
    gomoku.GomokuFrame()
    app.MainLoop()
