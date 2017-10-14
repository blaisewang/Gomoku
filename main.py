import wx


def main():
    win_width = 1024
    win_height = 720
    block_length = 42
    grid_number = 15 - 1
    grid_length = block_length * grid_number
    grid_position_x = (win_width - grid_length) / 2
    grid_position_y = (win_height - grid_length - 40) / 2
    row_name_list = ['15', '14', '13', '12', '11', '10', ' 9', ' 8', ' 7', ' 6', ' 5', ' 4', ' 3', ' 2', ' 1']
    column_name_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'O', 'P']

    line_list = []
    column_list = []
    row_list = []
    for i in range(0, grid_length, block_length):
        line_list.append((i + grid_position_x, grid_position_y, i + grid_position_x, grid_position_y + grid_length - 1))
        line_list.append((grid_position_x, i + grid_position_y, grid_position_x + grid_length - 1, i + grid_position_y))
        row_list.append((grid_position_x - 25, i + grid_position_y - 8))
        column_list.append((i + grid_position_x - 4, grid_position_y + grid_length + 5))
    row_list.append((grid_position_x - 25, grid_length + grid_position_y - 8))
    column_list.append((grid_length + grid_position_x - 4, grid_position_y + grid_length + 5))

    class Frame(wx.Frame):
        def __init__(self, title, width, height):
            screen_width = wx.DisplaySize()[0]
            screen_height = wx.DisplaySize()[1]
            wx.Frame.__init__(self, None, title=title, pos=((screen_width - width) / 2, (screen_height - height) / 2.5),
                              size=(width, height), style=wx.CLOSE_BOX)
            self.init_user_interface()

        def init_user_interface(self):
            self.Bind(wx.EVT_PAINT, self.on_paint)
            self.Centre()
            self.Show(True)

        def on_paint(self, e):
            dc = wx.PaintDC(self)
            dc.SetBackground(wx.Brush(wx.WHITE_BRUSH))
            dc.Clear()
            dc.SetPen(wx.Pen(wx.BLACK, width=3))
            dc.DrawRectangle(grid_position_x, grid_position_y, grid_length, grid_length)
            dc.SetPen(wx.Pen(wx.BLACK, width=2))
            dc.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, False))
            dc.DrawLineList(line_list)
            dc.DrawTextList(row_name_list, row_list)
            dc.DrawTextList(column_name_list, column_list)
            dc.SetBrush(wx.Brush(wx.BLACK))
            dc.DrawCircle(grid_position_x + block_length * 3, grid_position_y + block_length * 3, 4)
            dc.DrawCircle(grid_position_x + block_length * 3, grid_position_y + block_length * 11, 4)
            dc.DrawCircle(grid_position_x + block_length * 7, grid_position_y + block_length * 7, 4)
            dc.DrawCircle(grid_position_x + block_length * 11, grid_position_y + block_length * 3, 4)
            dc.DrawCircle(grid_position_x + block_length * 11, grid_position_y + block_length * 11, 4)

    app = wx.App(False)
    Frame('Gomoku', win_width, win_height)
    app.MainLoop()


main()
