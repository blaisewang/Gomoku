import ai
import ai.evaluate


def pattern_match_debug(y, x):
    player = 2 if ai.moves % 2 == 0 else 1
    opponent = 1 if player == 2 else 2

    if ai.evaluate.is_one_dimensional_pattern_match([player, player, player, player, player], x, y, 4):
        print("XXXXX")

    if ai.evaluate.is_one_dimensional_pattern_match([0, player, player, player, player, 0], x, y, 4):
        print("0XXXX0")

    if ai.evaluate.is_one_dimensional_cross_pattern_match([0, player, player, player, 0], x, y, 3):
        print("CROSS")

    if ai.evaluate.is_one_dimensional_pattern_match([0, player, player, player, 0], x, y, 4):
        print("0XXX0")

    if ai.evaluate.is_one_dimensional_pattern_match([0, player, player, 0], x, y, 2):
        print("0XX0")

    if ai.evaluate.is_one_dimensional_pattern_match([0, player, 0, player, 0], x, y, 3):
        print("0X0X0")

    if ai.evaluate.is_one_dimensional_pattern_match([opponent, player, player, player, player, 0], x, y, 4):
        print("OXXXX0")

    if ai.evaluate.is_one_dimensional_pattern_match([0, player, player, player, player, opponent], x, y, 4):
        print("0XXXXO")

    if ai.evaluate.is_one_dimensional_pattern_match([opponent, player, player, player, 0], x, y, 3):
        print("OXXX0")

    if ai.evaluate.is_one_dimensional_pattern_match([0, player, player, player, opponent], x, y, 3):
        print("0XXXO")

    if ai.evaluate.is_one_dimensional_pattern_match([opponent, player, player, 0], x, y, 2):
        print("OXX0")

    if ai.evaluate.is_one_dimensional_pattern_match([0, player, player, opponent], x, y, 2):
        print("0XXO")
