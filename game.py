import numpy as np

import evaluate
from mcts_alphaZero import MCTSPlayer


class Board:
    def __init__(self, n: int):
        if 8 <= n <= 15:
            self.n = n
        else:
            raise Exception('Illegal Parameter N')
        self.winner = 0
        self.move_list = []
        self.chess = [[0 for _ in range(self.n)] for _ in range(self.n)]

    def initialize(self):
        self.winner = 0
        self.move_list = []
        self.chess = [[0 for _ in range(self.n)] for _ in range(self.n)]

    def add_move(self, x: int, y: int):
        self.move_list.append((x, y))
        self.chess[x][y] = 2 if len(self.move_list) % 2 == 0 else 1

    def remove_move(self):
        x, y = self.move_list.pop()
        self.chess[x][y] = 0

    def move_to_location(self, move: int) -> (int, int):
        x = self.n - move // self.n - 1
        y = move % self.n
        return x, y

    def location_to_move(self, x: int, y: int) -> int:
        return (self.n - x - 1) * self.n + y

    def get_available_moves(self) -> []:
        move_list = []
        append = move_list.append
        for i in range(self.n):
            for j in range(self.n):
                if self.chess[i][j] == 0:
                    append(self.location_to_move(i, j))
        return sorted(move_list)

    def current_state(self) -> []:
        player = 1 if len(self.move_list) % 2 == 0 else 2
        opponent = 2 if player == 1 else 1
        square_state = np.zeros((4, self.n, self.n))
        for i in range(self.n):
            for j in range(self.n):
                if self.chess[i][j] == player:
                    square_state[0][self.n - i - 1][j] = 1.0
                elif self.chess[i][j] == opponent:
                    square_state[1][self.n - i - 1][j] = 1.0
        if len(self.move_list) > 0:
            x, y = self.move_list[len(self.move_list) - 1]
            square_state[2][self.n - x - 1][y] = 1.0
        if player == 1:
            square_state[3][:, :] = 1.0
        return square_state[:, ::-1, :]

    def has_winner(self, x: int, y: int):
        player = 2 if len(self.move_list) % 2 == 0 else 1
        chess = [[-2 for _ in range(self.n + 8)] for _ in range(self.n + 8)]
        for i in range(self.n):
            for j in range(self.n):
                chess[i + 4][j + 4] = self.chess[i][j]
        if evaluate.has_winner(x + 4, y + 4, player, chess):
            self.winner = player

    def has_ended(self) -> (bool, int):
        if len(self.move_list) == 0:
            return False, -1
        x, y = self.move_list[len(self.move_list) - 1]
        self.has_winner(x, y)
        if self.winner != 0:
            return True, self.winner
        else:
            if len(self.move_list) == self.n * self.n:
                return True, -1
            else:
                return False, -1

    def get_current_player(self):
        return 1 if len(self.move_list) % 2 == 0 else 2


class Game:
    def __init__(self, board: 'Board'):
        self.board = board

    def start_play(self, player1, player2):
        self.board.initialize()
        while 1:
            player_in_turn = player1 if self.board.get_current_player() == 1 else player2
            move = player_in_turn.get_action(self.board)
            x, y = self.board.move_to_location(move)
            self.board.add_move(x, y)
            has_ended, winner = self.board.has_ended()
            if has_ended:
                return winner

    def start_self_play(self, player: 'MCTSPlayer', temp=1e-3):
        """ start a self-play game using a MCTS player, reuse the search tree
        store the self-play data: (state, mcts_probability, z)
        """
        self.board.initialize()
        states, mcts_probability, current_players = [], [], []
        while 1:
            move, move_probability = player.get_action(self.board, temp=temp, return_probability=1)
            # store the data
            states.append(self.board.current_state())
            mcts_probability.append(move_probability)
            current_players.append(self.board.get_current_player())
            # perform a move
            x, y = self.board.move_to_location(move)
            self.board.add_move(x, y)
            has_ended, winner = self.board.has_ended()
            if has_ended:
                # winner from the perspective of the current player of each state
                winners_z = np.zeros(len(current_players))
                if winner != -1:
                    winners_z[np.array(current_players) == winner] = 1.0
                    winners_z[np.array(current_players) != winner] = -1.0
                # reset MCTS root node
                player.reset_player()
                return winner, zip(states, mcts_probability, winners_z)
