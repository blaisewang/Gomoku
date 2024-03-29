"""
An implementation of the game and the game board

@author: Xudong Wang
"""

import numpy as np

import evaluate
from mcts_alphaZero import MCTSPlayer


def to_list(p1: int, p2: int, n: int) -> []:
    c = [((p1 ^ (p1 >> 1)) >> k) & 1 for k in range(0, n >> 1)][::-1]
    return c + [((p2 ^ (p2 >> 1)) >> k) & 1 for k in range(0, n - (n >> 1))][::-1]


class Board:
    def __init__(self, n: int):
        self.n = n
        self.winner = 0
        self.move_list = []
        self.chess = np.repeat(-1, (self.n + 8) * (self.n + 8)).reshape(self.n + 8, self.n + 8)
        self.chess[4:self.n + 4, 4:self.n + 4] = 0

    def initialize(self):
        self.winner = 0
        self.move_list = []
        self.chess[4:self.n + 4, 4:self.n + 4] = 0

    def add_move(self, x: int, y: int):
        self.move_list.append((x, y))
        self.chess[x + 4, y + 4] = 2 if self.get_move_number() % 2 == 0 else 1

    def remove_move(self):
        x, y = self.move_list.pop()
        self.chess[x + 4, y + 4] = 0

    def move_to_location(self, move: int) -> (int, int):
        x = self.n - move // self.n - 1
        y = move % self.n
        return x, y

    def location_to_move(self, x: int, y: int) -> int:
        return (self.n - x - 1) * self.n + y

    def get_available_moves(self) -> []:
        potential_move_list = []
        for (x, y), value in np.ndenumerate(self.chess[4:self.n + 4, 4:self.n + 4]):
            if not value:
                potential_move_list.append(self.location_to_move(x, y))
        return sorted(potential_move_list)

    def get_current_state(self):
        player = self.get_current_player()
        black_list, white_list = evaluate.get_state(self.chess)
        square_state = np.zeros((4, self.n, self.n))
        for (x, y), value in np.ndenumerate(self.chess[4:self.n + 4, 4:self.n + 4]):
            if value == 1 or value == 2:
                square_state[0][self.n - x - 1][y] = 1.0
        if black_list[0] > 0:
            square_state[1 if player == 1 else 2][self.n - 1] = np.repeat(1, self.n)
        elif white_list[0] > 0:
            square_state[2 if player == 1 else 1][self.n - 1] = np.repeat(1, self.n)
        for i in range(1, 10):
            square_state[1 if player == 1 else 2][self.n - i - 1] = to_list(black_list[i], black_list[i + 9], self.n)
            square_state[2 if player == 1 else 1][self.n - i - 1] = to_list(white_list[i], white_list[i + 9], self.n)
        if self.get_move_number() > 0:
            x, y = self.move_list[self.get_move_number() - 1]
            square_state[3][self.n - x - 1][y] = 1.0
        # opponent = 2 if player == 1 else 1
        # square_state = np.zeros((4, self.n, self.n))
        # for (x, y), value in np.ndenumerate(self.chess[4:self.n + 4, 4:self.n + 4]):
        #     if value == player:
        #         square_state[0][self.n - x - 1][y] = 1.0
        #     elif value == opponent:
        #         square_state[1][self.n - x - 1][y] = 1.0
        # if self.get_move_number() > 0:
        #     x, y = self.move_list[self.get_move_number() - 1]
        #     square_state[2][self.n - x - 1][y] = 1.0
        # if self.get_current_player() == 1:
        #     square_state[3][:, :] = 1.0
        return square_state[:, ::-1, :]

    def get_move_number(self) -> int:
        return len(self.move_list)

    def get_current_player(self) -> int:
        return 1 if self.get_move_number() % 2 == 0 else 2

    def has_winner(self, x: int, y: int):
        if evaluate.has_winner(self.chess, x, y):
            self.winner = self.chess[x, y]

    def has_ended(self):
        if self.get_move_number() == 0:
            return False, -1
        x, y = self.move_list[self.get_move_number() - 1]
        self.has_winner(x + 4, y + 4)
        if self.winner != 0:
            return True, self.winner
        else:
            if self.get_move_number() == self.n * self.n:
                return True, -1
            else:
                return False, -1


class Game:
    def __init__(self, board: 'Board'):
        self.board = board

    def start_play(self, args) -> int:
        player1, player2, index = args
        if index % 2:
            player1, player2 = player2, player1
        self.board.initialize()
        while self.board.get_move_number() < self.board.n * self.board.n:
            player_in_turn = player1 if self.board.get_current_player() == 1 else player2
            move = player_in_turn.get_action(self.board)
            x, y = self.board.move_to_location(move)
            self.board.add_move(x, y)
            has_ended, winner = self.board.has_ended()
            if has_ended:
                if index % 2:
                    winner = 1 if winner == 2 else 2
                return winner

    def start_self_play(self, player: 'MCTSPlayer', temp=1e-3):
        """ start a self-play game using a MCTS player, reuse the search tree
        store the self-play data: (state, mcts_probabilities, z)
        """
        self.board.initialize()
        states, mcts_probabilities, current_players = [], [], []
        while self.board.get_move_number() < self.board.n * self.board.n:
            move, move_probabilities = player.get_action(self.board, temp=temp, return_probability=1)
            # store the data
            states.append(self.board.get_current_state())
            mcts_probabilities.append(move_probabilities)
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
                return zip(states, mcts_probabilities, winners_z)
