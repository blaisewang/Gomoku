import os.path
import pickle
import time

import ai.play

moves = 0
chess = [[0 for _ in range(23)] for _ in range(23)]
weight_dictionary = {}
black_key_record: [(str, (int, int))] = []
white_key_record: [(str, (int, int))] = []

file_path = "training.data"
max_bytes = 2 ** 31 - 1


def initialize():
    global moves, chess, black_key_record, white_key_record
    moves = 0
    black_key_record = []
    white_key_record = []
    chess = [[0 for _ in range(23)] for _ in range(23)]


def add_move(x: int, y: int):
    global moves
    moves += 1
    player = 2 if moves % 2 == 0 else 1
    chess[x][y] = player
    key = get_chess_key()
    if moves > 1:
        if moves % 2 == 0:
            black_key_record.append((key, (x - 4, y - 4)))
        else:
            white_key_record.append((key, (x - 4, y - 4)))
    if len(ai.weight_dictionary) == 0:
        initial_weight_dictionary()
        weight_dictionary[key] = get_initial_weight()
    weight_dictionary[key] = get_initial_weight()


def remove_move(x: int, y: int):
    global moves
    moves -= 1
    chess[x][y] = 0


def is_win(x, y) -> bool:
    win = "11111" if moves % 2 == 1 else "22222"
    return win in "".join(map(str, [chess[i][y] for i in range(x - 4, x + 5)])) or win in "".join(
        map(str, [chess[x][i] for i in range(y - 4, y + 5)])) or win in "".join(
        map(str, [chess[x + i][y + i] for i in range(-4, 5)])) or win in "".join(
        map(str, [chess[x - i][y + i] for i in range(-4, 5)]))


def initial_weight_dictionary():
    weight = [[0.0 for _ in range(15)] for _ in range(15)]
    weight[7][7] = 1.0
    weight_dictionary["".join("0" for _ in range(225))] = weight


def get_chess_key():
    return "".join(map(str, [chess[i][j] for i in range(4, 19) for j in range(4, 19)]))


def get_initial_weight() -> [[]]:
    weight = [[0.0 for _ in range(15)] for _ in range(15)]
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
                    weight[i - 4][j - 4] = 1.0
    return weight


def load_weight_dictionary():
    global weight_dictionary
    try:
        bytes_in = bytearray(0)
        input_size = os.path.getsize(file_path)
        with open(file_path, 'rb') as file_in:
            for _ in range(0, input_size, max_bytes):
                bytes_in += file_in.read(max_bytes)
        weight_dictionary = pickle.loads(bytes_in)
    except IOError:
        weight_dictionary = dict()


def self_training(times: int):
    load_weight_dictionary()
    try:
        times_file = open("times.data", "rb")
        training_times = pickle.load(times_file)
        times_file.close()
    except IOError:
        training_times = 0

    time_start = time.time()

    for _ in range(times):
        initialize()
        winner = 0
        while moves <= 255:
            x, y = play.next_move()
            add_move(x, y)
            if is_win(x, y):
                winner = 2 if moves % 2 == 0 else 1
        play.update_weight(winner)

    time_end = time.time()
    training_times += times

    print("Has been trained", training_times, "times")
    print("Cost", time_end - time_start, "s")

    times_file = open("times.data", "wb")
    pickle.dump(training_times, times_file)
    times_file.close()
    bytes_out = pickle.dumps(weight_dictionary)
    with open(file_path, 'wb') as file_out:
        for i in range(0, len(bytes_out), max_bytes):
            file_out.write(bytes_out[i:i + max_bytes])
