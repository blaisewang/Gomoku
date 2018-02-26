import numpy as np

n = 0
chess = np.zeros(0)


def get_state(chess_list, moves: int):
    global n, chess
    n = len(chess_list)
    chess = chess_list

    p = 1 if moves % 2 == 0 else 2
    o = 2 if p == 1 else 1

    pattern_dictionary = {
        "B_P_P_P_P_B": 0,
        "B_P_P_P_B": 0,
        "B_P_P_B_B": 0,
        "B_P_B_P_B": 0,
        "B_B_P_B_B": 0,
        "H_P_P_P_P_B": 0,
        "H_P_P_P_B_B": 0,
        "H_P_P_B_B_B": 0,
        "H_P_B_P_B_B": 0,
        "H_B_P_B_B_B": 0,
        "H_P_B_B_B_B": 0,


        "O_O_O_O_O": 0,
        "O_O_O_O_B": 0,
        "B_O_O_O_B": 0,
        "B_O_O_B_B": 0,
        "B_O_B_O_B": 0,
        "B_B_O_B_B": 0,
        "H_O_O_O_B_B": 0,
        "H_O_O_B_B_B": 0,
        "H_O_B_O_B_B": 0,
        "H_B_O_B_B_B": 0,
        "H_O_B_B_B_B": 0
    }

    player_pattern_list = [
        ("B_P_P_P_P_B", [0, p, p, p, p, 0], False, 4),
        ("B_P_P_P_B", [0, p, p, p, 0], False, 3),
        ("B_P_P_B_B", [0, p, p, 0, 0], True, 3),
        ("B_P_B_P_B", [0, p, 0, p, 0], False, 3),
        ("B_B_P_B_B", [0, 0, p, 0, 0], False, 2),
        ("H_P_P_P_P_B", [o, p, p, p, p, 0], True, 4),
        ("H_P_P_P_P_B", [-2, p, p, p, p, 0], True, 4),
        ("H_P_P_P_B_B", [o, p, p, p, 0, 0], True, 4),
        ("H_P_P_P_B_B", [-2, p, p, p, 0, 0], True, 4),
        ("H_P_P_B_B_B", [o, p, p, 0, 0, 0], True, 4),
        ("H_P_P_B_B_B", [-2, p, p, 0, 0, 0], True, 4),
        ("H_P_B_P_B_B", [o, p, 0, p, 0, 0], True, 4),
        ("H_P_B_P_B_B", [-2, p, 0, p, 0, 0], True, 4),
        ("H_B_P_B_B_B", [p, 0, p, 0, 0, 0], True, 3),
        ("H_B_P_B_B_B", [-2, 0, p, 0, 0, 0], True, 3),
        ("H_P_B_B_B_B", [o, p, 0, 0, 0, 0], True, 4),
        ("H_P_B_B_B_B", [-2, p, 0, 0, 0, 0], True, 4)
    ]

    opponent_pattern_list = [
        ("O_O_O_O_O", [o, o, o, o, o], False, 4),
        ("O_O_O_O_B", [o, o, o, o, 0], True, 4),
        ("B_O_O_O_B", [0, o, o, o, 0], False, 3),
        ("B_O_O_B_B", [0, o, o, 0, 0], True, 3),
        ("B_O_B_O_B", [0, o, 0, o, 0], False, 3),
        ("B_B_O_B_B", [0, 0, o, 0, 0], False, 2),
        ("H_O_O_O_B_B", [p, o, o, o, 0, 0], True, 4),
        ("H_O_O_O_B_B", [-2, o, o, o, 0, 0], True, 4),
        ("H_O_O_B_B_B", [p, o, o, 0, 0, 0], True, 4),
        ("H_O_O_B_B_B", [-2, o, o, 0, 0, 0], True, 4),
        ("H_O_B_O_B_B", [p, o, 0, o, 0, 0], True, 4),
        ("H_O_B_O_B_B", [-2, o, 0, o, 0, 0], True, 4),
        ("H_B_O_B_B_B", [p, 0, o, 0, 0, 0], True, 3),
        ("H_B_O_B_B_B", [-2, 0, o, 0, 0, 0], True, 3),
        ("H_O_B_B_B_B", [p, o, 0, 0, 0, 0], True, 4),
        ("H_O_B_B_B_B", [-2, o, 0, 0, 0, 0], True, 4)
    ]

    for (x, y), value in np.ndenumerate(chess[4:n + 4, 4:n + 4]):
        if value == p:
            for key, pattern, need_reverse, left_offset in player_pattern_list:
                pattern_dictionary[key] += get_pattern_match(pattern, need_reverse, x + 4, y + 4, left_offset)
        elif value == o:
            for key, pattern, need_reverse, left_offset in opponent_pattern_list:
                pattern_dictionary[key] += get_pattern_match(pattern, need_reverse, x + 4, y + 4, left_offset)
    return list(pattern_dictionary.values())


def has_winner(x: int, y: int, player: int, chess_list):
    global n, chess
    n = len(chess_list)
    chess = chess_list
    return get_pattern_match([player, player, player, player, player], False, x, y, 4) > 0


def get_matching(pattern: [], x: int, y: int, l_ofs: int, r_ofs: int):
    diff = y - x
    rot = x - (n - 1) + y
    bias = 0 if diff <= 0 else abs(diff)
    rot_bias = 0 if rot <= 0 else abs(rot)

    return (int(is_pattern_match([pattern], [chess[x, y - l_ofs: y + r_ofs]])) +
            int(is_pattern_match([pattern], [chess[x - l_ofs: x + r_ofs, y]])) +
            int(is_pattern_match([pattern], [np.diagonal(chess, offset=diff)[y - bias - l_ofs:y - bias + r_ofs]])) +
            int(is_pattern_match([pattern], [
                np.diagonal(np.rot90(chess), offset=rot)[x - rot_bias - l_ofs:x - rot_bias + r_ofs]])))


def get_pattern_match(pattern: [], need_reverse: bool, x: int, y: int, l_ofs: int) -> int:
    number = get_matching(pattern, x, y, l_ofs, l_ofs + 1)
    if need_reverse:
        number += get_matching(list(reversed(pattern)), x, y, l_ofs, l_ofs + 1)
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
