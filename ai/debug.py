import numpy

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

    one_dimensional_dangerous_pattern_list = [
        ([0, opponent, opponent, opponent, player], True, 4, 1),
        ([opponent, opponent, opponent, opponent, player], True, 4, 1)
    ]

    two_dimensional_winning_pattern_list = [
        ([[-1, -1, 0, -1, -1],
          [-1, -1, player, -1, -1],
          [0, player, player, player, 0],
          [-1, -1, player, -1, -1],
          [-1, -1, 0, -1, -1]], False, (2, 2)),

        ([[-1, 0, -1, -1, -1],
          [0, player, player, player, 0],
          [-1, player, - 1, -1, -1],
          [-1, player, - 1, -1, -1],
          [-1, 0, -1, -1, -1]], True, (1, 1))
    ]

    two_dimensional_dangerous_pattern_list = [
        ([[-1, -1, 0, -1, -1],
          [-1, -1, opponent, -1, -1],
          [0, opponent, player, opponent, 0],
          [-1, -1, opponent, -1, -1],
          [-1, -1, 0, -1, -1]], False, (2, 2)),

        ([[-1, 0, -1, -1, -1],
          [0, player, opponent, opponent, 0],
          [-1, opponent, - 1, -1, -1],
          [-1, opponent, - 1, -1, -1],
          [-1, 0, -1, -1, -1]], True, (1, 1))
    ]

    one_dimensional_pattern_list = [
        ([0, player, player, player, 0], False, 3, 50),
        ([0, player, player, 0], False, 2, 40),
        ([0, player, 0, player, 0], False, 3, 30),
        ([opponent, player, player, player, player, 0], True, 4, 20),
        ([opponent, player, player, player, 0], True, 3, 10),
        ([opponent, player, player, 0], True, 2, 5),
        ([opponent, player, 0], True, 1, 1)
    ]

    for pattern, left_offset in one_dimensional_winning_pattern_list:
        if ai.evaluate.one_dimensional_pattern_match(pattern, False, x, y, left_offset):
            print(pattern, ai.evaluate.one_dimensional_pattern_match(pattern, False, x, y, left_offset))

    for pattern, need_reverse, left_offset, right_offset in one_dimensional_dangerous_pattern_list:
        if ai.evaluate.one_dimensional_pattern_match(pattern, need_reverse, x, y, left_offset, right_offset):
            print(pattern,
                  ai.evaluate.one_dimensional_pattern_match(pattern, need_reverse, x, y, left_offset, right_offset))

    for pattern, need_rotate, (anchor_x, anchor_y) in two_dimensional_winning_pattern_list:
        if ai.evaluate.two_dimensional_pattern_match(pattern, need_rotate, x, y, anchor_x, anchor_y):
            print(numpy.array(pattern), ai.evaluate.two_dimensional_pattern_match(pattern, need_rotate, x, y, anchor_x, anchor_y))

    for pattern, need_rotate, (anchor_x, anchor_y) in two_dimensional_dangerous_pattern_list:
        if ai.evaluate.two_dimensional_pattern_match(pattern, need_rotate, x, y, anchor_x, anchor_y):
            print(numpy.array(pattern), ai.evaluate.two_dimensional_pattern_match(pattern, need_rotate, x, y, anchor_x, anchor_y))

    for pattern, need_reverse, left_offset, _ in one_dimensional_pattern_list:
        if ai.evaluate.one_dimensional_pattern_match(pattern, need_reverse, x, y, left_offset):
            print(pattern, ai.evaluate.one_dimensional_pattern_match(pattern, need_reverse, x, y, left_offset))
