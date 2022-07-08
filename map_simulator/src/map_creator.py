from random import randint

import sys

sys.path.append('../..')

EMPTY_SPACE = 0
WALL = 1


def create_map(num_cols, num_rows):
    num_cols = num_cols
    num_rows = num_rows

    map = []
    for _ in range(num_rows):
        curr_row = []
        for _ in range(num_cols):
            curr_row.append(WALL)
        map.append(curr_row)

    curr_row = 0
    curr_col = 0

    while (curr_row < num_rows) and (curr_col < num_cols):
        if (curr_row >= 0) and (curr_col >= 0):
            map[curr_row][curr_col] = EMPTY_SPACE

        direction = randint(0, 3)
        if direction == 0:
            curr_col += 1
        elif direction == 1:
            curr_row -= 1
        elif direction == 2:
            curr_col -= 1
        else:
            curr_row += 1

        if curr_row < 0:
            curr_row = 0

        if curr_col < 0:
            curr_col = 0

    return map
