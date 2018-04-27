import sys

import wx

import ui


def run(n: int):
    app = wx.App(False)
    ui.GomokuFrame(n=n)
    app.MainLoop()


if __name__ == '__main__':
    length = sys.argv[1]
    if length.isdigit():
        run(int(length))
