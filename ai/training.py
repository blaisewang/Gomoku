from sys import argv

import ai

if __name__ == "__main__":
    times = argv[1]
    if times.isdigit():
        ai.self_play_training(int(times))
