import copy
import os
import pickle
import sys
import time
import numpy as np
import pp

import ai.play
import ai.evaluate

moves: int
max_q: int
winner: int
black_wins: int
white_wins: int
training_times: int
chess: [[]]

last_state: []
state_list: []
next_result_list = []
q_matrix: np.matrix
state_record = []

DATA_NAME = "training.data"
LOAD_TRAINING_FILE_PATH = "./output/"
TRAINING_DATA_PATH = "/users/kaitok/gomoku/data/"
MAX_BYTES = 2 ** 31 - 1

pp_servers = None
job_server = None


def initialize():
    global moves, max_q, chess, winner, last_state, q_matrix, next_result_list, state_record
    moves = 0
    max_q = -sys.maxsize - 1
    winner = 0
    state_record = []
    next_result_list = []
    chess = [[-2 for _ in range(23)] for _ in range(23)]
    for i in range(4, 19):
        for j in range(4, 19):
            chess[i][j] = 0

    _, (state, _) = evaluate.get_state_and_reward(chess, (11, 11))
    last_state = state
    if not state_list:
        state_list.append(state)
        q_matrix = np.matrix(np.array([[0]]))


def q_matrix_processing(args):
    global last_state, q_matrix
    _, (state, _) = evaluate.get_state_and_reward(copy.deepcopy(chess), args, moves)
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
    if evaluate.has_winner(x, y, [player, player, player, player, player], copy.deepcopy(chess)):
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


def load_training_data(is_training: bool) -> bool:
    global state_list, q_matrix, black_wins, white_wins, training_times

    if is_training:
        file_path = TRAINING_DATA_PATH
    else:
        file_path = LOAD_TRAINING_FILE_PATH
    file_path += DATA_NAME

    try:
        bytes_in = bytearray(0)
        input_size = os.path.getsize(file_path)
        with open(file_path, 'rb') as file_in:
            for _ in range(0, input_size, MAX_BYTES):
                bytes_in += file_in.read(MAX_BYTES)
        (training_times, black_wins, white_wins), state_list, q_matrix = pickle.loads(bytes_in)
        file_in.close()
        return True
    except IOError as error:
        print(error)
        state_list = []
        q_matrix = [[]]
        black_wins = 0
        white_wins = 0
        training_times = 0
        return False


def save_training_data(file_path: str) -> bool:
    bytes_out = pickle.dumps(((training_times, black_wins, white_wins), state_list, q_matrix))
    try:
        with open(file_path, 'wb') as file_out:
            for i in range(0, len(bytes_out), MAX_BYTES):
                file_out.write(bytes_out[i: i + MAX_BYTES])
            file_out.close()
            return True
    except IOError as error:
        print(error)
        return False


def self_play_training(times: int):
    global pp_servers, job_server, black_wins, white_wins, training_times
    time_start = time.time()
    load_training_data(True)

    # pp_servers = (
    #     "node182.prv.sciama.cluster:37180", "node171.prv.sciama.cluster:37180", "node170.prv.sciama.cluster:37180",
    #     "node169.prv.sciama.cluster:37180", "node164.prv.sciama.cluster:37180")
    # job_server = pp.Server(ppservers=pp_servers, secret="Overdesirousness57-helicoid67")

    pp_servers = ()
    job_server = pp.Server(ppservers=pp_servers)

    black = 0
    white = 0

    for i in range(times):
        print(i + training_times + 1)
        initialize()
        while moves <= 255:
            x, y = play.next_move(True)
            add_move(x, y)
            state_record.append(last_state)
            has_winner(x, y)
            if winner != 0:
                if winner == 1:
                    black += 1
                elif winner == 2:
                    white += 1
                break
        play.update_q(winner)
        if (i + 1) % 50 == 0:
            save_training_data(TRAINING_DATA_PATH + str(training_times + i + 1) + DATA_NAME)

    black_wins += black
    white_wins += white
    training_times += times

    job_server.print_stats()

    if save_training_data(TRAINING_DATA_PATH + DATA_NAME):
        print("Has been trained", training_times, "times")
    else:
        print("Save training data failed")

    print("Cost", time.time() - time_start, "s")
    print("Black wins", black_wins, "times, White wins", white_wins, "times")
