import wx

WIN_WIDTH = 1024
WIN_HEIGHT = 720
TEXT_WIDTH = 216
TEXT_HEIGHT = 26
BANNER_WIDTH = 300
BANNER_HEIGHT = 100
BLOCK_LENGTH = 42
HEIGHT_OFFSET = 50


def main():
    piece_radius = int(BLOCK_LENGTH / 2 - 3)
    inner_circle_radius = piece_radius - 4
    grid_length = BLOCK_LENGTH * 14
    grid_position_x = (WIN_WIDTH - grid_length) / 2
    grid_position_y = (WIN_HEIGHT - grid_length - HEIGHT_OFFSET) / 2

    line_list = []
    row_list = []
    column_list = []
    chess_record = []
    chess = [[0 for _ in range(23)] for _ in range(23)]
    row_name_list = ['15', '14', '13', '12', '11', '10', ' 9', ' 8', ' 7', ' 6', ' 5', ' 4', ' 3', ' 2', ' 1']
    column_name_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'O', 'P']

    move = 0
    winner = 0
    banner_displayed = 0

    def check_winner(x, y):
        win = "11111" if move % 2 == 1 else "22222"
        return win in "".join(map(str, [chess[i][y] for i in range(x - 4, x + 5)])) or win in "".join(
            map(str, [chess[x][i] for i in range(y - 4, y + 5)])) or win in "".join(
            map(str, [chess[x + i][y + i] for i in range(-4, 5)])) or win in "".join(
            map(str, [chess[x - i][y + i] for i in range(-4, 5)]))

    class Frame(wx.Frame):
        def __init__(self, title, width, height):
            screen_width = wx.DisplaySize()[0]
            screen_height = wx.DisplaySize()[1]
            for i in range(0, grid_length + 1, BLOCK_LENGTH):
                line_list.append(
                    (i + grid_position_x, grid_position_y, i + grid_position_x, grid_position_y + grid_length - 1))
                line_list.append(
                    (grid_position_x, i + grid_position_y, grid_position_x + grid_length - 1, i + grid_position_y))
                row_list.append((grid_position_x - 40, i + grid_position_y - 8))
                column_list.append((i + grid_position_x - 4, grid_position_y + grid_length + 25))
            wx.Frame.__init__(self, None, title=title, pos=((screen_width - width) / 2, (screen_height - height) / 2.5),
                              size=(width, height), style=wx.CLOSE_BOX)
            self.back_button = wx.Button(self, label="Back", pos=(48, grid_position_y))
            self.replay_button = wx.Button(self, label="Replay", pos=(48, grid_position_y + 40))
            self.back_button.Disable()
            self.replay_button.Disable()
            self.init_user_interface()

        def on_back_button_click(self, _):
            nonlocal move, winner
            move -= 1
            winner = 0
            x, y = chess_record.pop()
            chess[x][y] = 0
            self.draw_board()
            self.draw_chess()
            if move > 0:
                x, y = chess_record[move - 1]
                self.draw_current_chess(x, y)
            else:
                self.back_button.Disable()
                self.replay_button.Disable()

        def on_replay_button_click(self, _):
            nonlocal move, chess, winner
            move = 0
            winner = 0
            chess = [[0 for _ in range(23)] for _ in range(23)]
            chess_record.clear()
            self.draw_board()
            self.back_button.Disable()
            self.replay_button.Disable()

        def init_user_interface(self):
            self.Bind(wx.EVT_PAINT, self.on_paint)
            self.Bind(wx.EVT_LEFT_UP, self.on_click)
            self.Bind(wx.EVT_BUTTON, self.on_back_button_click, self.back_button)
            self.Bind(wx.EVT_BUTTON, self.on_replay_button_click, self.replay_button)
            self.Centre()
            self.Show(True)

        def on_paint(self, _):
            dc = wx.PaintDC(self)
            dc.SetBackground(wx.Brush(wx.WHITE_BRUSH))
            dc.Clear()
            self.draw_board()

        def draw_board(self):
            dc = wx.ClientDC(self)
            dc.SetPen(wx.Pen(wx.WHITE))
            dc.SetBrush(wx.Brush(wx.WHITE))
            dc.DrawRectangle(grid_position_x - BLOCK_LENGTH / 2, grid_position_y - BLOCK_LENGTH / 2,
                             grid_length + BLOCK_LENGTH, grid_length + BLOCK_LENGTH)
            dc.SetPen(wx.Pen(wx.BLACK, width=2))
            dc.DrawLineList(line_list)
            dc.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, False))
            dc.DrawTextList(row_name_list, row_list)
            dc.DrawTextList(column_name_list, column_list)
            dc.SetBrush(wx.Brush(wx.BLACK))
            dc.DrawCircle(grid_position_x + BLOCK_LENGTH * 3, grid_position_y + BLOCK_LENGTH * 3, 4)
            dc.DrawCircle(grid_position_x + BLOCK_LENGTH * 3, grid_position_y + BLOCK_LENGTH * 11, 4)
            dc.DrawCircle(grid_position_x + BLOCK_LENGTH * 7, grid_position_y + BLOCK_LENGTH * 7, 4)
            dc.DrawCircle(grid_position_x + BLOCK_LENGTH * 11, grid_position_y + BLOCK_LENGTH * 3, 4)
            dc.DrawCircle(grid_position_x + BLOCK_LENGTH * 11, grid_position_y + BLOCK_LENGTH * 11, 4)

        def draw_chess(self):
            dc = wx.ClientDC(self)
            for i in range(15):
                for j in range(15):
                    if chess[i + 4][j + 4] != 0:
                        dc.SetBrush(wx.Brush(wx.BLACK if chess[i + 4][j + 4] == 1 else wx.WHITE))
                        dc.DrawCircle(grid_position_x + i * BLOCK_LENGTH, grid_position_y + j * BLOCK_LENGTH,
                                      piece_radius)

        def draw_current_chess(self, x, y):
            x = grid_position_x + (x - 4) * BLOCK_LENGTH
            y = grid_position_y + (y - 4) * BLOCK_LENGTH
            dc = wx.ClientDC(self)
            dc.SetBrush(wx.Brush(wx.BLACK if move % 2 == 1 else wx.WHITE))
            dc.DrawCircle(x, y, piece_radius)
            dc.SetPen(wx.Pen(wx.WHITE if move % 2 == 1 else wx.BLACK))
            dc.DrawCircle(x, y, inner_circle_radius)

        def draw_banner(self):
            nonlocal banner_displayed
            string = ("BLACK" if winner == 1 else "WHITE") + " WIN"
            dc = wx.ClientDC(self)
            dc.SetBrush(wx.Brush(wx.WHITE))
            dc.DrawRectangle((WIN_WIDTH - BANNER_WIDTH) / 2, (WIN_HEIGHT - BANNER_HEIGHT) / 2 - HEIGHT_OFFSET + 5,
                             BANNER_WIDTH, BANNER_HEIGHT)
            dc.SetPen(wx.Pen(wx.BLACK))
            dc.SetFont(wx.Font(40, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, False))
            dc.DrawText(string, (WIN_WIDTH - TEXT_WIDTH) / 2, (WIN_HEIGHT - TEXT_HEIGHT) / 2 - HEIGHT_OFFSET)
            banner_displayed = 1

        def on_click(self, e):
            nonlocal winner, banner_displayed
            if winner == 0:
                nonlocal move
                x, y = e.GetPosition()
                x = x - grid_position_x + BLOCK_LENGTH / 2
                y = y - grid_position_y + BLOCK_LENGTH / 2
                if x > 0 and y > 0:
                    x = int(x / BLOCK_LENGTH) + 4
                    y = int(y / BLOCK_LENGTH) + 4
                    if 4 <= x < 19 and 4 <= y < 19:
                        if chess[x][y] == 0:
                            if move == 0:
                                self.back_button.Enable()
                                self.replay_button.Enable()
                            move += 1
                            chess[x][y] = 1 if move % 2 == 1 else 2
                            chess_record.append((x, y))
                            self.draw_chess()
                            self.draw_current_chess(x, y)
                            if move > 8:
                                if check_winner(x, y):
                                    winner = 1 if move % 2 == 1 else 2
                                    self.draw_banner()

            elif banner_displayed == 1:
                self.draw_board()
                self.draw_chess()
                banner_displayed = 0

    app = wx.App(False)
    Frame('Gomoku', WIN_WIDTH, WIN_HEIGHT)
    app.MainLoop()


main()
