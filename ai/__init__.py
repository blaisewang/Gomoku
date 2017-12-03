import copy
import numpy as np
import os
import pickle
import shutil
from multiprocessing.pool import ThreadPool

import time

import ai.play
import ai.evaluate

moves: int
winner: int
training_times: int
chess: [[]]

last_state = {}
state_list = []
q_matrix: np.matrix
black_key_record: [([], (int, int))] = []
white_key_record: [([], (int, int))] = []

training_data_path = "training.data"
max_bytes = 2 ** 31 - 1

pool = ThreadPool(processes=1)


def initialize():
    global moves, chess, winner, last_state, q_matrix, black_key_record, white_key_record
    moves = 0
    winner = 0
    black_key_record = []
    white_key_record = []
    chess = [[-2 for _ in range(23)] for _ in range(23)]
    for i in range(4, 19):
        for j in range(4, 19):
            chess[i][j] = 0

    if len(state_list) == 0:
        state, _ = evaluate.StateAndReward(chess, (11, 11)).get_state_and_reward()
        last_state = state
        state_list.append(state)
        q_matrix = np.matrix(np.array([[0]]))


def q_matrix_thread(args):
    global last_state, q_matrix
    state, reward = evaluate.StateAndReward(copy.deepcopy(chess), args, moves).get_state_and_reward()
    if state not in state_list:
        q_matrix = np.row_stack((q_matrix, np.zeros(len(state_list))))
        state_list.append(state)
        q_matrix = np.column_stack((q_matrix, np.zeros((len(state_list), 1))))
        q_matrix[state_list.index(last_state), state_list.index(state)] = 0
    last_state = state


def add_move(x: int, y: int):
    global moves
    moves += 1
    player = 2 if moves % 2 == 0 else 1
    chess[x][y] = player


def remove_move(x: int, y: int):
    global moves
    moves -= 1
    chess[x][y] = 0


def has_winner(x: int, y: int):
    global winner
    player = 2 if moves % 2 == 0 else 1
    if evaluate.StateAndReward(ai.chess, (x, y)).has_winner([player, player, player, player, player]):
        winner = player


def get_boundary(chess_copy: [[]]) -> []:
    boundary_list = []
    for i in range(4, 19):
        for j in range(4, 19):
            if chess_copy[i][j] == 0:
                if (chess_copy[i - 1][j - 1] == 1 or chess_copy[i - 1][j - 1] == 2) or (
                        chess_copy[i - 1][j] == 1 or chess_copy[i - 1][j] == 2) or (
                        chess_copy[i - 1][j + 1] == 1 or chess_copy[i - 1][j + 1] == 2) or (
                        chess_copy[i][j - 1] == 1 or chess_copy[i][j - 1] == 2) or (
                        chess_copy[i][j + 1] == 1 or chess_copy[i][j + 1] == 2) or (
                        chess_copy[i + 1][j - 1] == 1 or chess_copy[i + 1][j - 1] == 2) or (
                        chess_copy[i + 1][j] == 1 or chess_copy[i + 1][j] == 2) or (
                        chess_copy[i + 1][j + 1] == 1 or chess_copy[i + 1][j + 1] == 2):
                    boundary_list.append((i, j))
    return boundary_list


def get_available_move() -> []:
    move_list = []
    for i in range(4, 19):
        for j in range(4, 19):
            if chess[i][j] == 0:
                move_list.append((i, j))
    return move_list


def load_training_data() -> bool:
    global state_list, q_matrix, training_times
    try:
        bytes_in = bytearray(0)
        input_size = os.path.getsize(training_data_path)
        with open(training_data_path, 'rb') as file_in:
            for _ in range(0, input_size, max_bytes):
                bytes_in += file_in.read(max_bytes)
        training_tuple = pickle.loads(bytes_in)
        training_times, state_list, q_matrix = training_tuple
        file_in.close()
        shutil.copyfile(training_data_path, training_data_path + ".backup")
        return True
    except IOError as error:
        print(error)
        state_list = []
        q_matrix = [[]]
        training_times = 0
        return False


def save_training_data() -> bool:
    bytes_out = pickle.dumps((training_times, state_list, q_matrix))
    try:
        with open(training_data_path, 'wb') as file_out:
            for i in range(0, len(bytes_out), max_bytes):
                file_out.write(bytes_out[i: i + max_bytes])
            file_out.close()
            return True
    except IOError as error:
        print(error)
        return False


def self_play_training(times: int):
    global training_times
    time_start = time.time()
    load_training_data()

    for _ in range(times):
        initialize()
        while moves <= 255:
            x, y = play.next_move(True)
            add_move(x, y)
            if moves % 2 == 0:
                white_key_record.append(last_state)
            else:
                black_key_record.append(last_state)
            has_winner(x, y)
            if winner != 0:
                break
        play.update_q(winner)
        print(moves)
        print(len(state_list))
        print("")

        if save_training_data():
            training_times += times
            print("Has been trained", training_times, "times")
        else:
            print("Save training data failed")

        print("Cost", time.time() - time_start, "s")
