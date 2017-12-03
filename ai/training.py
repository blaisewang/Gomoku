import ai


def main():
    times = input("Set training times: ")
    if times.isdigit():
        ai.self_play_training(int(times))


main()
