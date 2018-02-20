import wx

import ui


def run():
    app = wx.App(False)
    ui.GomokuFrame(n=9)
    app.MainLoop()


if __name__ == '__main__':
    run()
