import copy
import pickle
import threading

import wx

from game import Board
from mcts_alphaZero import MCTSPlayer
from policy_value_net_numpy import PolicyValueNetNumpy

WIN_WIDTH = 1024
WIN_HEIGHT = 720
BLOCK_LENGTH = 42
HEIGHT_OFFSET = 50
BANNER_WIDTH = 300
BANNER_HEIGHT = 100
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 32
STANDARD_LENGTH = 15
ROW_LIST_MARGIN = 40
COLUMN_LIST_MARGIN = 25
BUTTON_WIDTH_MARGIN = 6
BUTTON_HEIGHT_MARGIN = 45


class GomokuFrame(wx.Frame):
    moves = 0
    current_move = 0
    has_set_ai_player = False
    is_banner_displayed = False
    is_analysis_displayed = False

    piece_radius = int(BLOCK_LENGTH / 2 - 3)
    inner_circle_radius = piece_radius - 4
    half_button_width = (BUTTON_WIDTH - BUTTON_WIDTH_MARGIN) / 2

    mcts_player = None

    line_list = []
    row_list = []
    column_list = []
    chess_record = []
    row_name_list = ['15', '14', '13', '12', '11', '10', ' 9', ' 8', ' 7', ' 6', ' 5', ' 4', ' 3', ' 2', ' 1']
    column_name_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'O', 'P']

    def __init__(self, n: int):
        if 8 <= n <= STANDARD_LENGTH:
            self.n = n
        else:
            raise Exception('Illegal Parameter N')

        self.thread = threading.Thread()
        self.board = Board(n)
        self.row_name_list = self.row_name_list[STANDARD_LENGTH - n: STANDARD_LENGTH]
        self.column_name_list = self.column_name_list[0:n]
        self.grid_length = BLOCK_LENGTH * (n - 1)
        self.grid_position_x = (WIN_WIDTH - self.grid_length) / 2 + 15
        self.grid_position_y = (WIN_HEIGHT - self.grid_length - HEIGHT_OFFSET) / 2
        self.button_position_x = (self.grid_position_x - ROW_LIST_MARGIN - BUTTON_WIDTH) / 2
        self.second_button_position_x = self.button_position_x + self.half_button_width + BUTTON_WIDTH_MARGIN

        for i in range(0, self.grid_length + 1, BLOCK_LENGTH):
            self.line_list.append((i + self.grid_position_x, self.grid_position_y, i + self.grid_position_x,
                                   self.grid_position_y + self.grid_length - 1))
            self.line_list.append((self.grid_position_x, i + self.grid_position_y,
                                   self.grid_position_x + self.grid_length - 1, i + self.grid_position_y))
            self.row_list.append((self.grid_position_x - ROW_LIST_MARGIN, i + self.grid_position_y - 8))
            self.column_list.append(
                (i + self.grid_position_x, self.grid_position_y + self.grid_length + COLUMN_LIST_MARGIN))

        wx.Frame.__init__(self, None, title="Gomoku",
                          pos=((wx.DisplaySize()[0] - WIN_WIDTH) / 2, (wx.DisplaySize()[1] - WIN_HEIGHT) / 2.5),
                          size=(WIN_WIDTH, WIN_HEIGHT), style=wx.CLOSE_BOX)
        button_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, False)
        image_font = wx.Font(25, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, False)
        self.back_button = wx.Button(self, label="Back", pos=(self.button_position_x, self.grid_position_y),
                                     size=(self.half_button_width, BUTTON_HEIGHT))
        self.forward_button = wx.Button(self, label="Forward",
                                        pos=(self.second_button_position_x, self.grid_position_y),
                                        size=(self.half_button_width, BUTTON_HEIGHT))
        self.replay_button = wx.Button(self, label="Replay",
                                       pos=(self.button_position_x, self.grid_position_y + BUTTON_HEIGHT_MARGIN),
                                       size=(BUTTON_WIDTH, BUTTON_HEIGHT))
        self.black_button = wx.Button(self, label="●",
                                      pos=(self.button_position_x, self.grid_position_y + 2 * BUTTON_HEIGHT_MARGIN),
                                      size=(self.half_button_width, BUTTON_HEIGHT))
        self.white_button = wx.Button(self, label="○",
                                      pos=(
                                          self.second_button_position_x,
                                          self.grid_position_y + 2 * BUTTON_HEIGHT_MARGIN),
                                      size=(self.half_button_width, BUTTON_HEIGHT))
        self.ai_hint_button = wx.Button(self, label="AI Hint",
                                        pos=(self.button_position_x, self.grid_position_y + 3 * BUTTON_HEIGHT_MARGIN),
                                        size=(BUTTON_WIDTH, BUTTON_HEIGHT))
        self.analysis_button = wx.Button(self, label="Analysis",
                                         pos=(self.button_position_x, self.grid_position_y + 4 * BUTTON_HEIGHT_MARGIN),
                                         size=(BUTTON_WIDTH, BUTTON_HEIGHT))
        self.back_button.SetFont(button_font)
        self.forward_button.SetFont(button_font)
        self.replay_button.SetFont(button_font)
        self.ai_hint_button.SetFont(button_font)
        self.analysis_button.SetFont(button_font)
        self.black_button.SetFont(image_font)
        self.white_button.SetFont(image_font)
        self.back_button.Disable()
        self.forward_button.Disable()
        self.replay_button.Disable()
        try:
            model_file = 'best_policy.model'
            policy_param = pickle.load(open(model_file, 'rb'), encoding='bytes')
            best_policy = PolicyValueNetNumpy(self.n, policy_param)
            self.mcts_player = MCTSPlayer(best_policy.policy_value_func, c_puct=5, n_play_out=800)
            self.black_button.Enable()
            self.white_button.Enable()
            self.ai_hint_button.Enable()
            self.analysis_button.Enable()
        except IOError as _:
            self.black_button.Disable()
            self.white_button.Disable()
            self.ai_hint_button.Disable()
            self.analysis_button.Disable()
        self.initialize_user_interface()

    def on_back_button_click(self, _):
        if not self.thread.is_alive():
            self.current_move -= 1
            self.board.winner = 0
            self.board.remove_move()
            if self.has_set_ai_player and (self.board.winner == 0 or len(self.board.move_list) < self.n * self.n):
                self.current_move -= 1
                self.board.remove_move()
            self.forward_button.Enable()
            self.analysis_button.Enable()
            self.repaint_board()
            if self.current_move == 0:
                self.back_button.Disable()
                self.replay_button.Disable()
            if self.mcts_player is not None:
                self.ai_hint_button.Enable()

    def on_forward_button_click(self, _):
        if not self.thread.is_alive():
            x, y = self.chess_record[self.current_move]
            self.current_move += 1
            self.board.add_move(y, x)
            if self.has_set_ai_player and (self.board.winner == 0 or len(self.board.move_list) < self.n * self.n):
                x, y = self.chess_record[self.current_move]
                self.current_move += 1
                self.board.add_move(y, x)
            self.back_button.Enable()
            self.replay_button.Enable()
            self.analysis_button.Enable()
            self.repaint_board()
            if self.current_move == self.moves:
                self.forward_button.Disable()
            if self.current_move == self.n * self.n:
                self.ai_hint_button.Disable()

    def on_replay_button_click(self, _):
        if not self.thread.is_alive():
            self.board.initialize()
            self.moves = 0
            self.current_move = 0
            self.has_set_ai_player = False
            self.chess_record.clear()
            self.draw_board()
            self.back_button.Disable()
            self.forward_button.Disable()
            self.replay_button.Disable()
            if self.mcts_player is not None:
                self.black_button.Enable()
                self.white_button.Enable()
                self.ai_hint_button.Enable()
                self.analysis_button.Enable()

    def on_black_button_click(self, _):
        self.black_button.Disable()
        self.white_button.Disable()
        self.has_set_ai_player = True

    def on_white_button_click(self, _):
        self.black_button.Disable()
        self.white_button.Disable()
        self.has_set_ai_player = True
        self.thread = threading.Thread(target=self.ai_next_move, args=())
        self.thread.start()

    def on_ai_hint_button_click(self, _):
        if not self.thread.is_alive():
            self.ai_next_move()

    def on_analysis_button_click(self, _):
        if not self.thread.is_alive():
            moves, probability = copy.deepcopy(self.mcts_player).get_action(self.board, return_probability=2)
            move_list = [(moves[i], p) for i, p in enumerate(probability) if p > 0]
            if len(move_list) > 0:
                self.draw_possible_moves(move_list)
                self.is_analysis_displayed = True
                self.analysis_button.Disable()

    def on_paint(self, _):
        dc = wx.PaintDC(self)
        dc.SetBackground(wx.Brush(wx.WHITE_BRUSH))
        dc.Clear()
        self.draw_board()

    def ai_next_move(self):
        move = self.mcts_player.get_action(self.board)
        x, y = self.board.move_to_location(move)
        self.board.add_move(x, y)
        if self.is_analysis_displayed:
            self.repaint_board()
        self.analysis_button.Enable()
        self.draw_move(y, x)

    def disable_buttons(self):
        end, _ = self.board.has_ended()
        if end:
            self.ai_hint_button.Disable()
            self.analysis_button.Disable()

    def initialize_user_interface(self):
        self.board = Board(self.n)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_UP, self.on_click)
        self.Bind(wx.EVT_BUTTON, self.on_back_button_click, self.back_button)
        self.Bind(wx.EVT_BUTTON, self.on_forward_button_click, self.forward_button)
        self.Bind(wx.EVT_BUTTON, self.on_replay_button_click, self.replay_button)
        self.Bind(wx.EVT_BUTTON, self.on_black_button_click, self.black_button)
        self.Bind(wx.EVT_BUTTON, self.on_white_button_click, self.white_button)
        self.Bind(wx.EVT_BUTTON, self.on_ai_hint_button_click, self.ai_hint_button)
        self.Bind(wx.EVT_BUTTON, self.on_analysis_button_click, self.analysis_button)
        self.Centre()
        self.Show(True)

    def repaint_board(self):
        self.draw_board()
        self.draw_chess()
        self.is_banner_displayed = False
        self.is_analysis_displayed = False

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
        if self.n == STANDARD_LENGTH:
            dc.DrawCircle(self.grid_position_x + BLOCK_LENGTH * 3, self.grid_position_y + BLOCK_LENGTH * 3, 4)
            dc.DrawCircle(self.grid_position_x + BLOCK_LENGTH * 3, self.grid_position_y + BLOCK_LENGTH * 11, 4)
            dc.DrawCircle(self.grid_position_x + BLOCK_LENGTH * 7, self.grid_position_y + BLOCK_LENGTH * 7, 4)
            dc.DrawCircle(self.grid_position_x + BLOCK_LENGTH * 11, self.grid_position_y + BLOCK_LENGTH * 3, 4)
            dc.DrawCircle(self.grid_position_x + BLOCK_LENGTH * 11, self.grid_position_y + BLOCK_LENGTH * 11, 4)

    def draw_possible_moves(self, possible_move):
        dc = wx.ClientDC(self)
        for move, p in possible_move:
            y, x = self.board.move_to_location(move)
            dc.SetBrush(wx.Brush(wx.Colour(56, 162, 84, alpha=14 if int(p * 230) < 14 else int(p * 230))))
            dc.SetPen(wx.Pen(wx.Colour(56, 162, 84, alpha=230)))
            dc.DrawCircle(self.grid_position_x + x * BLOCK_LENGTH, self.grid_position_y + y * BLOCK_LENGTH,
                          self.piece_radius)

    def draw_chess(self):
        dc = wx.ClientDC(self)
        self.disable_buttons()
        for i in range(4, self.n + 4):
            for j in range(4, self.n + 4):
                if self.board.chess[j][i] > 0:
                    dc.SetBrush(wx.Brush(wx.BLACK if self.board.chess[j][i] == 1 else wx.WHITE))
                    dc.DrawCircle(self.grid_position_x + (i - 4) * BLOCK_LENGTH,
                                  self.grid_position_y + (j - 4) * BLOCK_LENGTH, self.piece_radius)
        if self.current_move > 0:
            x, y = self.chess_record[self.current_move - 1]
            x = self.grid_position_x + x * BLOCK_LENGTH
            y = self.grid_position_y + y * BLOCK_LENGTH
            dc.SetBrush(wx.Brush(wx.BLACK if self.current_move % 2 == 1 == 1 else wx.WHITE))
            dc.SetPen(wx.Pen(wx.WHITE if self.current_move % 2 == 1 else wx.BLACK))
            dc.DrawCircle(x, y, self.inner_circle_radius)

    def draw_banner(self, result: int):
        x = (WIN_WIDTH - 216) / 2 + 16
        if result == 1:
            string = "BLACK WIN"
        elif result == 2:
            string = "WHITE WIN"
        else:
            string = "DRAW"
            x = (WIN_WIDTH - 97) / 2 + 16
        dc = wx.ClientDC(self)
        dc.SetBrush(wx.Brush(wx.WHITE))
        dc.DrawRectangle((WIN_WIDTH - BANNER_WIDTH) / 2 + 15, (WIN_HEIGHT - BANNER_HEIGHT) / 2 - HEIGHT_OFFSET + 5,
                         BANNER_WIDTH, BANNER_HEIGHT)
        dc.SetPen(wx.Pen(wx.BLACK))
        dc.SetFont(wx.Font(40, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, False))
        dc.DrawText(string, x, (WIN_HEIGHT - 26) / 2 - HEIGHT_OFFSET)
        self.is_banner_displayed = True

    def draw_move(self, x: int, y: int) -> bool:
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
            end, winner = self.board.has_ended()
            if end:
                self.disable_buttons()
                self.draw_banner(winner)
            return end
        return False

    def on_click(self, e):
        if not self.thread.is_alive():
            if self.board.winner == 0:
                if self.is_analysis_displayed:
                    self.repaint_board()
                x, y = e.GetPosition()
                x = x - self.grid_position_x + BLOCK_LENGTH / 2
                y = y - self.grid_position_y + BLOCK_LENGTH / 2
                if x > 0 and y > 0:
                    x = int(x / BLOCK_LENGTH)
                    y = int(y / BLOCK_LENGTH)
                    if 0 <= x < self.n and 0 <= y < self.n:
                        if self.board.chess[y + 4][x + 4] == 0:
                            self.analysis_button.Enable()
                            self.black_button.Disable()
                            self.white_button.Disable()
                            self.board.add_move(y, x)
                            has_end = self.draw_move(x, y)
                            if self.has_set_ai_player and not has_end:
                                self.thread = threading.Thread(target=self.ai_next_move, args=())
                                self.thread.start()
            elif self.is_banner_displayed:
                self.repaint_board()
