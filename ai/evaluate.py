import copy
import numpy

import ai


def get_state_and_reward(chess, args, moves=0, is_simulate=False) -> ():
    x, y = args
    if is_simulate:
        chess[x][y] = 2 if moves % 2 == 0 else 1

    return args, (get_state(moves, chess), get_reward(x, y, moves, chess))


def get_state(move: int, chess: [[]]) -> []:
    player = 2 if move % 2 == 0 else 1
    opponent = 2 if player == 1 else 1

    pattern_dictionary = {
        "PLAYER": player,

        "B_P_P_P_B": 0.0,
        "B_P_P_B_B": 0.0,
        "B_P_B_P_B": 0.0,
        "O_P_P_P_P_B": 0.0,
        "O_P_P_P_B_B": 0.0,
        "O_P_P_B_B_B": 0.0,
        "O_P_B_B_B_B": 0.0,

        "B_O_O_B_O_B": 0.0,
        "O_O_B_O_O": 0.0,
        "O_O_O_B_O": 0.0,
        "B_O_O_O_B": 0.0,
        "B_O_O_B_B": 0.0,
        "B_O_B_O_B": 0.0,
        "P_O_O_O_O_B": 0.0,
        "P_O_O_O_B_B": 0.0,
        "P_O_O_B_B_B": 0.0,
        "P_O_B_B_B_B": 0.0,

        "PLAYER_CROSS": 0.0,
        "PLAYER_VERTICAL_CROSS": 0.0,
        "OPPONENT_CROSS": 0.0,
        "OPPONENT_VERTICAL_CROSS": 0.0,

        "PLAYER_NEARLY_WIN": 0.0,
        "PLAYER_CROSS_NEARLY_WIN": 0.0,
        "PLAYER_WIN": 0.0,

        "OPPONENT_NEARLY_WIN": 0.0,
        "OPPONENT_CROSS_NEARLY_WIN": 0.0,
        "OPPONENT_WIN": 0.0,

        "START": 0.0
    }

    if move == 0:
        return list(pattern_dictionary.values())
    if move == 1:
        pattern_dictionary["START"] = 1.0
    else:
        one_dimensional_player_pattern_list = [
            ("B_P_P_P_B", [0, player, player, player, 0], False, 3, 30),
            ("B_P_P_B_B", [0, player, player, 0, 0], True, 3, 12),
            ("B_P_B_P_B", [0, player, 0, player, 0], False, 3, 20),
            ("O_P_P_P_P_B", [opponent, player, player, player, player, 0], True, 4, 15),
            ("O_P_P_P_B_B", [opponent, player, player, player, 0, 0], True, 4, 10),
            ("O_P_P_B_B_B", [opponent, player, player, 0, 0, 0], True, 4, 5),
            ("O_P_B_B_B_B", [opponent, player, 0, 0, 0, 0], True, 4, 1)
        ]

        one_dimensional_opponent_pattern_list = [
            ("B_O_O_B_O_B", [0, opponent, opponent, 0, opponent, 0], True, 4),
            ("O_O_B_O_O", [opponent, opponent, 0, opponent, opponent], False, 4),
            ("O_O_O_B_O", [opponent, opponent, opponent, 0, opponent], True, 4),
            ("B_O_O_O_B", [0, opponent, opponent, opponent, 0], False, 3),
            ("B_O_O_B_B", [0, opponent, opponent, 0, 0], True, 3),
            ("B_O_B_O_B", [0, opponent, 0, opponent, 0], False, 3),
            ("P_O_O_O_O_B", [player, opponent, opponent, opponent, opponent, 0], True, 4),
            ("P_O_O_O_B_B", [player, opponent, opponent, opponent, 0, 0], True, 4),
            ("P_O_O_B_B_B", [player, opponent, opponent, 0, 0, 0], True, 4),
            ("P_O_B_B_B_B", [player, opponent, 0, 0, 0, 0], True, 4)
        ]

        two_dimensional_pattern_list = [
            ("PLAYER_CROSS", [[-1, -1, 0, -1, -1],
                              [-1, -1, player, -1, -1],
                              [0, player, 0, player, 0],
                              [-1, -1, player, -1, -1],
                              [-1, -1, 0, -1, -1]], False, (2, 2)),
            ("PLAYER_VERTICAL_CROSS", [[-1, 0, -1, -1, -1],
                                       [0, 0, player, player, 0],
                                       [-1, player, - 1, -1, -1],
                                       [-1, player, - 1, -1, -1],
                                       [-1, 0, -1, -1, -1]], True, (1, 1)),
            ("OPPONENT_CROSS", [[-1, -1, 0, -1, -1],
                                [-1, -1, opponent, -1, -1],
                                [0, opponent, 0, opponent, 0],
                                [-1, -1, opponent, -1, -1],
                                [-1, -1, 0, -1, -1]], False, (2, 2)),
            ("OPPONENT_VERTICAL_CROSS", [[-1, 0, -1, -1, -1],
                                         [0, 0, opponent, opponent, 0],
                                         [-1, opponent, - 1, -1, -1],
                                         [-1, opponent, - 1, -1, -1],
                                         [-1, 0, -1, -1, -1]], True, (1, 1)),
        ]

        one_dimensional_player_winning_pattern_list = [
            ("PLAYER_WIN", [player, player, player, player, player], 4),
            ("PLAYER_NEARLY_WIN", [0, player, player, player, player, 0], 4)
        ]

        one_dimensional_opponent_winning_pattern_list = [
            ("OPPONENT_WIN", [opponent, opponent, opponent, opponent, opponent], False, 4),
            ("OPPONENT_NEARLY_WIN", [opponent, opponent, opponent, opponent, 0], True, 4),
        ]

        two_dimensional_player_winning_pattern_list = [
            ("PLAYER_CROSS_NEARLY_WIN", [[-1, -1, 0, -1, -1],
                                         [-1, -1, player, -1, -1],
                                         [0, player, player, player, 0],
                                         [-1, -1, player, -1, -1],
                                         [-1, -1, 0, -1, -1]], False, (2, 2)),
            ("PLAYER_CROSS_NEARLY_WIN", [[-1, 0, -1, -1, -1],
                                         [0, player, player, player, 0],
                                         [-1, player, - 1, -1, -1],
                                         [-1, player, - 1, -1, -1],
                                         [-1, 0, -1, -1, -1]], True, (1, 1))
        ]

        two_dimensional_opponent_winning_pattern_list = [
            ("OPPONENT_CROSS_NEARLY_WIN", [[-1, -1, 0, -1, -1],
                                           [-1, -1, opponent, -1, -1],
                                           [0, opponent, opponent, opponent, 0],
                                           [-1, -1, opponent, -1, -1],
                                           [-1, -1, 0, -1, -1]], False, (2, 2)),
            ("OPPONENT_CROSS_NEARLY_WIN", [[-1, 0, -1, -1, -1],
                                           [0, opponent, opponent, opponent, 0],
                                           [-1, opponent, - 1, -1, -1],
                                           [-1, opponent, - 1, -1, -1],
                                           [-1, 0, -1, -1, -1]], True, (1, 1))
        ]

        for i in range(4, 19):
            for j in range(4, 19):
                if chess[i][j] == player:
                    for key, pattern, need_reverse, left_offset, _ in one_dimensional_player_pattern_list:
                        number = one_dimensional_pattern_match(pattern, chess, need_reverse, i, j, left_offset)
                        if number > 0:
                            pattern_dictionary[key] += number
                    for key, pattern, left_offset in one_dimensional_player_winning_pattern_list:
                        number = one_dimensional_pattern_match(pattern, chess, False, i, j, left_offset)
                        if number > 0:
                            pattern_dictionary[key] += number
                    for key, pattern, need_rotate, (
                            anchor_x, anchor_y) in two_dimensional_player_winning_pattern_list:
                        number = two_dimensional_pattern_match(pattern, chess, need_rotate, i, j, anchor_x, anchor_y)
                        if number > 0:
                            pattern_dictionary[key] += number
                elif chess[i][j] == opponent:
                    for key, pattern, need_reverse, left_offset in one_dimensional_opponent_pattern_list:
                        number = one_dimensional_pattern_match(pattern, chess, need_reverse, i, j, left_offset)
                        if number > 0:
                            pattern_dictionary[key] += number
                    for key, pattern, need_reverse, left_offset in one_dimensional_opponent_winning_pattern_list:
                        number = one_dimensional_pattern_match(pattern, chess, need_reverse, i, j, left_offset)
                        if number > 0:
                            pattern_dictionary[key] += number
                    for key, pattern, need_rotate, (
                            anchor_x, anchor_y) in two_dimensional_opponent_winning_pattern_list:
                        number = two_dimensional_pattern_match(pattern, chess, need_rotate, i, j, anchor_x, anchor_y)
                        if number > 0:
                            pattern_dictionary[key] += number
                else:
                    for key, pattern, need_rotate, (anchor_x, anchor_y) in two_dimensional_pattern_list:
                        number = two_dimensional_pattern_match(pattern, chess, need_rotate, i, j, anchor_x, anchor_y)
                        if number > 0:
                            pattern_dictionary[key] += number

        pattern_dictionary["B_P_P_P_B"] /= 3
        pattern_dictionary["B_P_P_B_B"] /= 2
        pattern_dictionary["B_P_B_P_B"] /= 2
        pattern_dictionary["O_P_P_P_P_B"] /= 4
        pattern_dictionary["O_P_P_P_B_B"] /= 3
        pattern_dictionary["O_P_P_B_B_B"] /= 2
        pattern_dictionary["B_O_O_B_O_B"] /= 3
        pattern_dictionary["O_O_B_O_O"] /= 4
        pattern_dictionary["O_O_O_B_O"] /= 4
        pattern_dictionary["B_O_O_O_B"] /= 3
        pattern_dictionary["B_O_O_B_B"] /= 2
        pattern_dictionary["B_O_B_O_B"] /= 2
        pattern_dictionary["P_O_O_O_O_B"] /= 4
        pattern_dictionary["P_O_O_O_B_B"] /= 3
        pattern_dictionary["P_O_O_B_B_B"] /= 2
        pattern_dictionary["PLAYER_WIN"] /= 5
        pattern_dictionary["PLAYER_NEARLY_WIN"] /= 4
        pattern_dictionary["OPPONENT_WIN"] /= 5
        pattern_dictionary["OPPONENT_NEARLY_WIN"] /= 4
        if pattern_dictionary["PLAYER_CROSS_NEARLY_WIN"] % 2 == 0:
            pattern_dictionary["PLAYER_CROSS_NEARLY_WIN"] /= 2
        if pattern_dictionary["PLAYER_CROSS"] % 2 == 0:
            pattern_dictionary["PLAYER_CROSS"] /= 2
        if pattern_dictionary["OPPONENT_CROSS_NEARLY_WIN"] % 2 == 0:
            pattern_dictionary["OPPONENT_CROSS_NEARLY_WIN"] /= 2
        if pattern_dictionary["OPPONENT_CROSS"] % 2 == 0:
            pattern_dictionary["OPPONENT_CROSS"] /= 2

    return list(pattern_dictionary.values())


