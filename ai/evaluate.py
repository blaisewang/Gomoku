import copy
import numpy as np
import threading

import ai

chess: [[]]
one_dimensional_player_pattern_list: []
one_dimensional_player_winning_pattern_list: []
two_dimensional_player_winning_pattern_list: [[]]

state_lock = threading.Lock()


def state_function_thread(chess_copy, moves) -> {}:
    global chess
    state_dictionary = {}

    if state_lock.acquire():
        chess = chess_copy
        state_dictionary = get_state(moves)
        state_lock.release()

    return state_dictionary


def get_state(moves) -> {}:
    global one_dimensional_player_pattern_list
    global one_dimensional_player_winning_pattern_list, two_dimensional_player_winning_pattern_list

    player = 1 if moves % 2 == 0 else 2
    opponent = 2 if player == 1 else 1

    pattern_dictionary = {
        "BPPPB": 0,
        "BPPB": 0,
        "BPBPB": 0,
        "OPPPPB": 0,
        "OPPPB": 0,
        "OPPB": 0,
        "OPB": 0,

        "BOOOB": 0,
        "BOOB": 0,
        "BOBOB": 0,
        "POOOOB": 0,
        "POOOB": 0,
        "POOB": 0,
        "POB": 0,

        "P_CROSS": 0,
        "P_V_CROSS": 0,
        "O_CROSS": 0,
        "O_V_CROSS": 0,

        "P_N_WIN": 0,
        "PC_N_WIN": 0,
        "P_WIN": 0,

        "O_N_WIN": 0,
        "OC_N_WIN": 0,
        "O_WIN": 0
    }

    one_dimensional_player_pattern_list = [
        ("BPPPB", [0, player, player, player, 0], False, 3, 50),
        ("BPPB", [0, player, player, 0], False, 2, 40),
        ("BPBPB", [0, player, 0, player, 0], False, 3, 30),
        ("OPPPPB", [opponent, player, player, player, player, 0], True, 4, 20),
        ("OPPPB", [opponent, player, player, player, 0], True, 3, 10),
        ("OPPB", [opponent, player, player, 0], True, 2, 5),
        ("OPB", [opponent, player, 0], True, 1, 1)
    ]

    one_dimensional_opponent_pattern_list = [
        ("BOOOB", [0, opponent, opponent, opponent, 0], False, 3),
        ("BOOB", [0, opponent, opponent, 0], False, 2),
        ("BOBOB", [0, opponent, 0, opponent, 0], False, 3),
        ("POOOOB", [player, opponent, opponent, opponent, opponent, 0], True, 4),
        ("POOOB", [player, opponent, opponent, opponent, 0], True, 3),
        ("POOB", [player, opponent, opponent, 0], True, 2),
        ("POB", [player, opponent, 0], True, 2)
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

    one_dimensional_opponent_winning_pattern_list = [
        ("O_WIN", [opponent, opponent, opponent, opponent, opponent], 4),
        ("O_N_WIN", [opponent, opponent, opponent, opponent, 0], 3),
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

    two_dimensional_opponent_winning_pattern_list = [
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

    for i in range(4, 19):
        for j in range(4, 19):
            if chess[i][j] == player:
                for key, pattern, need_reverse, left_offset, _ in one_dimensional_player_pattern_list:
                    number = one_dimensional_pattern_match(pattern, need_reverse, i, j, left_offset)
                    if number > 0:
                        pattern_dictionary[key] += number
                for key, pattern, left_offset in one_dimensional_player_winning_pattern_list:
                    number = one_dimensional_pattern_match(pattern, False, i, j, left_offset)
                    if number > 0:
                        pattern_dictionary[key] += number
                for key, pattern, need_rotate, (anchor_x, anchor_y) in two_dimensional_player_winning_pattern_list:
                    number = two_dimensional_pattern_match(pattern, need_rotate, i, j, anchor_x, anchor_y)
                    if number > 0:
                        pattern_dictionary[key] += number
            elif chess[i][j] == opponent:
                for key, pattern, need_reverse, left_offset in one_dimensional_opponent_pattern_list:
                    number = one_dimensional_pattern_match(pattern, need_reverse, i, j, left_offset)
                    if number > 0:
                        pattern_dictionary[key] += number
                for key, pattern, left_offset in one_dimensional_opponent_winning_pattern_list:
                    number = one_dimensional_pattern_match(pattern, False, i, j, left_offset)
                    if number > 0:
                        pattern_dictionary[key] += number
                for key, pattern, need_rotate, (
                        anchor_x, anchor_y) in two_dimensional_opponent_winning_pattern_list:
                    number = two_dimensional_pattern_match(pattern, need_rotate, i, j, anchor_x, anchor_y)
                    if number > 0:
                        pattern_dictionary[key] += number
            else:
                for key, pattern, need_rotate, (anchor_x, anchor_y) in two_dimensional_pattern_list:
                    number = two_dimensional_pattern_match(pattern, need_rotate, i, j, anchor_x, anchor_y)
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


def get_reward(x: int, y: int) -> int:
    global chess
    reward = 0
    player = 1 if ai.moves % 2 == 0 else 2
    opponent = 2 if player == 1 else 1
    chess = copy.deepcopy(ai.chess)
    chess[x][y] = player

    one_dimensional_dangerous_pattern_list = [
        ([0, opponent, opponent, opponent, player], 4, 1),
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

    for _, pattern, left_offset in one_dimensional_player_winning_pattern_list:
        if one_dimensional_pattern_match(pattern, False, x, y, left_offset):
            return 100

    for pattern, left_offset, right_offset in one_dimensional_dangerous_pattern_list:
        if one_dimensional_pattern_match(pattern, True, x, y, left_offset, right_offset):
            return 100

    for _, pattern, need_rotate, (anchor_x, anchor_y) in two_dimensional_player_winning_pattern_list:
        if two_dimensional_pattern_match(pattern, need_rotate, x, y, anchor_x, anchor_y):
            return 100

    for pattern, need_rotate, (anchor_x, anchor_y) in two_dimensional_dangerous_pattern_list:
        if two_dimensional_pattern_match(pattern, need_rotate, x, y, anchor_x, anchor_y):
            return 100

    for _, pattern, need_reverse, left_offset, expect_reward in one_dimensional_player_pattern_list:
        reward += expect_reward * one_dimensional_pattern_match(pattern, need_reverse, x, y, left_offset)

    return reward


def has_winner(pattern: [], x, y) -> bool:
    global chess
    chess = ai.chess
    return one_dimensional_pattern_match(pattern, False, x, y, 4) > 0


def get_1d_matching(pattern: [], x: int, y: int, l_ofs: int, r_ofs: int) -> int:
    diff = y - x
    rot = x - 22 + y
    bias = 0 if diff <= 0 else abs(diff)
    rot_bias = 0 if rot <= 0 else abs(rot)

    return (int(is_pattern_match([pattern], [np.array(chess)[x, y - l_ofs: y + r_ofs]])) +
            int(is_pattern_match([pattern], [np.array(chess)[x - l_ofs: x + r_ofs, y]])) +
            int(is_pattern_match([pattern], [np.diagonal(chess, offset=diff)[y - bias - l_ofs:y - bias + r_ofs]])) +
            int(is_pattern_match([pattern], [np.diagonal(np.rot90(chess), offset=rot)[
                                             x - rot_bias - l_ofs:x - rot_bias + r_ofs]])))


def one_dimensional_pattern_match(pattern: [], need_reverse: bool, x: int, y: int, l_ofs: int, *r_offset: int) -> int:
    if len(r_offset) == 0:
        r_ofs = l_ofs + 1
    else:
        r_ofs = r_offset[0]
    number = get_1d_matching(pattern, x, y, l_ofs, r_ofs)
    if need_reverse:
        number += get_1d_matching(list(reversed(pattern)), x, y, r_ofs - 1, l_ofs + 1)
    return number


def get_2d_matching(pattern: [[]], x: int, y: int, anchor_x: int, anchor_y: int) -> int:
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
        diagonal.append(np.diagonal(chess, offset=offset)[i - bias - l_ofs:i - bias + r_ofs])
    anti_diagonal = []
    for i in range(x - u_ofs, x + d_ofs):
        offset = rot + (i - x) * 2
        rot_bias = 0 if offset <= 0 else offset
        anti_diagonal.append(np.diagonal(np.rot90(chess), offset=offset)[i - rot_bias - l_ofs:i - rot_bias + r_ofs])

    return (int(is_pattern_match(pattern, np.array(chess)[x - u_ofs: x + d_ofs, y - l_ofs: y + r_ofs])) +
            int(is_pattern_match(pattern,
                                 np.rot90(chess)[rot_x - u_ofs: rot_x + d_ofs, rot_y - l_ofs: rot_y + r_ofs])) +
            int(is_pattern_match(pattern, diagonal)) + int(is_pattern_match(pattern, anti_diagonal)))


def two_dimensional_pattern_match(pattern: [[]], need_rotate: bool, x: int, y: int,
                                  anchor_x: int, anchor_y: int) -> int:
    number = get_2d_matching(pattern, x, y, anchor_x, anchor_y)
    if need_rotate:
        number += get_2d_matching(np.rot90(np.rot90(pattern)), x, y, len(pattern) - anchor_x - 1,
                                  len(pattern[0]) - anchor_y - 1)
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
