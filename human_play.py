import wx

import ui


def run():
    app = wx.App(False)
    ui.GomokuFrame(n=15)
    app.MainLoop()


if __name__ == '__main__':
    run()
