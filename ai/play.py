import copy
import math
import numpy as np
import random
import threading

import ai

epsilon = 0.015
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
    global chess, next_state, next_move_result, potential_q_result
    next_move_result = []
    potential_q_result = []
    next_state = {}
    greedy_threshold = epsilon * 1000

    if ai.moves == 0:
        return 11, 11
    else:
        greedy = True
        chess = copy.deepcopy(ai.chess)
        next_move_list = ai.get_boundary(chess)

        if is_training:
            if random.randint(1, 1000) <= greedy_threshold:
                greedy = False

        if greedy:
            threads = []
            for x, y in next_move_list:
                thread = threading.Thread(target=get_next_move_result, args=((x, y),))
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()

            max_q = 0.0
            potential_next_move_greedy_result = []
            for _, _, q_value, _ in next_move_result:
                max_q = q_value if q_value > max_q else max_q
            for (x, y), state, q_value, reward in next_move_result:
                if q_value == max_q:
                    potential_next_move_greedy_result.append(((x, y), state, q_value, reward))
            (next_x, next_y), next_state, _, next_r = potential_next_move_greedy_result[
                random.randint(0, len(potential_next_move_greedy_result) - 1)]

        else:
            if random.randint(1, greedy_threshold) <= 0.8 * greedy_threshold:
                next_x, next_y = next_move_list[random.randint(0, len(next_move_list) - 1)]
            else:
                available_move = ai.get_available_move()
                next_x, next_y = available_move[random.randint(0, len(available_move) - 1)]
            next_state, next_r = ai.evaluate.StateAndReward(copy.deepcopy(chess), (next_x, next_y),
                                                            ai.moves).get_state_and_reward()
        if is_training:
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

        return next_state, (next_x, next_y)


def update_q(winner: int):
    draw_penalty = 0.1

    if winner == 1:
        length = len(ai.white_key_record) - 1
        for i in range(length):
            last_state = ai.white_key_record[length - i - 1]
            state = ai.white_key_record[length - i]
            ai.q_matrix[ai.state_list.index(last_state), ai.state_list.index(state)] -= bias_function(i)
    elif winner == 2:
        length = len(ai.black_key_record) - 1
        for i in range(length):
            last_state = ai.black_key_record[length - i - 1]
            state = ai.black_key_record[length - i]
            ai.q_matrix[ai.state_list.index(last_state), ai.state_list.index(state)] -= bias_function(i)
    else:
        length = len(ai.white_key_record) - 1
        for i in range(length):
            last_state = ai.white_key_record[length - i - 1]
            state = ai.white_key_record[length - i]
            ai.q_matrix[ai.state_list.index(last_state), ai.state_list.index(state)] -= draw_penalty * bias_function(i)
        length = len(ai.black_key_record) - 1
        for i in range(length):
            last_state = ai.black_key_record[length - i - 1]
            state = ai.black_key_record[length - i]
            ai.q_matrix[ai.state_list.index(last_state), ai.state_list.index(state)] -= draw_penalty * bias_function(i)


def bias_function(step: int) -> float:
    eta = 0.8
    return 1 - 2 / math.pi * math.atan(math.pi / 2 * eta * step)
