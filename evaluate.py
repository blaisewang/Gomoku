import numpy as np


def get_state(chess) -> ():
    n = len(chess)

    black_pattern_dictionary = {
        (1, 1, 1, 1, 1): 0,
        (1, 1, 1, 1, 0): 0,
        (1, 1, 1, 0, 1): 0,
        (1, 1, 0, 1, 1): 0,
        (0, 1, 1, 1, 0): 0,
        (1, 1, 1, 0, 0): 0,
        (1, 1, 0, 1, 0): 0,
        (1, 1, 0, 0, 1): 0,
        (0, 1, 1, 0, 1): 0,
        (1, 0, 1, 0, 1): 0,
        (0, 1, 1, 0, 0): 0,
        (0, 1, 0, 1, 0): 0,
        (1, 1, 0, 0, 0): 0,
        (1, 0, 1, 0, 0): 0,
        (1, 0, 0, 1, 0): 0,
        (1, 0, 0, 0, 1): 0,
        (0, 0, 1, 0, 0): 0,
        (0, 1, 0, 0, 0): 0,
        (1, 0, 0, 0, 0): 0
    }

    white_pattern_dictionary = {
        (2, 2, 2, 2, 2): 0,
        (2, 2, 2, 2, 0): 0,
        (2, 2, 2, 0, 2): 0,
        (2, 2, 0, 2, 2): 0,
        (0, 2, 2, 2, 0): 0,
        (2, 2, 2, 0, 0): 0,
        (2, 2, 0, 2, 0): 0,
        (2, 2, 0, 0, 2): 0,
        (0, 2, 2, 0, 2): 0,
        (2, 0, 2, 0, 2): 0,
        (0, 2, 2, 0, 0): 0,
        (0, 2, 0, 2, 0): 0,
        (2, 2, 0, 0, 0): 0,
        (2, 0, 2, 0, 0): 0,
        (2, 0, 0, 2, 0): 0,
        (2, 0, 0, 0, 2): 0,
        (0, 0, 2, 0, 0): 0,
        (0, 2, 0, 0, 0): 0,
        (2, 0, 0, 0, 0): 0
    }

    for (x, y), v in np.ndenumerate(chess[4:n + 4, 4:n + 4]):
        x += 4
        y += 4
        diff = y - x
        rot = x - (n - 1) + y
        bias = max(0, diff)
        rot_bias = max(0, rot)
        if v == 1 or v == 2:
            for array in [chess[x, y - 4: y + 5], chess[x - 4: x + 5, y],
                          np.diagonal(chess, diff)[y - bias - 4:y - bias + 5],
                          np.diagonal(np.rot90(chess), rot)[x - rot_bias - 4:x - rot_bias + 5]]:
                for i in range(5):
                    similarity = 0
                    for j in range(5):
                        if array[i + j] != v and array[i + j] != 0:
                            break
                        similarity += 1
                    if similarity == 5:
                        key = tuple(array[i:i + 5])
                        if v == 1:
                            if key in black_pattern_dictionary:
                                black_pattern_dictionary[key] += 1
                            else:
                                black_pattern_dictionary[key[::-1]] += 1
                        else:
                            if key in white_pattern_dictionary:
                                white_pattern_dictionary[key] += 1
                            else:
                                white_pattern_dictionary[key[::-1]] += 1
    return list(black_pattern_dictionary.values()), list(white_pattern_dictionary.values())


def has_winner(chess, x: int, y: int) -> bool:
    diff = y - x
    rot = x - (len(chess) - 1) + y
    bias = max(0, diff)
    rot_bias = max(0, rot)

    for array in [chess[x, y - 4: y + 5], chess[x - 4: x + 5, y],
                  np.diagonal(chess, diff)[y - bias - 4:y - bias + 5],
                  np.diagonal(np.rot90(chess), rot)[x - rot_bias - 4:x - rot_bias + 5]]:
        for i in range(5):
            similarity = 0
            for j in range(5):
                if array[i + j] != chess[x, y]:
                    break
                similarity += 1
            if similarity == 5:
                return True
    return False
