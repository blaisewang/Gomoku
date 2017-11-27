import wx

import gomoku.user_interface


def main():
    app = wx.App(False)
    gomoku.user_interface.GomokuFrame()
    app.MainLoop()


main()
