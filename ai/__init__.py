import copy
import numpy as np
import os
import pickle
import shutil
from multiprocessing.pool import ThreadPool

import ai.play
import ai.evaluate

moves: int
winner: int
chess: [[]]

last_state = {}
state_list = []
q_matrix: np.matrix
# black_key_record: [(str, (int, int))] = []
# white_key_record: [(str, (int, int))] = []

training_data_path = "training.data"
max_bytes = 2 ** 31 - 1

pool = ThreadPool(processes=1)


def initialize():
    global moves, chess, winner, last_state, q_matrix
    moves = 0
    winner = 0
    # black_key_record = []
    # white_key_record = []
    chess = [[-2 for _ in range(23)] for _ in range(23)]
    for i in range(4, 19):
        for j in range(4, 19):
            chess[i][j] = 0

    if len(state_list) == 0:
        state, _ = evaluate.StateAndReward(chess, (11, 11), moves).get_state_and_reward()
        last_state = state
        state_list.append(state)
        q_matrix = np.matrix(np.array([[0]]))


def q_matrix_thread(args):
    global last_state, q_matrix
    state, _ = evaluate.StateAndReward(copy.deepcopy(chess), args, moves).get_state_and_reward()
    if state not in state_list:
        q_matrix = np.row_stack((q_matrix, np.zeros(len(state_list))))
        state_list.append(state)
        q_matrix = np.column_stack((q_matrix, np.zeros((len(state_list), 1))))
        q_matrix[state_list.index(last_state), state_list.index(state)] = 0
    last_state = state


def add_move(y: int, x: int):
    global moves
    moves += 1
    player = 2 if moves % 2 == 0 else 1
    chess[x][y] = player
    # if moves > 1:
    #     if moves % 2 == 0:
    #         black_key_record.append((key, (x - 4, y - 4)))
    #     else:
    #         white_key_record.append((key, (x - 4, y - 4)))


def remove_move(y: int, x: int):
    global moves
    moves -= 1
    chess[x][y] = 0


def has_winner(y: int, x: int):
    global winner
    player = 2 if moves % 2 == 0 else 1
    if evaluate.StateAndReward(ai.chess, (x, y)).has_winner([player, player, player, player, player]):
        winner = player


def get_boundary(chess_copy: [[]]) -> []:
    boundary = []
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
                    boundary.append((i, j))
    return boundary


def load_training_data() -> bool:
    global state_list, q_matrix
    try:
        bytes_in = bytearray(0)
        input_size = os.path.getsize(training_data_path)
        with open(training_data_path, 'rb') as file_in:
            for _ in range(0, input_size, max_bytes):
                bytes_in += file_in.read(max_bytes)
        training_tuple = pickle.loads(bytes_in)
        state_list, q_matrix = training_tuple
        file_in.close()
        shutil.copyfile(training_data_path, training_data_path + ".backup")
        return True
    except IOError as error:
        print(error)
        state_list = []
        q_matrix = [[]]
        return False


def save_training_data() -> bool:
    bytes_out = pickle.dumps((state_list, q_matrix))
    try:
        with open(training_data_path, 'wb') as file_out:
            for i in range(0, len(bytes_out), max_bytes):
                file_out.write(bytes_out[i: i + max_bytes])
            file_out.close()
            return True
    except IOError as e:
        print(e)
        return False

# def self_play_training(times: int):
#     load_weight_dictionary()
#     try:
#         times_file = open("times.data", "rb")
#         training_times = pickle.load(times_file)
#         times_file.close()
#     except IOError:
#         training_times = 0
#
#     time_start = time.time()
#
#     for _ in range(times):
#         initialize()
#         winner = 0
#         while moves <= 255:
#             x, y = play.next_move()
#             add_move(x, y)
#             if has_winner(x, y):
#                 winner = 2 if moves % 2 == 0 else 1
#         play.update_weight(winner)
#
#     time_end = time.time()
#     training_times += times
#
#     print("Has been trained", training_times, "times")
#     print("Cost", time_end - time_start, "s")
#
#     times_file = open("times.data", "wb")
#     pickle.dump(training_times, times_file)
#     times_file.close()
#     bytes_out = pickle.dumps(weight_dictionary)
#     with open(file_path, 'wb') as file_out:
#         for i in range(0, len(bytes_out), max_bytes):
#             file_out.write(bytes_out[i:i + max_bytes])
#         file_out.close()
