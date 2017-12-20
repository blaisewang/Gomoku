import wx

import ai.user_interface


def main():
    app = wx.App(False)
    ai.user_interface.GomokuFrame()
    app.MainLoop()


main()
