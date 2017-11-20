import wx

import ai

WIN_WIDTH = 1024
WIN_HEIGHT = 720
BLOCK_LENGTH = 42
HEIGHT_OFFSET = 50
BANNER_WIDTH = 300
BANNER_HEIGHT = 100


class GomokuFrame(wx.Frame):
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
    current_move = 0
    winner = 0
    is_banner_displayed = False

    def __init__(self):
        screen_width = wx.DisplaySize()[0]
        screen_height = wx.DisplaySize()[1]
        for i in range(0, self.grid_length + 1, BLOCK_LENGTH):
            self.line_list.append((i + self.grid_position_x, self.grid_position_y, i + self.grid_position_x,
                                   self.grid_position_y + self.grid_length - 1))
            self.line_list.append((self.grid_position_x, i + self.grid_position_y,
                                   self.grid_position_x + self.grid_length - 1, i + self.grid_position_y))
            self.row_list.append((self.grid_position_x - 40, i + self.grid_position_y - 8))
            self.column_list.append((i + self.grid_position_x - 4, self.grid_position_y + self.grid_length + 25))
        wx.Frame.__init__(self, None, title="Gomoku",
                          pos=((screen_width - WIN_WIDTH) / 2, (screen_height - WIN_HEIGHT) / 2.5),
                          size=(WIN_WIDTH, WIN_HEIGHT), style=wx.CLOSE_BOX)
        button_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, False)
        self.back_button = wx.Button(self, label="Back", pos=(14, self.grid_position_y), size=(72, 32))
        self.forward_button = wx.Button(self, label="Forward", pos=(92, self.grid_position_y), size=(72, 32))
        self.replay_button = wx.Button(self, label="Replay", pos=(14, self.grid_position_y + 45), size=(150, 32))
        self.ai_button = wx.Button(self, label="AI-play", pos=(14, self.grid_position_y + 90), size=(150, 32))
        self.back_button.SetFont(button_font)
        self.forward_button.SetFont(button_font)
        self.replay_button.SetFont(button_font)
        self.ai_button.SetFont(button_font)
        self.back_button.Disable()
        self.forward_button.Disable()
        self.replay_button.Disable()
        self.init_user_interface()

    def on_back_button_click(self, _):
        self.current_move -= 1
        self.winner = 0
        x, y = self.chess_record[self.current_move]
        self.chess[x][y] = 0
        ai.remove_move(x, y)
        self.draw_board()
        self.draw_chess()
        self.forward_button.Enable()
        if self.current_move == 0:
            self.back_button.Disable()
            self.replay_button.Disable()

    def on_forward_button_click(self, _):
        x, y = self.chess_record[self.current_move]
        self.current_move += 1
        self.chess[x][y] = 2 if self.current_move % 2 == 0 else 1
        ai.add_move(x, y)
        self.draw_board()
        self.draw_chess()
        self.back_button.Enable()
        self.replay_button.Enable()
        if self.current_move == self.move:
            self.forward_button.Disable()

    def on_replay_button_click(self, _):
        ai.initialize()
        ai.load_weight_dictionary()
        self.move = 0
        self.current_move = 0
        self.winner = 0
        self.chess = [[0 for _ in range(23)] for _ in range(23)]
        self.chess_record.clear()
        self.draw_board()
        self.back_button.Disable()
        self.forward_button.Disable()
        self.replay_button.Disable()
        self.ai_button.Enable()

    def on_ai_play_button_click(self, _):
        x, y = ai.play.next_move()
        ai.add_move(x, y)
        self.draw_move(x, y)
        if self.move == 255 or self.winner != 0:
            self.ai_button.Disable()

    def on_paint(self, _):
        dc = wx.PaintDC(self)
        dc.SetBackground(wx.Brush(wx.WHITE_BRUSH))
        dc.Clear()
        self.draw_board()

    def init_user_interface(self):
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_UP, self.on_click)
        self.Bind(wx.EVT_BUTTON, self.on_back_button_click, self.back_button)
        self.Bind(wx.EVT_BUTTON, self.on_forward_button_click, self.forward_button)
        self.Bind(wx.EVT_BUTTON, self.on_replay_button_click, self.replay_button)
        self.Bind(wx.EVT_BUTTON, self.on_ai_play_button_click, self.ai_button)
        self.Centre()
        self.Show(True)
        ai.load_weight_dictionary()

    def draw_board(self):
        dc = wx.ClientDC(self)
        dc.SetPen(wx.Pen(wx.WHITE))
        dc.SetBrush(wx.Brush(wx.WHITE))
        dc.DrawRectangle(self.grid_position_x - BLOCK_LENGTH, self.grid_position_y - BLOCK_LENGTH,
                         self.grid_length + BLOCK_LENGTH * 2, self.grid_length + BLOCK_LENGTH * 2)
        dc.SetPen(wx.Pen(wx.BLACK, width=2))
        dc.DrawLineList(self.line_list)
        dc.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, False))
        dc.DrawTextList(self.row_name_list, self.row_list)
        dc.DrawTextList(self.column_name_list, self.column_list)
        dc.SetBrush(wx.Brush(wx.BLACK))
        dc.DrawCircle(self.grid_position_x + BLOCK_LENGTH * 3, self.grid_position_y + BLOCK_LENGTH * 3, 4)
        dc.DrawCircle(self.grid_position_x + BLOCK_LENGTH * 3, self.grid_position_y + BLOCK_LENGTH * 11, 4)
        dc.DrawCircle(self.grid_position_x + BLOCK_LENGTH * 7, self.grid_position_y + BLOCK_LENGTH * 7, 4)
        dc.DrawCircle(self.grid_position_x + BLOCK_LENGTH * 11, self.grid_position_y + BLOCK_LENGTH * 3, 4)
        dc.DrawCircle(self.grid_position_x + BLOCK_LENGTH * 11, self.grid_position_y + BLOCK_LENGTH * 11, 4)

    def draw_chess(self):
        dc = wx.ClientDC(self)
        for i in range(15):
            for j in range(15):
                if self.chess[i + 4][j + 4]:
                    dc.SetBrush(wx.Brush(wx.BLACK if self.chess[i + 4][j + 4] == 1 else wx.WHITE))
                    dc.DrawCircle(self.grid_position_x + i * BLOCK_LENGTH, self.grid_position_y + j * BLOCK_LENGTH,
                                  self.piece_radius)
        if self.current_move > 0:
            x, y = self.chess_record[self.current_move - 1]
            x = self.grid_position_x + (x - 4) * BLOCK_LENGTH
            y = self.grid_position_y + (y - 4) * BLOCK_LENGTH
            dc.SetBrush(wx.Brush(wx.BLACK if self.current_move % 2 == 1 == 1 else wx.WHITE))
            dc.SetPen(wx.Pen(wx.WHITE if self.current_move % 2 == 1 else wx.BLACK))
            dc.DrawCircle(x, y, self.inner_circle_radius)

    def draw_banner(self):
        string = ("BLACK" if self.winner == 1 else "WHITE") + " WIN"
        dc = wx.ClientDC(self)
        dc.SetBrush(wx.Brush(wx.WHITE))
        dc.DrawRectangle((WIN_WIDTH - BANNER_WIDTH) / 2, (WIN_HEIGHT - BANNER_HEIGHT) / 2 - HEIGHT_OFFSET + 5,
                         BANNER_WIDTH, BANNER_HEIGHT)
        dc.SetPen(wx.Pen(wx.BLACK))
        dc.SetFont(wx.Font(40, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, False))
        dc.DrawText(string, (WIN_WIDTH - 216) / 2, (WIN_HEIGHT - 26) / 2 - HEIGHT_OFFSET)
        self.is_banner_displayed = True

    def draw_draw_banner(self):
        string = "DRAW"
        dc = wx.ClientDC(self)
        dc.SetBrush(wx.Brush(wx.WHITE))
        dc.DrawRectangle((WIN_WIDTH - BANNER_WIDTH) / 2, (WIN_HEIGHT - BANNER_HEIGHT) / 2 - HEIGHT_OFFSET + 5,
                         BANNER_WIDTH, BANNER_HEIGHT)
        dc.SetPen(wx.Pen(wx.BLACK))
        dc.SetFont(wx.Font(40, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, False))
        dc.DrawText(string, (WIN_WIDTH - 97) / 2, (WIN_HEIGHT - 26) / 2 - HEIGHT_OFFSET)
        self.is_banner_displayed = True

    def draw_move(self, x, y):
        if self.chess[x][y] == 0:
            if self.current_move == 0:
                self.back_button.Enable()
                self.replay_button.Enable()
            if self.current_move != self.move:
                for i in range(self.current_move, self.move):
                    self.chess_record.pop()
                self.forward_button.Disable()
            self.current_move += 1
            self.move = self.current_move
            current_player = 1 if self.move % 2 == 1 else 2
            self.chess[x][y] = current_player
            self.chess_record.append((x, y))
            self.draw_chess()
            if self.move > 8:
                if ai.is_win(x, y):
                    self.winner = current_player
                    self.draw_banner()
                else:
                    if self.move == 255:
                        self.draw_draw_banner()

    def on_click(self, e):
        if self.winner == 0:
            x, y = e.GetPosition()
            x = x - self.grid_position_x + BLOCK_LENGTH / 2
            y = y - self.grid_position_y + BLOCK_LENGTH / 2
            if x > 0 and y > 0:
                x = int(x / BLOCK_LENGTH) + 4
                y = int(y / BLOCK_LENGTH) + 4
                if 4 <= x < 19 and 4 <= y < 19:
                    ai.add_move(x, y)
                    self.draw_move(x, y)
        elif self.is_banner_displayed:
            self.draw_board()
            self.draw_chess()
            self.is_banner_displayed = False
