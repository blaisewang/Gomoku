import copy
import math
import sys

import numpy as np
import scoop.futures

import ai
import ai.evaluate

EPSILON = 0.0015
MAGNIFICATION_FACTOR = 10000
GAMMA = 0.8


def next_move(is_training: bool) -> (int, int):
    moves = ai.moves
    chess = copy.deepcopy(ai.chess)
    greedy_threshold = int(EPSILON * MAGNIFICATION_FACTOR)

    if moves == 0:
        _, (state, reward) = ai.evaluate.get_state_and_reward(((11, 11), copy.deepcopy(chess), 0, True))
        if state not in ai.state_list:
            ai.state_list.append(state)
            ai.q_dictionary[str((ai.state_list.index(ai.last_state), ai.state_list.index(state)))] = reward
        ai.last_state = state
        return 11, 11
    else:
        greedy = True
        next_move_result = []
        next_move_list = ai.get_boundary(chess)

        if is_training and moves > 2 and not ai.has_random:
            if np.random.randint(1, MAGNIFICATION_FACTOR) <= greedy_threshold:
                ai.has_random = True
                greedy = False

        if greedy:
            if not ai.next_result_list:
                # results = ai.pool.map(ai.evaluate.get_state_and_reward,
                #                       [(position, copy.deepcopy(chess), moves, True) for position in
                #                        next_move_list])
                results = list(scoop.futures.map(ai.evaluate.get_state_and_reward,
                                                 [(position, copy.deepcopy(chess), ai.moves, True) for position in
                                                  next_move_list]))
                for result in results:
                    position, (state, reward) = result
                    q_value = 0.0
                    if state in ai.state_list:
                        if str((ai.state_list.index(ai.last_state), ai.state_list.index(state))) in ai.q_dictionary:
                            q_value = ai.q_dictionary[
                                str((ai.state_list.index(ai.last_state), ai.state_list.index(state)))]
                    if q_value > ai.max_q:
                        ai.max_q = q_value
                    next_move_result.append((position, state, q_value, reward))
            else:
                next_move_result = copy.deepcopy(ai.next_result_list)
                ai.next_result_list.clear()

            potential_next_move_greedy_result = []
            for position, state, q_value, reward in next_move_result:
                if q_value == ai.max_q:
                    potential_next_move_greedy_result.append((position, state, q_value, reward))
            (next_x, next_y), next_state, _, next_r = potential_next_move_greedy_result[
                np.random.randint(0, len(potential_next_move_greedy_result))]
            ai.max_q = -sys.maxsize - 1
        else:
            if np.random.randint(1, greedy_threshold) <= 0.8 * greedy_threshold:
                next_x, next_y = next_move_list[np.random.randint(0, len(next_move_list))]
            else:
                available_move = ai.get_available_move()
                next_x, next_y = available_move[np.random.randint(0, len(available_move))]
            _, (next_state, next_r) = ai.evaluate.get_state_and_reward(
                ((next_x, next_y), copy.deepcopy(chess), moves, True))

        moves += 1
        chess[next_x][next_y] = 2 if moves % 2 == 0 else 1

        if is_training:
            if next_state not in ai.state_list:
                ai.state_list.append(next_state)

            potential_move_list = ai.get_boundary(chess)
            # results = ai.pool.map(ai.evaluate.get_state_and_reward,
            #                       [(position, copy.deepcopy(chess), moves, True) for position in
            #                        potential_move_list])
            results = list(scoop.futures.map(ai.evaluate.get_state_and_reward,
                                             [(position, copy.deepcopy(chess), ai.moves, True) for position in
                                              potential_move_list]))
            for result in results:
                position, (state, reward) = result
                q_value = 0.0
                if state in ai.state_list:
                    if str((ai.state_list.index(next_state), ai.state_list.index(state))) in ai.q_dictionary:
                        q_value = ai.q_dictionary[str((ai.state_list.index(next_state), ai.state_list.index(state)))]
                if q_value > ai.max_q:
                    ai.max_q = q_value
                ai.next_result_list.append((position, state, q_value, reward))
            ai.q_dictionary[
                str((ai.state_list.index(ai.last_state), ai.state_list.index(next_state)))] = next_r - GAMMA * ai.max_q

        ai.last_state = next_state

        return next_x, next_y


def update_q(winner: int):
    draw_penalty = 0.1

    if winner == 1:
        length = len(ai.state_record) - 1
        for i in range(1, length - 2, 2):
            ai.q_dictionary[str((ai.state_list.index(ai.state_record[length - i - 1]),
                                 ai.state_list.index(ai.state_record[length - i])))] -= bias_function(int((i - 1) / 2))
    elif winner == 2:
        length = len(ai.state_record) - 1
        for i in range(1, length - 1, 2):
            ai.q_dictionary[str((ai.state_list.index(ai.state_record[length - i - 1]),
                                 ai.state_list.index(ai.state_record[length - i])))] -= bias_function(int((i - 1) / 2))
    else:
        length = len(ai.state_record) - 1
        for i in range(length - 2):
            ai.q_dictionary[str((ai.state_list.index(ai.state_record[length - i - 1]), ai.state_list.index(
                ai.state_record[length - i])))] -= draw_penalty * bias_function(i)


def bias_function(step: int) -> float:
    eta = 0.8
    penalty = 100
    return penalty * (1 - 2 / math.pi * math.atan(math.pi / 2 * eta * step))
