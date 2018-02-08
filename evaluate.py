import numpy as np

n = 0
chess = np.zeros(0)


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


def one_dimensional_pattern_match(pattern: [], need_reverse: bool, x: int, y: int, l_ofs: int, *r_offset: int) -> int:
    if len(r_offset) == 0:
        r_ofs = l_ofs + 1
    else:
        r_ofs = r_offset[0]
    number = get_1d_matching(pattern, x, y, l_ofs, r_ofs)
    if need_reverse:
        number += get_1d_matching(list(reversed(pattern)), x, y, r_ofs - 1, l_ofs + 1)
    return number


def get_2d_matching(pattern: [[]], x: int, y: int, anchor_x: int, anchor_y: int):
    diff = y - x
    u_ofs = anchor_y
    d_ofs = len(pattern) - anchor_y
    l_ofs = anchor_x
    r_ofs = len(pattern[0]) - anchor_x
    rot_x = n - y - 1
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


def two_dimensional_pattern_match(pattern: [[]], need_rotate: bool, x: int, y: int, anchor_x: int, anchor_y: int):
    number = get_2d_matching(pattern, x, y, anchor_x, anchor_y)
    if need_rotate:
        number += get_2d_matching(np.rot90(np.rot90(pattern)), x, y, len(pattern) - anchor_x - 1,
                                  len(pattern[0]) - anchor_y - 1)
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
