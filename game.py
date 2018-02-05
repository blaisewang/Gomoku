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
        self.chess = [[-2 for _ in range(self.n + 8)] for _ in range(self.n + 8)]
        for i in range(4, self.n + 4):
            for j in range(4, self.n + 4):
                self.chess[i][j] = 0

    def initialize(self):
        self.winner = 0
        self.move_list = []
        for i in range(4, self.n + 4):
            for j in range(4, self.n + 4):
                self.chess[i][j] = 0

    def add_move(self, x: int, y: int):
        self.move_list.append((x, y))
        self.chess[x + 4][y + 4] = 2 if len(self.move_list) % 2 == 0 else 1

    def remove_move(self):
        x, y = self.move_list.pop()
        self.chess[x + 4][y + 4] = 0

    def move_to_location(self, move: int) -> (int, int):
        x = self.n - move // self.n - 1
        y = move % self.n
        return x, y

    def location_to_move(self, x: int, y: int) -> int:
        return (self.n - x - 1) * self.n + y

    def get_available_moves(self) -> []:
        potential_move_list = []
        for i in range(4, self.n + 4):
            for j in range(4, self.n + 4):
                if self.chess[i][j] == 0:
                    if len(self.move_list) % 2 == 1:
                        if self.has_neighbor(i, j, 2):
                            potential_move_list.append(self.location_to_move(i - 4, j - 4))
                    else:
                        potential_move_list.append(self.location_to_move(i - 4, j - 4))
        return sorted(potential_move_list)

    def get_current_state(self) -> []:
        player = 1 if len(self.move_list) % 2 == 0 else 2
        opponent = 2 if player == 1 else 1
        square_state = np.zeros((4, self.n, self.n))
        for i in range(4, self.n + 4):
            for j in range(4, self.n + 4):
                if self.chess[i][j] == player and self.is_boundary(i, j, 2):
                    square_state[0][self.n - i + 3][j - 4] = 1.0
                elif self.chess[i][j] == opponent and self.is_boundary(i, j, 2):
                    square_state[1][self.n - i + 3][j - 4] = 1.0
        if len(self.move_list) > 0:
            x, y = self.move_list[len(self.move_list) - 1]
            square_state[2][self.n - x - 1][y] = 1.0
        if player == 1:
            square_state[3][:, :] = 1.0
        return square_state[:, ::-1, :]

    def has_neighbor(self, x: int, y: int, depth: int) -> bool:
        neighbor_list = [(x - 1, y - 1), (x - 1, y), (x - 1, y + 1), (x, y - 1), (x, y + 1), (x + 1, y - 1),
                         (x + 1, y), (x + 1, y + 1)]
        for px, py in neighbor_list:
            if self.chess[px][py] == 1 or self.chess[px][py] == 2:
                if depth == 0 or self.is_boundary(px, py, depth - 1):
                    return True
        return False

    def is_boundary(self, x: int, y: int, depth: int) -> bool:
        if len(self.move_list) < 4:
            return True
        return self.has_neighbor(x, y, depth)

    def has_winner(self, x: int, y: int):
        player = 2 if len(self.move_list) % 2 == 0 else 1
        if evaluate.has_winner(x + 4, y + 4, player, self.chess):
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

    def start_play(self, args):
        player1, player2, index = args
        if index % 2:
            player1, player2 = player2, player1
        self.board.initialize()
        while len(self.board.move_list) < self.board.n * self.board.n:
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
        store the self-play data: (state, mcts_probability, z)
        """
        self.board.initialize()
        states, mcts_probability, current_players = [], [], []
        while len(self.board.move_list) < self.board.n * self.board.n:
            move, move_probability = player.get_action(self.board, temp=temp, return_probability=1)
            # store the data
            states.append(self.board.get_current_state())
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
