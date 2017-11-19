import ai

import math
import numpy
import random


def next_move() -> (int, int):
    key = ai.get_chess_key()
    if len(ai.weight_dictionary) == 0:
        weight = ai.null_weight.copy()
        weight[7][7] = 1.0
        ai.weight_dictionary[key] = weight
        return 7, 7
    else:
        weight_array: [(int, int)] = []
        max_weight = numpy.max(ai.weight_dictionary[key])
        for i in range(15):
            for j in range(15):
                if abs(ai.weight_dictionary[key][i][j] - max_weight) < 0.1:
                    weight_array.append((i, j))
        x, y = weight_array[random.randint(0, len(weight_array) - 1)]
        if ai.moves % 2 == 0 and ai.moves > 1:
            ai.black_key_record.append((key, (x, y)))
        else:
            ai.white_key_record.append((key, (x, y)))
        return x, y


def update_weight(winner: int):
    penalty_factor = 0.1
    reward_factor = 0.05
    if winner == 1:
        length = len(ai.white_key_record)
        for i in range(length):
            key, (x, y) = ai.white_key_record[length - i - 1]
            ai.weight_dictionary[key][x][y] -= bias_function(i)
        length = len(ai.black_key_record)
        for i in range(length):
            key, (x, y) = ai.black_key_record[length - i - 1]
            ai.weight_dictionary[key][x][y] += reward_factor * bias_function(i)
    elif winner == 2:
        length = len(ai.black_key_record)
        for i in range(length):
            key, (x, y) = ai.black_key_record[length - i - 1]
            ai.weight_dictionary[key][x][y] -= bias_function(i)
        length = len(ai.white_key_record)
        for i in range(length):
            key, (x, y) = ai.white_key_record[length - i - 1]
            ai.weight_dictionary[key][x][y] += reward_factor * bias_function(i)
    else:
        length = len(ai.white_key_record)
        for i in range(length):
            key, (x, y) = ai.white_key_record[length - i - 1]
            ai.weight_dictionary[key][x][y] -= penalty_factor * bias_function(i)
        length = len(ai.black_key_record)
        for i in range(length):
            key, (x, y) = ai.black_key_record[length - i - 1]
            ai.weight_dictionary[key][x][y] -= penalty_factor * bias_function(i)


def bias_function(step: int) -> float:
    eta = 0.2
    return 1 - 2 / math.pi * math.atan(math.pi / 2 * eta * step)
