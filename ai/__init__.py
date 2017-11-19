import pickle

import ai.play

moves = 0
chess: [[]]
chess_record: []
weight_dictionary = {}
black_key_record: [(str, (int, int))]
white_key_record: [(str, (int, int))]
null_weight = [[0.0 for _ in range(15)] for _ in range(15)]


def add_move(x: int, y: int):
    global moves
    moves += 1
    player = 2 if moves % 2 == 0 else 1
    chess_record.append((x, y, player))
    chess[x][y] = player
    key = get_chess_key()
    if key not in weight_dictionary:
        weight_dictionary[key] = get_initial_weight()


def is_win(x, y) -> bool:
    win = "11111" if moves % 2 == 1 else "22222"
    return win in "".join(map(str, [chess[i][y] for i in range(x - 4, x + 5)])) or win in "".join(
        map(str, [chess[x][i] for i in range(y - 4, y + 5)])) or win in "".join(
        map(str, [chess[x + i][y + i] for i in range(-4, 5)])) or win in "".join(
        map(str, [chess[x - i][y + i] for i in range(-4, 5)]))


def get_chess_key():
    return "".join(map(str, [chess[i][j] for i in range(4, 19) for j in range(4, 19)]))


def get_initial_weight() -> [[]]:
    weight = null_weight.copy()
    for i in range(4, 19):
        for j in range(4, 19):
            if chess[i][j] == 0:
                if (chess[i - 1][j - 1] == 1 or chess[i - 1][j - 1] == 2) or (
                                chess[i - 1][j] == 1 or chess[i - 1][j] == 2) or (
                                chess[i - 1][j + 1] == 1 or chess[i - 1][j + 1] == 2) or (
                                chess[i][j - 1] == 1 or chess[i][j - 1] == 2) or (
                                chess[i][j] == 1 or chess[i][j] == 2) or (
                                chess[i][j + 1] == 1 or chess[i][j + 1] == 2) or (
                                chess[i + 1][j - 1] == 1 or chess[i + 1][j - 1] == 2) or (
                                chess[i + 1][j] == 1 or chess[i + 1][j] == 2) or (
                                chess[i + 1][j + 1] == 1 or chess[i + 1][j + 1] == 2):
                    weight[i - 4][j - 4] = 1.0
    return weight


def self_training(times: int):
    global moves, chess, chess_record, black_key_record, white_key_record, weight_dictionary

    try:
        training_file = open("training.data", "rb")
        weight_dictionary = pickle.load(training_file)
        training_file.close()
    except IOError:
        weight_dictionary = dict()

    try:
        times_file = open("times.data", "rb")
        training_times = pickle.load(times_file)
        times_file.close()
    except IOError:
        training_times = 0

    for _ in range(times):
        moves = 0
        winner = 0
        chess_record = []
        black_key_record = []
        white_key_record = []
        chess = [[0 for _ in range(23)] for _ in range(23)]
        black_key_record = []
        while moves <= 255:
            x, y = play.next_move()
            add_move(x, y)
            if is_win(x, y):
                winner = 2 if moves % 2 == 0 else 1
        play.update_weight(winner)

    training_times += times
    print("Has been trained", training_times, "times")

    times_file = open("times.data", "wb")
    pickle.dump(training_times, times_file)
    times_file.close()
    training_file = open("training.data", "wb")
    pickle.dump(weight_dictionary, training_file)
    training_file.close()
