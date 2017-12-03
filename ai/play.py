import copy
import math
import numpy as np
import random
import threading

import time

import ai

epsilon = 0.01
gamma = 0.8

chess: [[]]
next_state: {}
next_move_result: []
potential_q_result: []


def get_next_move_result(args) -> ():
    state, reward = ai.evaluate.StateAndReward(copy.deepcopy(chess), args, ai.moves, True).get_state_and_reward()
    q_value = 0.0
    if state in ai.state_list:
        q_value = ai.q_matrix[ai.state_list.index(ai.last_state), ai.state_list.index(state)]
    next_move_result.append((args, state, q_value, reward))


def get_potential_q_result(args):
    state, _ = ai.evaluate.StateAndReward(copy.deepcopy(chess), args, ai.moves + 1, True).get_state_and_reward()
    q_value = 0.0
    if state in ai.state_list:
        q_value = ai.q_matrix[ai.state_list.index(next_state), ai.state_list.index(state)]
    potential_q_result.append(q_value)


def next_move(is_training: bool) -> (int, int):
    s = time.time()
    global chess, next_state, next_move_result, potential_q_result
    next_move_result = []
    potential_q_result = []
    next_state = {}

    if ai.moves == 0:
        return 11, 11
    else:
        greedy = True
        chess = copy.deepcopy(ai.chess)
        next_move_list = ai.get_boundary(chess)

        threads = []
        for x, y in next_move_list:
            thread = threading.Thread(target=get_next_move_result, args=((x, y),))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

        if is_training:
            if random.randint(1, 100) <= epsilon * 100:
                greedy = False
        if greedy:
            max_q = 0.0
            potential_next_move_greedy_result = []
            for _, _, q_value, _ in next_move_result:
                max_q = q_value if q_value > max_q else max_q
            for (x, y), state, q_value, reward in next_move_result:
                if q_value == max_q:
                    potential_next_move_greedy_result.append(((x, y), state, q_value, reward))
            (next_x, next_y), next_s, next_q, next_r = potential_next_move_greedy_result[
                random.randint(0, len(potential_next_move_greedy_result) - 1)]
        else:
            (next_x, next_y), next_state, next_q, next_r = next_move_result[
                random.randint(0, len(next_move_result) - 1)]

        if next_state not in ai.state_list:
            ai.q_matrix = np.row_stack((ai.q_matrix, np.zeros(len(ai.state_list))))
            ai.state_list.append(next_state)
            ai.q_matrix = np.column_stack((ai.q_matrix, np.zeros((len(ai.state_list), 1))))

        chess[next_x][next_y] = 2 if (ai.moves + 1) % 2 == 0 else 1
        potential_move_list = ai.get_boundary(chess)

        threads = []
        for x, y in potential_move_list:
            thread = threading.Thread(target=get_potential_q_result, args=((x, y),))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

        ai.q_matrix[ai.state_list.index(ai.last_state), ai.state_list.index(next_state)] = next_r + gamma * max(
            potential_q_result)
        ai.last_state = next_state

        print(time.time() - s)
        return 1, 1


#
#
# def update_weight(winner: int):
#     penalty_factor = 0.1
#     reward_factor = 0.5
#     if winner == 1:
#         length = len(ai.white_key_record)
#         for i in range(length):
#             key, (x, y) = ai.white_key_record[length - i - 1]
#             ai.weight_dictionary[key][x][y] -= bias_function(i)
#         length = len(ai.black_key_record)
#         for i in range(length):
#             key, (x, y) = ai.black_key_record[length - i - 1]
#             ai.weight_dictionary[key][x][y] += reward_factor * bias_function(i)
#     elif winner == 2:
#         length = len(ai.black_key_record)
#         for i in range(length):
#             key, (x, y) = ai.black_key_record[length - i - 1]
#             ai.weight_dictionary[key][x][y] -= bias_function(i)
#         length = len(ai.white_key_record)
#         for i in range(length):
#             key, (x, y) = ai.white_key_record[length - i - 1]
#             ai.weight_dictionary[key][x][y] += reward_factor * bias_function(i)
#     else:
#         length = len(ai.white_key_record)
#         for i in range(length):
#             key, (x, y) = ai.white_key_record[length - i - 1]
#             ai.weight_dictionary[key][x][y] -= penalty_factor * bias_function(i)
#         length = len(ai.black_key_record)
#         for i in range(length):
#             key, (x, y) = ai.black_key_record[length - i - 1]
#             ai.weight_dictionary[key][x][y] -= penalty_factor * bias_function(i)
#
#

def bias_function(step: int) -> float:
    eta = 0.63
    return 1 - 2 / math.pi * math.atan(math.pi / 2 * eta * step)
