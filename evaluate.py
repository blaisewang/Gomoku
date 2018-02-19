import numpy as np

n = 0
chess = np.zeros(0)


def get_state(chess_list, moves: int):
    global n, chess
    n = len(chess_list)
    chess = chess_list

    p = 2 if moves % 2 == 0 else 1
    o = 2 if p == 1 else 1

    pattern_dictionary = {
        "P_P_P_P_P": 0,
        "B_P_P_P_P_B": 0,
        "B_P_P_P_B": 0,
        "B_P_P_B_B": 0,
        "B_P_B_P_B": 0,
        "B_P_B": 0,
        "O_P_P_P_P_B": 0,
        "O_P_P_P_B_B": 0,
        "O_P_P_B_B_B": 0,
        "O_P_B_B_B_B": 0,

        "O_O_O_O_O": 0,
        "O_O_O_O_B": 0,
        "B_O_O_O_B": 0,
        "B_O_O_B_B": 0,
        "B_O_B_O_B": 0,
        "B_O_B": 0,
        "P_O_O_O_O_B": 0,
        "P_O_O_O_B_B": 0,
        "P_O_O_B_B_B": 0,
        "P_O_B_B_B_B": 0
    }

    one_dimensional_player_pattern_list = [
        ("P_P_P_P_P", [p, p, p, p, p], False, 4),
        ("B_P_P_P_P_B", [0, p, p, p, p, 0], False, 4),
        ("B_P_P_P_B", [0, p, p, p, 0], False, 3),
        ("B_P_P_B_B", [0, p, p, 0, 0], True, 3),
        ("B_P_B_P_B", [0, p, 0, p, 0], False, 3),
        ("O_P_P_P_P_B", [o, p, p, p, p, 0], True, 4),
        ("O_P_P_P_B_B", [o, p, p, p, 0, 0], True, 4),
        ("O_P_P_B_B_B", [o, p, p, 0, 0, 0], True, 4),
        ("O_P_B_B_B_B", [o, p, 0, 0, 0, 0], True, 4)
    ]

    one_dimensional_opponent_pattern_list = [
        ("O_O_O_O_O", [o, o, o, o, o], False, 4),
        ("O_O_O_O_B", [o, o, o, o, 0], True, 4),
        ("B_O_O_O_B", [0, o, o, o, 0], False, 3),
        ("B_O_O_B_B", [0, o, o, 0, 0], True, 3),
        ("B_O_B_O_B", [0, o, 0, o, 0], False, 3),
        ("P_O_O_O_O_B", [p, o, o, o, o, 0], True, 4),
        ("P_O_O_O_B_B", [p, o, o, o, 0, 0], True, 4),
        ("P_O_O_B_B_B", [p, o, o, 0, 0, 0], True, 4),
        ("P_O_B_B_B_B", [p, o, 0, 0, 0, 0], True, 4)
    ]

    two_dimensional_player_pattern_list = [
        ("B_P_B", [[0, 0, 0],
                   [0, p, 0],
                   [0, 0, 0]], False, (1, 1)),
        ("B_P_B", [[-2, 0, 0],
                   [-2, p, 0],
                   [-2, 0, 0]], True, (1, 1)),
        ("B_P_B", [[-2, 0, 0],
                   [-2, p, 0],
                   [-2, -2, -2]], True, (1, 1))
    ]

    two_dimensional_opponent_pattern_list = [
        ("B_O_B", [[0, 0, 0],
                   [0, o, 0],
                   [0, 0, 0]], False, (1, 1)),
        ("B_O_B", [[-2, 0, 0],
                   [-2, o, 0],
                   [-2, 0, 0]], True, (1, 1)),
        ("B_O_B", [[-2, 0, 0],
                   [-2, o, 0],
                   [-2, -2, -2]], True, (1, 1))
    ]

    for (x, y), value in np.ndenumerate(chess[4:n + 4, 4:n + 4]):
        if value == p:
            for key, pattern, need_reverse, left_offset in one_dimensional_player_pattern_list:
                pattern_dictionary[key] += one_dimensional_pattern_match(pattern, need_reverse, x + 4, y + 4,
                                                                         left_offset)
            for key, pattern, need_rotate, (anchor_x, anchor_y) in two_dimensional_player_pattern_list:
                pattern_dictionary[key] += two_dimensional_pattern_match(pattern, need_rotate, x + 4, y + 4,
                                                                         anchor_x, anchor_y)
        elif value == o:
            for key, pattern, need_reverse, left_offset in one_dimensional_opponent_pattern_list:
                pattern_dictionary[key] += one_dimensional_pattern_match(pattern, need_reverse, x + 4, y + 4,
                                                                         left_offset)
            for key, pattern, need_rotate, (anchor_x, anchor_y) in two_dimensional_opponent_pattern_list:
                pattern_dictionary[key] += two_dimensional_pattern_match(pattern, need_rotate, x + 4, y + 4,
                                                                         anchor_x, anchor_y)
    return list(pattern_dictionary.values())


def has_winner(x: int, y: int, player: int, chess_list):
    global n, chess
    n = len(chess_list)
    chess = chess_list
    return one_dimensional_pattern_match([player, player, player, player, player], False, x, y, 4) > 0


def get_1d_matching(pattern: [], x: int, y: int, l_ofs: int, r_ofs: int):
    diff = y - x
    rot = x - (n - 1) + y
    bias = 0 if diff <= 0 else abs(diff)
    rot_bias = 0 if rot <= 0 else abs(rot)

    return (int(is_pattern_match([pattern], [chess[x, y - l_ofs: y + r_ofs]])) +
            int(is_pattern_match([pattern], [chess[x - l_ofs: x + r_ofs, y]])) +
            int(is_pattern_match([pattern], [np.diagonal(chess, offset=diff)[y - bias - l_ofs:y - bias + r_ofs]])) +
            int(is_pattern_match([pattern], [
                np.diagonal(np.rot90(chess), offset=rot)[x - rot_bias - l_ofs:x - rot_bias + r_ofs]])))


def one_dimensional_pattern_match(pattern: [], need_reverse: bool, x: int, y: int, l_ofs: int) -> int:
    number = get_1d_matching(pattern, x, y, l_ofs, l_ofs + 1)
    if need_reverse:
        number += get_1d_matching(list(reversed(pattern)), x, y, l_ofs, l_ofs + 1)
    return number


def get_2d_matching(pattern: [[]], x: int, y: int, anchor_x: int, anchor_y: int):
    u_ofs = anchor_y
    d_ofs = len(pattern) - anchor_y
    l_ofs = anchor_x
    r_ofs = len(pattern[0]) - anchor_x
    rot_x = n - y - 1
    rot_y = x

    return (int(is_pattern_match(pattern, np.array(chess)[x - u_ofs: x + d_ofs, y - l_ofs: y + r_ofs])) +
            int(is_pattern_match(pattern, np.rot90(chess)[rot_x - u_ofs: rot_x + d_ofs, rot_y - l_ofs: rot_y + r_ofs])))


def two_dimensional_pattern_match(pattern: [[]], need_rotate: bool, x: int, y: int, anchor_x: int, anchor_y: int):
    number = get_2d_matching(pattern, x, y, anchor_x, anchor_y)
    if need_rotate:
        number += get_2d_matching(np.rot90(pattern, 2), x, y, len(pattern[0]) - anchor_x - 1,
                                  len(pattern) - anchor_y - 1)
    return number


def is_pattern_match(pattern: [[]], array: [[]]):
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
