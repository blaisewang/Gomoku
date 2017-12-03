import threading

import wx

import ai
import ai.play
import ai.evaluate

WIN_WIDTH = 1024
WIN_HEIGHT = 720
BLOCK_LENGTH = 42
HEIGHT_OFFSET = 50
BANNER_WIDTH = 300
BANNER_HEIGHT = 100
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 32
BUTTON_WIDTH_MARGIN = 6
BUTTON_HEIGHT_MARGIN = 45
ROW_LIST_MARGIN = 40
COLUMN_LIST_MARGIN = 25


class GomokuFrame(wx.Frame):
    piece_radius = int(BLOCK_LENGTH / 2 - 3)
    inner_circle_radius = piece_radius - 4
    grid_length = BLOCK_LENGTH * 14
    grid_position_x = (WIN_WIDTH - grid_length) / 2 + 10
    grid_position_y = (WIN_HEIGHT - grid_length - HEIGHT_OFFSET) / 2
    half_button_width = (BUTTON_WIDTH - BUTTON_WIDTH_MARGIN) / 2
    button_position_x = (grid_position_x - ROW_LIST_MARGIN - BUTTON_WIDTH) / 2
    second_button_position_x = button_position_x + half_button_width + BUTTON_WIDTH_MARGIN

    line_list = []
    row_list = []
    column_list = []
    chess_record = []
    row_name_list = ['15', '14', '13', '12', '11', '10', ' 9', ' 8', ' 7', ' 6', ' 5', ' 4', ' 3', ' 2', ' 1']
    column_name_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'O', 'P']

    moves = 0
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
            self.row_list.append((self.grid_position_x - ROW_LIST_MARGIN, i + self.grid_position_y - 8))
            self.column_list.append(
                (i + self.grid_position_x - 4, self.grid_position_y + self.grid_length + COLUMN_LIST_MARGIN))

        wx.Frame.__init__(self, None, title="Gomoku",
                          pos=((screen_width - WIN_WIDTH) / 2, (screen_height - WIN_HEIGHT) / 2.5),
                          size=(WIN_WIDTH, WIN_HEIGHT), style=wx.CLOSE_BOX)
        button_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, False)
        self.back_button = wx.Button(self, label="Back", pos=(self.button_position_x, self.grid_position_y),
                                     size=(self.half_button_width, BUTTON_HEIGHT))
        self.forward_button = wx.Button(self, label="Forward",
                                        pos=(self.second_button_position_x, self.grid_position_y),
                                        size=(self.half_button_width, BUTTON_HEIGHT))
        self.replay_button = wx.Button(self, label="Replay",
                                       pos=(self.button_position_x, self.grid_position_y + BUTTON_HEIGHT_MARGIN),
                                       size=(BUTTON_WIDTH, BUTTON_HEIGHT))
        self.ai_play_button = wx.Button(self, label="AI-play",
                                        pos=(self.button_position_x, self.grid_position_y + 2 * BUTTON_HEIGHT_MARGIN),
                                        size=(BUTTON_WIDTH, BUTTON_HEIGHT))
        self.back_button.SetFont(button_font)
        self.forward_button.SetFont(button_font)
        self.replay_button.SetFont(button_font)
        self.ai_play_button.SetFont(button_font)
        self.back_button.Disable()
        self.forward_button.Disable()
        self.replay_button.Disable()
        self.init_user_interface()

    def on_back_button_click(self, _):
        self.current_move -= 1
        ai.winner = 0
        x, y = self.chess_record[self.current_move]
        ai.remove_move(y, x)
        self.draw_board()
        self.draw_chess()
        self.ai_play_button.Enable()
        self.forward_button.Enable()
        if self.current_move == 0:
            self.back_button.Disable()
            self.replay_button.Disable()

    def on_forward_button_click(self, _):
        x, y = self.chess_record[self.current_move]
        self.current_move += 1
        ai.add_move(y, x)
        self.draw_board()
        self.draw_chess()
        self.back_button.Enable()
        self.replay_button.Enable()
        if self.current_move == self.moves:
            self.forward_button.Disable()
        if self.current_move == 255:
            self.ai_play_button.Disable()

    def on_replay_button_click(self, _):
        ai.initialize()
        self.moves = 0
        self.current_move = 0
        self.chess_record.clear()
        self.draw_board()
        self.back_button.Disable()
        self.forward_button.Disable()
        self.replay_button.Disable()
        self.ai_play_button.Enable()

    def on_ai_play_button_click(self, _):
        x, y = ai.play.next_move(False)
        ai.add_move(x, y)
        self.draw_move(y, x)
        if ai.moves == 255 or ai.winner != 0:
            self.ai_play_button.Disable()

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
        self.Bind(wx.EVT_BUTTON, self.on_ai_play_button_click, self.ai_play_button)
        self.Centre()
        self.Show(True)
        if not ai.load_training_data():
            self.ai_play_button.Disable()
        ai.initialize()

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
                if ai.chess[j + 4][i + 4]:
                    dc.SetBrush(wx.Brush(wx.BLACK if ai.chess[j + 4][i + 4] == 1 else wx.WHITE))
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
        string = ("BLACK" if ai.winner == 1 else "WHITE") + " WIN"
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
        if self.current_move == 0:
            self.back_button.Enable()
            self.replay_button.Enable()
        if self.current_move != self.moves:
            for i in range(self.current_move, self.moves):
                self.chess_record.pop()
            self.forward_button.Disable()
        self.current_move += 1
        self.moves = self.current_move
        self.chess_record.append((x, y))
        self.draw_chess()
        if self.moves > 8:
            ai.has_winner(y, x)
            if ai.winner != 0:
                self.draw_banner()
            else:
                if self.moves == 255:
                    self.draw_draw_banner()

    def on_click(self, e):
        if ai.winner == 0:
            x, y = e.GetPosition()
            x = x - self.grid_position_x + BLOCK_LENGTH / 2
            y = y - self.grid_position_y + BLOCK_LENGTH / 2
            if x > 0 and y > 0:
                x = int(x / BLOCK_LENGTH) + 4
                y = int(y / BLOCK_LENGTH) + 4
                if 4 <= x < 19 and 4 <= y < 19:
                    if ai.chess[y][x] == 0:
                        ai.add_move(y, x)
                        self.draw_move(x, y)
                        thread = threading.Thread(target=ai.q_matrix_thread, args=((y, x),))
                        thread.setDaemon(True)
                        thread.start()
                        thread.join()
        elif self.is_banner_displayed:
            self.draw_board()
            self.draw_chess()
            self.is_banner_displayed = False
