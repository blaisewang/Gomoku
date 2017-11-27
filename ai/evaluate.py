import numpy as np

import ai

chess: [[]]


def evaluation(x: int, y: int) -> int:
    global chess
    reward = 0
    player = 1 if ai.moves % 2 == 0 else 0
    opponent = 2 if player == 1 else 1
    chess = ai.chess[:]
    chess[x][y] = player

    one_dimensional_winning_pattern_list = [
        ([player, player, player, player, player], 4),
        ([player, opponent, opponent, opponent, opponent, player], 5),
        ([0, player, player, player, player, 0], 4),
    ]

    one_dimensional_important_pattern_list = [
        ([0, opponent, opponent, opponent, player], 4, 1),
        ([player, opponent, opponent, opponent, 0], 0, 5)
    ]

    two_dimensional_winning_pattern_list = [
        ([[-1, -1, 0, -1, -1],
          [-1, -1, player, -1, -1],
          [0, player, player, player, 0],
          [-1, -1, player, -1, -1],
          [-1, -1, 0, -1, -1]], 2, 2),

        ([[-1, -1, -1, 0, -1],
          [-1, -1, -1, player, -1],
          [-1, -1, -1, player, -1],
          [0, player, player, player, 0],
          [-1, -1, -1, 0, -1]], 3, 3),

        ([[-1, 0, -1, -1, -1],
          [-1, player, - 1, -1, -1],
          [-1, player, - 1, -1, -1],
          [0, player, player, player, 0],
          [-1, 0, -1, -1, -1]], 3, 1),

        ([[-1, -1, -1, 0, -1],
          [0, player, player, player, 0],
          [-1, -1, -1, player, -1],
          [-1, -1, -1, player, -1],
          [-1, -1, -1, 0, -1]], 1, 3),

        ([[-1, 0, -1, -1, -1],
          [0, player, player, player, 0],
          [-1, player, - 1, -1, -1],
          [-1, player, - 1, -1, -1],
          [-1, 0, -1, -1, -1]], 1, 1)
    ]

    two_dimensional_important_pattern_list = [
        ([[-1, -1, 0, -1, -1],
          [-1, -1, opponent, -1, -1],
          [0, opponent, player, opponent, 0],
          [-1, -1, opponent, -1, -1],
          [-1, -1, 0, -1, -1]], 2, 2),

        ([[-1, -1, -1, 0, -1],
          [-1, -1, -1, opponent, -1],
          [-1, -1, -1, opponent, -1],
          [0, opponent, opponent, player, 0],
          [-1, -1, -1, 0, -1]], 3, 3),

        ([[-1, 0, -1, -1, -1],
          [-1, opponent, - 1, -1, -1],
          [-1, opponent, - 1, -1, -1],
          [0, player, opponent, opponent, 0],
          [-1, 0, -1, -1, -1]], 3, 1),

        ([[-1, -1, -1, 0, -1],
          [0, opponent, opponent, player, 0],
          [-1, -1, -1, opponent, -1],
          [-1, -1, -1, opponent, -1],
          [-1, -1, -1, 0, -1]], 1, 3),

        ([[-1, 0, -1, -1, -1],
          [0, player, opponent, opponent, 0],
          [-1, opponent, - 1, -1, -1],
          [-1, opponent, - 1, -1, -1],
          [-1, 0, -1, -1, -1]], 1, 1)
    ]

    one_dimensional_pattern_list = [
        ([0, player, player, player, 0], 50, 3),
        ([0, player, player, 0], 40, 2),
        ([0, player, 0, player, 0], 30, 3),
        ([opponent, player, player, player, player, 0], 20, 4),
        ([0, player, player, player, player, opponent], 20, 4),
        ([opponent, player, player, player, 0], 10, 3),
        ([0, player, player, player, opponent], 10, 3),
        ([opponent, player, player, 0], 1, 2),
        ([0, player, player, opponent], 1, 2)
    ]

    for pattern, left_offset in one_dimensional_winning_pattern_list:
        if is_one_dimensional_pattern_match(pattern, x, y, left_offset):
            return 200

    for pattern, left_offset, right_offset in one_dimensional_important_pattern_list:
        if is_one_dimensional_pattern_match(pattern, x, y, left_offset, right_offset):
            return 200

    for pattern, anchor_x, anchor_y in two_dimensional_winning_pattern_list:
        if is_two_dimensional_pattern_match(pattern, x, y, anchor_x, anchor_y):
            return 200

    for pattern, anchor_x, anchor_y in two_dimensional_important_pattern_list:
        if is_two_dimensional_pattern_match(pattern, x, y, anchor_x, anchor_y):
            return 200

    for pattern, expect_reward, left_offset in one_dimensional_pattern_list:
        reward += expect_reward * is_one_dimensional_pattern_match(pattern, x, y, left_offset)

    return reward


def has_winner(pattern: [], x, y) -> bool:
    global chess
    chess = ai.chess
    return is_one_dimensional_pattern_match(pattern, x, y, 4) > 0


def is_one_dimensional_pattern_match(pattern: [], x: int, y: int, l_ofs: int, *r_offset: int) -> int:
    diff = y - x
    rot = x - 22 + y
    bias = 0 if diff <= 0 else abs(diff)
    rot_bias = 0 if rot <= 0 else abs(rot)
    if len(r_offset) == 0:
        r_ofs = l_ofs + 1
    else:
        r_ofs = r_offset[0]

    return (int(is_pattern_match([pattern], [np.array(ai.chess)[x, y - l_ofs: y + r_ofs]])) +
            int(is_pattern_match([pattern], [np.array(ai.chess)[x - l_ofs: x + r_ofs, y]])) +
            int(is_pattern_match([pattern],
                                 [np.diagonal(ai.chess, offset=diff)[y - bias - l_ofs:y - bias + r_ofs]])) +
            int(is_pattern_match([pattern],
                                 [np.diagonal(np.rot90(ai.chess), offset=rot)[
                                  x - rot_bias - l_ofs:x - rot_bias + r_ofs]])))


def is_two_dimensional_pattern_match(pattern: [[]], x: int, y: int, anchor_x: int, anchor_y: int) -> int:
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
        diagonal.append(np.diagonal(ai.chess, offset=offset)[i - bias - l_ofs:i - bias + r_ofs])

    anti_diagonal = []
    for i in range(x - u_ofs, x + d_ofs):
        offset = rot + (i - x) * 2
        rot_bias = 0 if offset <= 0 else offset
        anti_diagonal.append(np.diagonal(np.rot90(ai.chess), offset=offset)[i - rot_bias - l_ofs:i - rot_bias + r_ofs])

    return (
        int(is_pattern_match(pattern, np.array(ai.chess)[x - u_ofs: x + d_ofs, y - l_ofs: y + r_ofs])) +
        int(is_pattern_match(pattern, np.rot90(ai.chess)[rot_x - u_ofs: rot_x + d_ofs, rot_y - l_ofs: rot_y + r_ofs])) +
        int(is_pattern_match(pattern, diagonal)) + int(is_pattern_match(pattern, anti_diagonal)))


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