def get_reward(x: int, y: int, move: int, chess: [[]]) -> int:
    if move == 0:
        return 0
    elif move == 1:
        if x == 11 and y == 11:
            return 100
        else:
            return 0

    reward = 0
    player = 2 if move % 2 == 0 else 1
    opponent = 1 if player == 1 else 2

    one_dimensional_player_winning_pattern_list = [
        ("PLAYER_WIN", [player, player, player, player, player], 4),
        ("PLAYER_NEARLY_WIN", [0, player, player, player, player, 0], 4)
    ]

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

    two_dimensional_player_winning_pattern_list = [
        ("PLAYER_CROSS_NEARLY_WIN", [[-1, -1, 0, -1, -1],
                                     [-1, -1, player, -1, -1],
                                     [0, player, player, player, 0],
                                     [-1, -1, player, -1, -1],
                                     [-1, -1, 0, -1, -1]], False, (2, 2)),
        ("PLAYER_CROSS_NEARLY_WIN", [[-1, 0, -1, -1, -1],
                                     [0, player, player, player, 0],
                                     [-1, player, - 1, -1, -1],
                                     [-1, player, - 1, -1, -1],
                                     [-1, 0, -1, -1, -1]], True, (1, 1))
    ]

    one_dimensional_player_pattern_list = [
        ("B_P_P_P_B", [0, player, player, player, 0], False, 3, 30),
        ("B_P_P_B_B", [0, player, player, 0, 0], True, 3, 12),
        ("B_P_B_P_B", [0, player, 0, player, 0], False, 3, 20),
        ("O_P_P_P_P_B", [opponent, player, player, player, player, 0], True, 4, 15),
        ("O_P_P_P_B_B", [opponent, player, player, player, 0, 0], True, 4, 10),
        ("O_P_P_B_B_B", [opponent, player, player, 0, 0, 0], True, 4, 5),
        ("O_P_B_B_B_B", [opponent, player, 0, 0, 0, 0], True, 4, 1)
    ]

    for _, pattern, left_offset in one_dimensional_player_winning_pattern_list:
        if one_dimensional_pattern_match(pattern, chess, False, x, y, left_offset):
            return 100

    for pattern, left_offset, right_offset in one_dimensional_dangerous_pattern_list:
        if one_dimensional_pattern_match(pattern, chess, True, x, y, left_offset, right_offset):
            return 100

    for _, pattern, need_rotate, (anchor_x, anchor_y) in two_dimensional_player_winning_pattern_list:
        if two_dimensional_pattern_match(pattern, chess, need_rotate, x, y, anchor_x, anchor_y):
            return 100

    for pattern, need_rotate, (anchor_x, anchor_y) in two_dimensional_dangerous_pattern_list:
        if two_dimensional_pattern_match(pattern, chess, need_rotate, x, y, anchor_x, anchor_y):
            return 100

    for _, pattern, need_reverse, left_offset, expect_reward in one_dimensional_player_pattern_list:
        reward += expect_reward * one_dimensional_pattern_match(pattern, chess, need_reverse, x, y, left_offset)
    return reward


