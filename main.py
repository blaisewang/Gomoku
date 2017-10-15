import wx


def main():
    win_width = 1024
    win_height = 720
    banner_width = 300
    banner_height = 100
    text_width = 216
    text_height = 26
    block_length = 42
    height_offset = 50
    piece_radius = int(block_length / 2 - 3)
    inner_circle_radius = piece_radius - 4
    grid_length = block_length * 14
    grid_position_x = (win_width - grid_length) / 2
    grid_position_y = (win_height - grid_length - height_offset) / 2

    line_list = []
    row_list = []
    column_list = []
    row_name_list = ['15', '14', '13', '12', '11', '10', ' 9', ' 8', ' 7', ' 6', ' 5', ' 4', ' 3', ' 2', ' 1']
    column_name_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'O', 'P']

    winner = 0
    banner_displayed = 0
    current_player = 1
    current_chess = [[0 for _ in range(15)] for _ in range(15)]

    def check_winner(player, x, y):
        nonlocal winner
        x += 4
        y += 4
        win = "11111" if player == 1 else "-1-1-1-1-1"
        chess = [[0 for _ in range(23)] for _ in range(23)]
        for i in range(15):
            for j in range(15):
                chess[i + 4][j + 4] = current_chess[i][j]
        if win in "".join(map(str, [chess[i][y] for i in range(x - 4, x + 5)])) or win in "".join(
                map(str, [chess[x][i] for i in range(y - 4, y + 5)])) or win in "".join(
            map(str, [chess[x + i][y + i] for i in range(- 4, 5)])) or win in "".join(
            map(str, [chess[x - i][y + i] for i in range(- 4, 5)])):
            winner = player

    class Frame(wx.Frame):

        def __init__(self, title, width, height):
            screen_width = wx.DisplaySize()[0]
            screen_height = wx.DisplaySize()[1]
            for i in range(0, grid_length + 1, block_length):
                line_list.append(
                    (i + grid_position_x, grid_position_y, i + grid_position_x, grid_position_y + grid_length - 1))
                line_list.append(
                    (grid_position_x, i + grid_position_y, grid_position_x + grid_length - 1, i + grid_position_y))
                row_list.append((grid_position_x - 40, i + grid_position_y - 8))
                column_list.append((i + grid_position_x - 4, grid_position_y + grid_length + 25))
            wx.Frame.__init__(self, None, title=title, pos=((screen_width - width) / 2, (screen_height - height) / 2.5),
                              size=(width, height), style=wx.CLOSE_BOX)
            self.init_user_interface()

        def init_user_interface(self):
            self.Bind(wx.EVT_PAINT, self.on_paint)
            self.Bind(wx.EVT_LEFT_UP, self.on_click)
            self.Centre()
            self.Show(True)

        def on_paint(self, _):
            dc = wx.PaintDC(self)
            dc.SetBackground(wx.Brush(wx.WHITE_BRUSH))
            dc.Clear()
            dc.SetPen(wx.Pen(wx.BLACK, width=2))
            dc.DrawLineList(line_list)
            dc.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, False))
            dc.DrawTextList(row_name_list, row_list)
            dc.DrawTextList(column_name_list, column_list)
            dc.SetBrush(wx.Brush(wx.BLACK))
            dc.DrawCircle(grid_position_x + block_length * 3, grid_position_y + block_length * 3, 4)
            dc.DrawCircle(grid_position_x + block_length * 3, grid_position_y + block_length * 11, 4)
            dc.DrawCircle(grid_position_x + block_length * 7, grid_position_y + block_length * 7, 4)
            dc.DrawCircle(grid_position_x + block_length * 11, grid_position_y + block_length * 3, 4)
            dc.DrawCircle(grid_position_x + block_length * 11, grid_position_y + block_length * 11, 4)

        def paint_chess(self):
            dc = wx.ClientDC(self)
            for i in range(15):
                for j in range(15):
                    if current_chess[i][j] != 0:
                        dc.SetBrush(wx.Brush(wx.BLACK if current_chess[i][j] == 1 else wx.WHITE))
                        dc.DrawCircle(grid_position_x + i * block_length, grid_position_y + j * block_length,
                                      piece_radius)

        def paint_current_chess(self, player, x, y):
            x = grid_position_x + x * block_length
            y = grid_position_y + y * block_length
            dc = wx.ClientDC(self)
            dc.SetBrush(wx.Brush(wx.BLACK if player == 1 else wx.WHITE))
            dc.DrawCircle(x, y, piece_radius)
            dc.SetPen(wx.Pen(wx.WHITE if player == 1 else wx.BLACK))
            dc.DrawCircle(x, y, inner_circle_radius)

        def paint_winner(self):
            nonlocal banner_displayed
            string = ("BLACK" if winner == 1 else "WHITE") + " WIN"
            dc = wx.ClientDC(self)
            dc.SetBrush(wx.Brush(wx.WHITE))
            dc.DrawRectangle((win_width - banner_width) / 2, (win_height - banner_height) / 2 - height_offset + 5,
                             banner_width, banner_height)
            dc.SetPen(wx.Pen(wx.BLACK))
            dc.SetFont(wx.Font(40, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, False))
            dc.DrawText(string, (win_width - text_width) / 2, (win_height - text_height) / 2 - height_offset)
            banner_displayed = 1

        def on_click(self, e):
            nonlocal banner_displayed
            if winner == 0:
                nonlocal current_player
                x, y = e.GetPosition()
                x = x - grid_position_x + block_length / 2
                y = y - grid_position_y + block_length / 2
                if x > 0 and y > 0:
                    x = int(x / block_length)
                    y = int(y / block_length)
                    if 0 <= x < 15 and 0 <= y < 15:
                        if current_chess[x][y] == 0:
                            current_chess[x][y] = current_player
                            check_winner(current_player, x, y)
                            self.paint_chess()
                            self.paint_current_chess(current_player, x, y)
                            current_player = -current_player
                            if winner != 0:
                                self.paint_winner()
            elif banner_displayed == 1:
                self.ClearBackground()
                self.paint_chess()
                banner_displayed = 0

    app = wx.App(False)
    Frame('Gomoku', win_width, win_height)
    app.MainLoop()


main()
