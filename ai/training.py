import sys

import ai

if __name__ == "__main__":
    times = sys.argv[1]
    if times.isdigit():
        ai.self_play_training(int(times))
