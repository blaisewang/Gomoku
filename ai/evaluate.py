import ai

import numpy as np

player = 0
opponent = 0
chess: [[]]
diff = 0
abs_diff = 0


def evaluation(x: int, y: int) -> int:
    global player, opponent, chess, diff, abs_diff
    player = 1 if ai.moves % 2 == 0 else 0
    opponent = 2 if player == 1 else 1
    chess = ai.chess[:]
    chess[x][y] = player
    diff = y - x
    abs_diff = abs(diff)
    reward = 0

    pattern = [player, player, player, player, player]
    if is_one_dimensional_pattern_match(pattern, x, y, 4):
        return 100

    pattern = [0, player, player, player, player, 0]
    if is_one_dimensional_pattern_match(pattern, x, y, 4):
        return 100

    pattern = [0, player, player, player, 0]
    if is_one_dimensional_cross_pattern_match(pattern, x, y, 3):
        return 100

    if reward < 50:
        pattern = [0, player, player, player, 0]
        if is_one_dimensional_pattern_match(pattern, x, y, 4):
            reward = 50

    if reward < 40:
        pattern = [0, player, player, 0]
        if is_one_dimensional_pattern_match(pattern, x, y, 2):
            reward = 40

    if reward < 30:
        pattern = [0, player, 0, player, 0]
        if is_one_dimensional_pattern_match(pattern, x, y, 3):
            reward = 30

    if reward < 20:
        pattern = [opponent, player, player, player, player, 0]
        if is_one_dimensional_pattern_match(pattern, x, y, 4):
            reward = 20

    if reward < 20:
        pattern = [0, player, player, player, player, opponent]
        if is_one_dimensional_pattern_match(pattern, x, y, 4):
            reward = 20

    if reward < 10:
        pattern = [opponent, player, player, player, 0]
        if is_one_dimensional_pattern_match(pattern, x, y, 3):
            reward = 10

    if reward < 10:
        pattern = [0, player, player, player, opponent]
        if is_one_dimensional_pattern_match(pattern, x, y, 3):
            reward = 10

    if reward < 1:
        pattern = [opponent, player, player, 0]
        if is_one_dimensional_pattern_match(pattern, x, y, 2):
            reward = 1

    if reward < 1:
        pattern = [0, player, player, opponent]
        if is_one_dimensional_pattern_match(pattern, x, y, 2):
            reward = 1

    return reward


def has_winner(pattern: [], x, y) -> bool:
    global chess
    chess = ai.chess
    return is_one_dimensional_pattern_match(pattern, x, y, 4)


def is_one_dimensional_pattern_match(pattern: [], x: int, y: int, l_ofs: int) -> bool:
    r_off = l_ofs + 1
    rot = x - 22 + y
    return (is_pattern_match(pattern, np.array(chess)[x, y - l_ofs: y + r_off]) or
            is_pattern_match(pattern, np.array(chess)[x - l_ofs: x + r_off, y]) or
            is_pattern_match(pattern,
                             np.diagonal(chess, offset=diff)[y - abs_diff - l_ofs:y - abs_diff + r_off]) or
            is_pattern_match(pattern,
                             np.diagonal(np.rot90(chess), offset=rot)[x - abs(rot) - l_ofs:x - abs(rot) + r_off]))


def is_one_dimensional_cross_pattern_match(pattern: [], x: int, y: int, l_ofs: int) -> bool:
    r_ofs = l_ofs + 1
    rot = x - 22 + y
    return (is_pattern_match(pattern, np.array(chess)[x, y - l_ofs: y + r_ofs]) and
            is_pattern_match(pattern, np.array(chess)[x - l_ofs: x + r_ofs, y])) or \
           (is_pattern_match(pattern,
                             np.diagonal(chess, offset=diff)[y - abs_diff - l_ofs:y - abs_diff + r_ofs]) and
            is_pattern_match(pattern,
                             np.diagonal(np.rot90(chess), offset=rot)[x - abs(rot) - l_ofs:x - abs(rot) + r_ofs]))


def is_pattern_match(pattern: [], array: []) -> bool:
    pattern_length = len(pattern)
    array_length = len(array)

    flag = False
    for i in range(array_length - pattern_length + 1):
        similarity = 0
        for j in range(pattern_length):
            if pattern[j] != array[i + j] and pattern[j] != -1:
                break
            similarity += 1
        if similarity == pattern_length:
            flag = True
            break
    return flag
