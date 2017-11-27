import ai
import ai.evaluate


def pattern_match_debug(y, x):
    player = 2 if ai.moves % 2 == 0 else 1
    opponent = 1 if player == 2 else 2

    one_dimensional_winning_pattern_list = [
        ([player, player, player, player, player], 4),
        ([player, opponent, opponent, opponent, opponent, player], 5),
        ([0, player, player, player, player, 0], 4),
    ]

    one_dimensional_important_pattern_list = [
        ([0, opponent, opponent, opponent, player], 4, 1),
        ([player, opponent, opponent, opponent, 0], 0, 5)
    ]

    two_dimensional_winning_pattern_list = [
        ([[-1, -1, 0, -1, -1],
          [-1, -1, player, -1, -1],
          [0, player, player, player, 0],
          [-1, -1, player, -1, -1],
          [-1, -1, 0, -1, -1]], 2, 2),

        ([[-1, -1, -1, 0, -1],
          [-1, -1, -1, player, -1],
          [-1, -1, -1, player, -1],
          [0, player, player, player, 0],
          [-1, -1, -1, 0, -1]], 3, 3),

        ([[-1, 0, -1, -1, -1],
          [-1, player, - 1, -1, -1],
          [-1, player, - 1, -1, -1],
          [0, player, player, player, 0],
          [-1, 0, -1, -1, -1]], 3, 1),

        ([[-1, -1, -1, 0, -1],
          [0, player, player, player, 0],
          [-1, -1, -1, player, -1],
          [-1, -1, -1, player, -1],
          [-1, -1, -1, 0, -1]], 1, 3),

        ([[-1, 0, -1, -1, -1],
          [0, player, player, player, 0],
          [-1, player, - 1, -1, -1],
          [-1, player, - 1, -1, -1],
          [-1, 0, -1, -1, -1]], 1, 1)
    ]

    two_dimensional_important_pattern_list = [
        ([[-1, -1, 0, -1, -1],
          [-1, -1, opponent, -1, -1],
          [0, opponent, player, opponent, 0],
          [-1, -1, opponent, -1, -1],
          [-1, -1, 0, -1, -1]], 2, 2),

        ([[-1, -1, -1, 0, -1],
          [-1, -1, -1, opponent, -1],
          [-1, -1, -1, opponent, -1],
          [0, opponent, opponent, player, 0],
          [-1, -1, -1, 0, -1]], 3, 3),

        ([[-1, 0, -1, -1, -1],
          [-1, opponent, - 1, -1, -1],
          [-1, opponent, - 1, -1, -1],
          [0, player, opponent, opponent, 0],
          [-1, 0, -1, -1, -1]], 3, 1),

        ([[-1, -1, -1, 0, -1],
          [0, opponent, opponent, player, 0],
          [-1, -1, -1, opponent, -1],
          [-1, -1, -1, opponent, -1],
          [-1, -1, -1, 0, -1]], 1, 3),

        ([[-1, 0, -1, -1, -1],
          [0, player, opponent, opponent, 0],
          [-1, opponent, - 1, -1, -1],
          [-1, opponent, - 1, -1, -1],
          [-1, 0, -1, -1, -1]], 1, 1)
    ]

    one_dimensional_pattern_list = [
        ([0, player, player, player, 0], 50, 3),
        ([0, player, player, 0], 40, 2),
        ([0, player, 0, player, 0], 30, 3),
        ([opponent, player, player, player, player, 0], 20, 4),
        ([0, player, player, player, player, opponent], 20, 4),
        ([opponent, player, player, player, 0], 10, 3),
        ([0, player, player, player, opponent], 10, 3),
        ([opponent, player, player, 0], 1, 2),
        ([0, player, player, opponent], 1, 2)
    ]

    for pattern, left_offset in one_dimensional_winning_pattern_list:
        if ai.evaluate.is_one_dimensional_pattern_match(pattern, x, y, left_offset):
            print(pattern, ai.evaluate.is_one_dimensional_pattern_match(pattern, x, y, left_offset))

    for pattern, left_offset, right_offset in one_dimensional_important_pattern_list:
        if ai.evaluate.is_one_dimensional_pattern_match(pattern, x, y, left_offset, right_offset):
            print(pattern, ai.evaluate.is_one_dimensional_pattern_match(pattern, x, y, left_offset, right_offset))

    for pattern, anchor_x, anchor_y in two_dimensional_winning_pattern_list:
        if ai.evaluate.is_two_dimensional_pattern_match(pattern, x, y, anchor_x, anchor_y) > 0:
            print(pattern, ai.evaluate.is_two_dimensional_pattern_match(pattern, x, y, anchor_x, anchor_y))

    for pattern, anchor_x, anchor_y in two_dimensional_important_pattern_list:
        if ai.evaluate.is_two_dimensional_pattern_match(pattern, x, y, anchor_x, anchor_y):
            print(pattern, ai.evaluate.is_two_dimensional_pattern_match(pattern, x, y, anchor_x, anchor_y))

    for pattern, expect_reward, left_offset in one_dimensional_pattern_list:
        if ai.evaluate.is_one_dimensional_pattern_match(pattern, x, y, left_offset):
            print(pattern, ai.evaluate.is_one_dimensional_pattern_match(pattern, x, y, left_offset))
