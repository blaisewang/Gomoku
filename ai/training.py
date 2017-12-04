from sys import argv

import ai


def main():
    times = argv[1]
    if times.isdigit():
        ai.self_play_training(int(times))


main()
