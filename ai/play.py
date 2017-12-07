import copy
import math
import multiprocessing
import numpy as np
import sys

import ai
import ai.evaluate

EPSILON = 0.0015
MAGNIFICATION_FACTOR = 10000
GAMMA = 0.8

chess: [[]]


def next_move(is_training: bool) -> (int, int):
    global chess
    next_move_result = []
    potential_q_result = []
    greedy_threshold = int(EPSILON * MAGNIFICATION_FACTOR)

    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())

    if ai.moves == 0:
        return 11, 11
    else:
        greedy = True
        chess = copy.deepcopy(ai.chess)
        next_move_list = ai.get_boundary(chess)

        if is_training:
            if np.random.randint(1, MAGNIFICATION_FACTOR) <= greedy_threshold:
                greedy = False

        if greedy:
            if not ai.next_result_list:
                result = []
                for x, y in next_move_list:
                    result.append(pool.apply_async(ai.evaluate.get_next_move_result, ((x, y), chess, ai.moves)))
                for res in result:
                    position, (state, reward) = res.get()
                    q_value = 0.0
                    if state in ai.state_list:
                        q_value = ai.q_matrix[ai.state_list.index(ai.last_state), ai.state_list.index(state)]
                    next_move_result.append((position, state, q_value, reward))
            else:
                next_move_result = copy.deepcopy(ai.next_result_list)
                ai.next_result_list.clear()

            max_q = -sys.maxsize - 1
            potential_next_move_greedy_result = []
            for _, _, q_value, _ in next_move_result:
                max_q = q_value if q_value > max_q else max_q
            for position, state, q_value, reward in next_move_result:
                if q_value == max_q:
                    potential_next_move_greedy_result.append((position, state, q_value, reward))
            (next_x, next_y), next_state, _, next_r = potential_next_move_greedy_result[
                np.random.randint(0, len(potential_next_move_greedy_result))]
        else:
            if np.random.randint(1, greedy_threshold) <= 0.8 * greedy_threshold:
                next_x, next_y = next_move_list[np.random.randint(0, len(next_move_list))]
            else:
                available_move = ai.get_available_move()
                next_x, next_y = available_move[np.random.randint(0, len(available_move))]
            next_state, next_r = ai.evaluate.StateAndReward(copy.deepcopy(chess), (next_x, next_y),
                                                            ai.moves).get_state_and_reward()

        if is_training:
            if next_state not in ai.state_list:
                ai.q_matrix = np.row_stack((ai.q_matrix, np.zeros(len(ai.state_list))))
                ai.state_list.append(next_state)
                ai.q_matrix = np.column_stack((ai.q_matrix, np.zeros((len(ai.state_list), 1))))

            chess[next_x][next_y] = 2 if (ai.moves + 1) % 2 == 0 else 1
            potential_move_list = ai.get_boundary(chess)

            result = []
            for x, y in potential_move_list:
                result.append(pool.apply_async(ai.evaluate.get_potential_q_result, ((x, y), chess, ai.moves)))
            pool.close()
            pool.join()
            for res in result:
                position, (state, reward) = res.get()
                q_value = 0.0
                if state in ai.state_list:
                    q_value = ai.q_matrix[ai.state_list.index(next_state), ai.state_list.index(state)]
                potential_q_result.append(q_value)
                ai.next_result_list.append((position, state, q_value, reward))

            ai.q_matrix[ai.state_list.index(ai.last_state), ai.state_list.index(next_state)] = next_r - GAMMA * max(
                potential_q_result)

        ai.last_state = next_state

        return next_x, next_y


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
    penalty = 100
    return penalty * (1 - 2 / math.pi * math.atan(math.pi / 2 * eta * step))
