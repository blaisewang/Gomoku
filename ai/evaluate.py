import numpy as np


class StateAndReward:
    x: int
    y: int
    move: int
    chess: [[]]
    one_dimensional_opponent_pattern_list: []
    one_dimensional_opponent_winning_pattern_list: []
    two_dimensional_opponent_winning_pattern_list: [[]]

    def __init__(self, chess, args, moves=0, is_simulate=False):
        self.chess = chess
        self.move = moves + 1 if is_simulate else moves
        self.x, self.y = args
        if is_simulate:
            self.chess[self.x][self.y] = 2 if self.move % 2 == 0 else 1

        player = 1 if self.move % 2 == 0 else 2
        opponent = 2 if player == 1 else 1
        self.one_dimensional_opponent_pattern_list = [
            ("BOOBOB", [0, opponent, opponent, 0, opponent, 0], True, 4, 100),
            ("OOBOO", [opponent, opponent, 0, opponent, opponent], False, 4, 100),
            ("OOOBO", [opponent, opponent, opponent, 0, opponent], True, 4, 100),
            ("BOOOB", [0, opponent, opponent, opponent, 0], False, 3, 50),
            ("BOOB", [0, opponent, opponent, 0], False, 2, 40),
            ("BOBOB", [0, opponent, 0, opponent, 0], False, 3, 30),
            ("POOOOB", [player, opponent, opponent, opponent, opponent, 0], True, 4, 20),
            ("POOOB", [player, opponent, opponent, opponent, 0], True, 3, 10),
            ("POOB", [player, opponent, opponent, 0], True, 2, 5),
            ("POB", [player, opponent, 0], True, 1, 1)
        ]
        self.one_dimensional_opponent_winning_pattern_list = [
            ("O_WIN", [opponent, opponent, opponent, opponent, opponent], 4),
            ("O_N_WIN", [opponent, opponent, opponent, opponent, 0], 3),
        ]
        self.two_dimensional_opponent_winning_pattern_list = [
            ("OC_N_WIN", [[-1, -1, 0, -1, -1],
                          [-1, -1, opponent, -1, -1],
                          [0, opponent, opponent, opponent, 0],
                          [-1, -1, opponent, -1, -1],
                          [-1, -1, 0, -1, -1]], False, (2, 2)),
            ("OC_N_WIN", [[-1, 0, -1, -1, -1],
                          [0, opponent, opponent, opponent, 0],
                          [-1, opponent, - 1, -1, -1],
                          [-1, opponent, - 1, -1, -1],
                          [-1, 0, -1, -1, -1]], True, (1, 1))
        ]

    def get_state_and_reward(self) -> ({}, int):
        return self.get_state(), self.get_reward()

    def get_state(self) -> {}:
        player = 1 if self.move % 2 == 0 else 2
        opponent = 2 if player == 1 else 1

        pattern_dictionary = {
            "BPPBPB": 0.0,
            "PPBPP": 0.0,
            "PPPBP": 0.0,
            "BPPPB": 0.0,
            "BPPB": 0.0,
            "BPBPB": 0.0,
            "OPPPPB": 0.0,
            "OPPPB": 0.0,
            "OPPB": 0.0,
            "OPB": 0.0,

            "BOOBOB": 0.0,
            "OOBOO": 0.0,
            "OOOBO": 0.0,
            "BOOOB": 0.0,
            "BOOB": 0.0,
            "BOBOB": 0.0,
            "POOOOB": 0.0,
            "POOOB": 0.0,
            "POOB": 0.0,
            "POB": 0.0,

            "P_CROSS": 0.0,
            "P_V_CROSS": 0.0,
            "O_CROSS": 0.0,
            "O_V_CROSS": 0.0,

            "P_N_WIN": 0.0,
            "PC_N_WIN": 0.0,
            "P_WIN": 0.0,

            "O_N_WIN": 0.0,
            "OC_N_WIN": 0.0,
            "O_WIN": 0.0,

            "START": 0.0
        }

        if self.move == 0:
            return pattern_dictionary

        if self.move == 1:
            pattern_dictionary["START"] = 1.0
        else:
            one_dimensional_player_pattern_list = [
                ("BPPBPB", [0, player, player, 0, player, 0], True, 4),
                ("PPBPP", [player, player, 0, player, player], False, 4),
                ("PPPBP", [player, player, player, 0, player], True, 4),
                ("BPPPB", [0, player, player, player, 0], False, 3),
                ("BPPB", [0, player, player, 0], False, 2),
                ("BPBPB", [0, player, 0, player, 0], False, 3),
                ("OPPPPB", [opponent, player, player, player, player, 0], True, 4),
                ("OPPPB", [opponent, player, player, player, 0], True, 3),
                ("OPPB", [opponent, player, player, 0], True, 2),
                ("OPB", [opponent, player, 0], True, 1)
            ]

            two_dimensional_pattern_list = [
                ("P_CROSS", [[-1, -1, 0, -1, -1],
                             [-1, -1, player, -1, -1],
                             [0, player, 0, player, 0],
                             [-1, -1, player, -1, -1],
                             [-1, -1, 0, -1, -1]], False, (2, 2)),
                ("P_V_CROSS", [[-1, 0, -1, -1, -1],
                               [0, 0, player, player, 0],
                               [-1, player, - 1, -1, -1],
                               [-1, player, - 1, -1, -1],
                               [-1, 0, -1, -1, -1]], True, (1, 1)),
                ("O_CROSS", [[-1, -1, 0, -1, -1],
                             [-1, -1, opponent, -1, -1],
                             [0, opponent, 0, opponent, 0],
                             [-1, -1, opponent, -1, -1],
                             [-1, -1, 0, -1, -1]], False, (2, 2)),
                ("O_V_CROSS", [[-1, 0, -1, -1, -1],
                               [0, 0, opponent, opponent, 0],
                               [-1, opponent, - 1, -1, -1],
                               [-1, opponent, - 1, -1, -1],
                               [-1, 0, -1, -1, -1]], True, (1, 1)),
            ]

            one_dimensional_player_winning_pattern_list = [
                ("P_WIN", [player, player, player, player, player], 4),
                ("P_N_WIN", [player, player, player, player, 0], 3)
            ]

            two_dimensional_player_winning_pattern_list = [
                ("PC_N_WIN", [[-1, -1, 0, -1, -1],
                              [-1, -1, player, -1, -1],
                              [0, player, player, player, 0],
                              [-1, -1, player, -1, -1],
                              [-1, -1, 0, -1, -1]], False, (2, 2)),
                ("PC_N_WIN", [[-1, 0, -1, -1, -1],
                              [0, player, player, player, 0],
                              [-1, player, - 1, -1, -1],
                              [-1, player, - 1, -1, -1],
                              [-1, 0, -1, -1, -1]], True, (1, 1))
            ]

            for i in range(4, 19):
                for j in range(4, 19):
                    if self.chess[i][j] == player:
                        for key, pattern, need_reverse, left_offset in one_dimensional_player_pattern_list:
                            number = self.one_dimensional_pattern_match(pattern, need_reverse, i, j, left_offset)
                            if number > 0:
                                pattern_dictionary[key] += number
                        for key, pattern, left_offset in one_dimensional_player_winning_pattern_list:
                            number = self.one_dimensional_pattern_match(pattern, False, i, j, left_offset)
                            if number > 0:
                                pattern_dictionary[key] += number
                        for key, pattern, need_rotate, (
                                anchor_x, anchor_y) in two_dimensional_player_winning_pattern_list:
                            number = self.two_dimensional_pattern_match(pattern, need_rotate, i, j, anchor_x, anchor_y)
                            if number > 0:
                                pattern_dictionary[key] += number
                    elif self.chess[i][j] == opponent:
                        for key, pattern, need_reverse, left_offset, _ in self.one_dimensional_opponent_pattern_list:
                            number = self.one_dimensional_pattern_match(pattern, need_reverse, i, j, left_offset)
                            if number > 0:
                                pattern_dictionary[key] += number
                        for key, pattern, left_offset in self.one_dimensional_opponent_winning_pattern_list:
                            number = self.one_dimensional_pattern_match(pattern, False, i, j, left_offset)
                            if number > 0:
                                pattern_dictionary[key] += number
                        for key, pattern, need_rotate, (
                                anchor_x, anchor_y) in self.two_dimensional_opponent_winning_pattern_list:
                            number = self.two_dimensional_pattern_match(pattern, need_rotate, i, j, anchor_x, anchor_y)
                            if number > 0:
                                pattern_dictionary[key] += number
                    else:
                        for key, pattern, need_rotate, (anchor_x, anchor_y) in two_dimensional_pattern_list:
                            number = self.two_dimensional_pattern_match(pattern, need_rotate, i, j, anchor_x, anchor_y)
                            if number > 0:
                                pattern_dictionary[key] += number

            pattern_dictionary["BPPPB"] /= 3
            pattern_dictionary["BPPB"] /= 2
            pattern_dictionary["BPBPB"] /= 2
            pattern_dictionary["OPPPPB"] /= 4
            pattern_dictionary["OPPPB"] /= 3
            pattern_dictionary["OPPB"] /= 2
            pattern_dictionary["BOOOB"] /= 3
            pattern_dictionary["BOOB"] /= 2
            pattern_dictionary["BOBOB"] /= 2
            pattern_dictionary["POOOOB"] /= 4
            pattern_dictionary["POOOB"] /= 3
            pattern_dictionary["POOB"] /= 2
            pattern_dictionary["P_WIN"] /= 5
            pattern_dictionary["P_N_WIN"] /= 4
            pattern_dictionary["O_WIN"] /= 5
            pattern_dictionary["O_N_WIN"] /= 4
            if pattern_dictionary["PC_N_WIN"] % 2 == 0:
                pattern_dictionary["PC_N_WIN"] /= 2
            if pattern_dictionary["P_CROSS"] % 2 == 0:
                pattern_dictionary["P_CROSS"] /= 2
            if pattern_dictionary["OC_N_WIN"] % 2 == 0:
                pattern_dictionary["OC_N_WIN"] /= 2
            if pattern_dictionary["O_CROSS"] % 2 == 0:
                pattern_dictionary["O_CROSS"] /= 2

        return pattern_dictionary

    def get_reward(self) -> int:
        if self.move == 0:
            return 0
        elif self.move == 1:
            if self.x == 11 and self.y == 11:
                return 100
            else:
                return 0

        reward = 0
        player = 2 if self.move % 2 == 0 else 1
        opponent = 1 if player == 1 else 2

        one_dimensional_dangerous_pattern_list = [
            ([opponent, opponent, player, opponent, opponent], 2, 3),
            ([opponent, opponent, opponent, player, opponent], 3, 2),
            ([0, opponent, opponent, opponent, player], 4, 1),
            ([0, opponent, opponent, player, opponent, 0], 3, 3),
            ([opponent, opponent, opponent, opponent, player], 4, 1)
        ]

        two_dimensional_dangerous_pattern_list = [
            ([[-1, -1, 0, -1, -1],
              [-1, -1, opponent, -1, -1],
              [0, opponent, player, opponent, 0],
              [-1, -1, opponent, -1, -1],
              [-1, -1, 0, -1, -1]], False, (2, 2)),

            ([[-1, 0, -1, -1, -1],
              [0, player, opponent, opponent, 0],
              [-1, opponent, - 1, -1, -1],
              [-1, opponent, - 1, -1, -1],
              [-1, 0, -1, -1, -1]], True, (1, 1))
        ]

        for _, pattern, left_offset in self.one_dimensional_opponent_winning_pattern_list:
            if self.one_dimensional_pattern_match(pattern, False, self.x, self.y, left_offset):
                return 100

        for pattern, left_offset, right_offset in one_dimensional_dangerous_pattern_list:
            if self.one_dimensional_pattern_match(pattern, True, self.x, self.y, left_offset, right_offset):
                return 100

        for _, pattern, need_rotate, (anchor_x, anchor_y) in self.two_dimensional_opponent_winning_pattern_list:
            if self.two_dimensional_pattern_match(pattern, need_rotate, self.x, self.y, anchor_x, anchor_y):
                return 100

        for pattern, need_rotate, (anchor_x, anchor_y) in two_dimensional_dangerous_pattern_list:
            if self.two_dimensional_pattern_match(pattern, need_rotate, self.x, self.y, anchor_x, anchor_y):
                return 100

        for _, pattern, need_reverse, left_offset, expect_reward in self.one_dimensional_opponent_pattern_list:
            reward += expect_reward * self.one_dimensional_pattern_match(pattern, need_reverse, self.x, self.y,
                                                                         left_offset)
        return reward

    def has_winner(self, pattern: []) -> bool:
        return self.one_dimensional_pattern_match(pattern, False, self.x, self.y, 4) > 0

    def get_1d_matching(self, pattern: [], x: int, y: int, l_ofs: int, r_ofs: int) -> int:
        diff = y - x
        rot = x - 22 + y
        bias = 0 if diff <= 0 else abs(diff)
        rot_bias = 0 if rot <= 0 else abs(rot)

        return (int(self.is_pattern_match([pattern], [np.array(self.chess)[x, y - l_ofs: y + r_ofs]])) +
                int(self.is_pattern_match([pattern], [np.array(self.chess)[x - l_ofs: x + r_ofs, y]])) +
                int(self.is_pattern_match([pattern],
                                          [np.diagonal(self.chess, offset=diff)[y - bias - l_ofs:y - bias + r_ofs]])) +
                int(self.is_pattern_match([pattern], [np.diagonal(np.rot90(self.chess), offset=rot)[
                                                      x - rot_bias - l_ofs:x - rot_bias + r_ofs]])))

    def one_dimensional_pattern_match(self, pattern: [], need_reverse: bool, x: int, y: int, l_ofs: int,
                                      *r_offset: int) -> int:
        if len(r_offset) == 0:
            r_ofs = l_ofs + 1
        else:
            r_ofs = r_offset[0]
        number = self.get_1d_matching(pattern, x, y, l_ofs, r_ofs)
        if need_reverse:
            number += self.get_1d_matching(list(reversed(pattern)), x, y, r_ofs - 1, l_ofs + 1)
        return number

    def get_2d_matching(self, pattern: [[]], x: int, y: int, anchor_x: int, anchor_y: int) -> int:
        diff = y - x
        u_ofs = anchor_y
        d_ofs = len(pattern) - anchor_y
        l_ofs = anchor_x
        r_ofs = len(pattern[0]) - anchor_x
        rot_x = 22 - y
        rot_y = x
        rot = rot_y - rot_x

        diagonal = []
        for i in range(y - u_ofs, y + d_ofs):
            offset = diff + (i - y) * 2
            bias = 0 if offset <= 0 else offset
            diagonal.append(np.diagonal(self.chess, offset=offset)[i - bias - l_ofs:i - bias + r_ofs])
        anti_diagonal = []
        for i in range(x - u_ofs, x + d_ofs):
            offset = rot + (i - x) * 2
            rot_bias = 0 if offset <= 0 else offset
            anti_diagonal.append(
                np.diagonal(np.rot90(self.chess), offset=offset)[i - rot_bias - l_ofs:i - rot_bias + r_ofs])

        return (int(self.is_pattern_match(pattern, np.array(self.chess)[x - u_ofs: x + d_ofs, y - l_ofs: y + r_ofs])) +
                int(self.is_pattern_match(pattern, np.rot90(self.chess)[
                                                   rot_x - u_ofs: rot_x + d_ofs, rot_y - l_ofs: rot_y + r_ofs])) +
                int(self.is_pattern_match(pattern, diagonal)) + int(self.is_pattern_match(pattern, anti_diagonal)))

    def two_dimensional_pattern_match(self, pattern: [[]], need_rotate: bool, x: int, y: int,
                                      anchor_x: int, anchor_y: int) -> int:
        number = self.get_2d_matching(pattern, x, y, anchor_x, anchor_y)
        if need_rotate:
            number += self.get_2d_matching(np.rot90(np.rot90(pattern)), x, y, len(pattern) - anchor_x - 1,
                                           len(pattern[0]) - anchor_y - 1)
        return number

    @staticmethod
    def is_pattern_match(pattern: [[]], array: [[]]) -> bool:
        pattern_rows = len(pattern)
        pattern_columns = len(pattern[0])
        array_rows = len(array)
        array_columns = len(array[0])

        flag = False
        for i in range(array_rows - pattern_rows + 1):
            for j in range(array_columns - pattern_columns + 1):
                similarity = 0
                for k in range(pattern_rows):
                    for l in range(pattern_columns):
                        if pattern[k][l] != array[i + k][j + l] and pattern[k][l] != -1:
                            break
                        similarity += 1
                if similarity == pattern_rows * pattern_columns:
                    flag = True
                    break
        return flag