def has_winner(x: int, y: int, pattern: []) -> bool:
    return one_dimensional_pattern_match(pattern, copy.deepcopy(ai.chess), False, x, y, 4) > 0


def get_1d_matching(pattern: [], chess: [[]], x: int, y: int, l_ofs: int, r_ofs: int) -> int:
    diff = y - x
    rot = x - 22 + y
    bias = 0 if diff <= 0 else abs(diff)
    rot_bias = 0 if rot <= 0 else abs(rot)

    return (int(is_pattern_match([pattern], [numpy.array(chess)[x, y - l_ofs: y + r_ofs]])) +
            int(is_pattern_match([pattern], [numpy.array(chess)[x - l_ofs: x + r_ofs, y]])) +
            int(is_pattern_match([pattern], [numpy.diagonal(chess, offset=diff)[y - bias - l_ofs:y - bias + r_ofs]])) +
            int(is_pattern_match([pattern], [
                numpy.diagonal(numpy.rot90(chess), offset=rot)[x - rot_bias - l_ofs:x - rot_bias + r_ofs]])))


def one_dimensional_pattern_match(pattern: [], chess: [[]], need_reverse: bool, x: int, y: int, l_ofs: int,
                                  *r_offset: int) -> int:
    if len(r_offset) == 0:
        r_ofs = l_ofs + 1
    else:
        r_ofs = r_offset[0]
    number = get_1d_matching(pattern, chess, x, y, l_ofs, r_ofs)
    if need_reverse:
        number += get_1d_matching(list(reversed(pattern)), chess, x, y, r_ofs - 1, l_ofs + 1)
    return number


