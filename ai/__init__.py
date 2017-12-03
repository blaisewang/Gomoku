import copy
import pickle
import shutil
import threading
from multiprocessing.pool import ThreadPool
import numpy as np

import os

import ai.play
import ai.evaluate

moves: int = 0
winner: int
chess: [[]]

last_state: []
state_list = []
reward_matrix: np.matrix
# black_key_record: [(str, (int, int))] = []
# white_key_record: [(str, (int, int))] = []

training_data_path = "training.data"
max_bytes = 2 ** 31 - 1

pool = ThreadPool(processes=1)


def initialize():
    global moves, chess, winner, last_state, reward_matrix
    moves = 0
    winner = 0
    # black_key_record = []
    # white_key_record = []
    chess = [[-2 for _ in range(23)] for _ in range(23)]
    for i in range(4, 19):
        for j in range(4, 19):
            chess[i][j] = 0

    if len(state_list) == 0:
        state, _ = evaluate.state_function_thread(chess, moves, (11, 11))
        last_state = state
        state_list.append(state)
        reward_matrix = np.matrix(np.array([[0]]))


def learning_thread(args):
    global last_state, reward_matrix
    async_result = pool.apply_async(evaluate.state_function_thread, (copy.deepcopy(chess), moves, args))
    state, reward = async_result.get()
    if state not in state_list:
        reward_matrix = np.row_stack((reward_matrix, np.zeros(len(state_list))))
        state_list.append(state)
        reward_matrix = np.column_stack((reward_matrix, np.zeros((len(state_list), 1))))
    reward_matrix[state_list.index(last_state), state_list.index(state)] = reward
    last_state = state
    if winner != 0:
        save_training_data()


def add_move(y: int, x: int):
    global moves
    moves += 1
    player = 2 if moves % 2 == 0 else 1
    chess[x][y] = player

    thread = threading.Thread(target=learning_thread, args=((x, y),))
    thread.setDaemon(True)
    thread.start()
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
    if evaluate.has_winner([player, player, player, player, player], x, y):
        winner = player


def get_boundary() -> [[]]:
    boundary = [[0.0 for _ in range(15)] for _ in range(15)]
    for i in range(4, 19):
        for j in range(4, 19):
            if chess[i][j] == 0:
                if (chess[i - 1][j - 1] == 1 or chess[i - 1][j - 1] == 2) or (
                        chess[i - 1][j] == 1 or chess[i - 1][j] == 2) or (
                        chess[i - 1][j + 1] == 1 or chess[i - 1][j + 1] == 2) or (
                        chess[i][j - 1] == 1 or chess[i][j - 1] == 2) or (
                        chess[i][j + 1] == 1 or chess[i][j + 1] == 2) or (
                        chess[i + 1][j - 1] == 1 or chess[i + 1][j - 1] == 2) or (
                        chess[i + 1][j] == 1 or chess[i + 1][j] == 2) or (
                        chess[i + 1][j + 1] == 1 or chess[i + 1][j + 1] == 2):
                    boundary[i - 4][j - 4] = 1.0
    return boundary


def load_training_data() -> bool:
    global state_list, reward_matrix
    try:
        bytes_in = bytearray(0)
        input_size = os.path.getsize(training_data_path)
        with open(training_data_path, 'rb') as file_in:
            for _ in range(0, input_size, max_bytes):
                bytes_in += file_in.read(max_bytes)
        training_tuple = pickle.loads(bytes_in)
        state_list, reward_matrix = training_tuple
        file_in.close()
        shutil.copyfile(training_data_path, training_data_path + ".backup")
        return True
    except IOError as error:
        print(error)
        state_list = []
        reward_matrix = [[]]
        return False


def save_training_data() -> bool:
    bytes_out = pickle.dumps((state_list, reward_matrix))
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
