import multiprocessing
import os
import pickle
import sys
import time

import ai.play
import ai.evaluate

moves: int
max_q: int
winner: int
black_wins: int
white_wins: int
has_random: bool
training_times: int
chess: [[]]

pool = multiprocessing.Pool(processes=4)

last_state = []
state_list = []
next_result_list = []
q_dictionary = {}
state_record = []

DATA_NAME = "training.data"
LOAD_TRAINING_FILE_PATH = "./data/"
TRAINING_DATA_PATH = "/mnt/lustre/kaitok/training/"
MAX_BYTES = 2 ** 31 - 1


def initialize():
    global moves, max_q, chess, winner, has_random, last_state, q_dictionary, next_result_list, state_record
    moves = 0
    winner = 0
    has_random = False
    max_q = -sys.maxsize - 1

    state_record = []
    next_result_list = []
    chess = [[-2 for _ in range(23)] for _ in range(23)]
    for i in range(4, 19):
        for j in range(4, 19):
            chess[i][j] = 0

    _, (state, _) = ai.evaluate.get_state_and_reward(((11, 11), chess, [], moves, False))
    last_state = state
    state_record.append(state)
    if not state_list:
        state_list.append(state)


def q_dictionary_processing(coordinate):
    global last_state
    _, (state, _) = ai.evaluate.get_state_and_reward((coordinate, chess, last_state, moves, False))
    if state not in state_list:
        state_list.append(state)
        q_dictionary[(state_list.index(last_state), state_list.index(state))] = 0
    last_state = state


def add_move(x: int, y: int):
    global moves
    moves += 1
    chess[x][y] = 2 if moves % 2 == 0 else 1


def remove_move(x: int, y: int):
    global moves
    moves -= 1
    chess[x][y] = 0


def has_winner(x: int, y: int):
    global winner
    player = 2 if moves % 2 == 0 else 1
    if ai.evaluate.has_winner(x, y, player):
        winner = player


def get_boundary(chess_copy: [[]]) -> []:
    boundary_list = []
    append = boundary_list.append
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
                    append((i, j))
    return boundary_list


def get_available_move() -> []:
    move_list = []
    append = move_list.append
    for i in range(4, 19):
        for j in range(4, 19):
            if chess[i][j] == 0:
                append((i, j))
    return move_list


def load_training_data(is_training: bool) -> bool:
    global state_list, q_dictionary, black_wins, white_wins, training_times

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
        (training_times, black_wins, white_wins), state_list, q_dictionary = pickle.loads(bytes_in)
        file_in.close()
        return True
    except IOError as error:
        print(error)
        state_list = []
        q_dictionary = {}
        black_wins = 0
        white_wins = 0
        training_times = 0
        return False


def save_training_data(file_path: str):
    bytes_out = pickle.dumps(((training_times, black_wins, white_wins), state_list, q_dictionary))
    try:
        with open(file_path, 'wb') as file_out:
            for i in range(0, len(bytes_out), MAX_BYTES):
                file_out.write(bytes_out[i: i + MAX_BYTES])
            file_out.close()
    except IOError as error:
        print("Failed to save the data.", error)


def save_log(string: str):
    with open("/users/kaitok/gomoku/log", 'a') as file:
        file.write(string + "\n")
    file.close()


def self_play_training(times: int):
    global black_wins, white_wins, training_times
    start_time = time.time()
    last_time = time.time()

    print("")
    load_training_data(True)
    append = state_record.append
    for i in range(times):
        initialize()
        while moves <= 225:
            x, y = ai.play.next_move(True)
            add_move(x, y)
            append(last_state)
            has_winner(x, y)
            if winner != 0:
                if winner == 1:
                    black_wins += 1
                elif winner == 2:
                    white_wins += 1
                break
        ai.play.update_q(winner)
        training_times += 1
        if training_times % 200 == 0:
            save_log("\nBlack wins " + str(black_wins) + " times. White wins " + str(white_wins) + " times.\n")
            save_training_data(TRAINING_DATA_PATH + DATA_NAME + "." + str(training_times))

        save_log(
            "No. " + str(training_times) + " Moves: " + str(moves) + " Costs " + str(time.time() - last_time) + " s")
        last_time = time.time()

    save_training_data(TRAINING_DATA_PATH + DATA_NAME)

    print("Cost", time.time() - start_time, "s")
    print("Black wins", black_wins, "times, White wins", white_wins, "times\n")