def get_2d_matching(pattern: [[]], chess: [[]], x: int, y: int, anchor_x: int, anchor_y: int) -> int:
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
        diagonal.append(numpy.diagonal(chess, offset=offset)[i - bias - l_ofs:i - bias + r_ofs])
    anti_diagonal = []
    for i in range(x - u_ofs, x + d_ofs):
        offset = rot + (i - x) * 2
        rot_bias = 0 if offset <= 0 else offset
        anti_diagonal.append(
            numpy.diagonal(numpy.rot90(chess), offset=offset)[i - rot_bias - l_ofs:i - rot_bias + r_ofs])

    return (int(is_pattern_match(pattern, numpy.array(chess)[x - u_ofs: x + d_ofs, y - l_ofs: y + r_ofs])) +
            int(is_pattern_match(pattern, numpy.rot90(chess)[
                                          rot_x - u_ofs: rot_x + d_ofs, rot_y - l_ofs: rot_y + r_ofs])) +
            int(is_pattern_match(pattern, diagonal)) + int(is_pattern_match(pattern, anti_diagonal)))


def two_dimensional_pattern_match(pattern: [[]], chess: [[]], need_rotate: bool, x: int, y: int,
                                  anchor_x: int, anchor_y: int) -> int:
    number = get_2d_matching(pattern, chess, x, y, anchor_x, anchor_y)
    if need_rotate:
        number += get_2d_matching(numpy.rot90(numpy.rot90(pattern)), chess, x, y,
                                  len(pattern) - anchor_x - 1, len(pattern[0]) - anchor_y - 1)
    return number


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
