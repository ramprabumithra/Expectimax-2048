import random
size = 4

def new_board():
    return [[0] * size for _ in range(size)]

def empty(board):
    tiles = []
    for row in range(size):
        for col in range(size):
            if board[row][col] == 0:
                tiles.append((row, col))
    return tiles

def rand_tile_val(board):
    empties = empty(board)
    if not empties:
        return board
    row, col = random.choice(empties)
    # New tiles are 4 with 10% probability and 2 with 90% probability.
    value = 4 if random.random() < 0.10 else 2
    board[row][col] = value
    return board

# Checking if there are any legal moves left. If not, game over.
def can_move(board):
    if empty(board):
        return True
    for row in range(size):
        for col in range(size):
            v = board[row][col]
            if row + 1 < size and board[row + 1][col] == v:
                return True
            if col + 1 < size and board[row][col + 1] == v:
                return True
    return False

# This function makes the tiles move in the required direction and merge together if they are the same value.
def move_and_merge(line):
    nums = [x for x in line if x != 0]
    gained = 0
    merged = []
    i = 0
    while i < len(nums):
        if i + 1 < len(nums) and nums[i] == nums[i + 1]:
            val = nums[i] * 2
            merged.append(val)
            gained += val
            i += 2
        else:
            merged.append(nums[i])
            i += 1
    merged += [0] * (size - len(merged))
    changed = merged != line
    return merged, gained, changed

# Defining move functions for all 4 cardinal directions.
def move_left(board):
    changed_any = False
    gained_total = 0
    new_board = []
    for r in range(size):
        merged, gained, changed = move_and_merge(board[r])
        new_board.append(merged)
        gained_total += gained
        changed_any = changed_any or changed
    return new_board, gained_total, changed_any

def move_right(board):
    changed_any = False
    gained_total = 0
    new_board = []
    for r in range(size):
        # Reversing row to reuse the move_and_merge function for right moves.
        row = list(reversed(board[r]))
        merged, gained, changed = move_and_merge(row)
        merged = list(reversed(merged))
        new_board.append(merged)
        gained_total += gained
        changed_any = changed_any or changed
    return new_board, gained_total, changed_any

def move_up(board):
    changed_any = False
    gained_total = 0
    new_board = [[0] * size for _ in range(size)]
    for col in range(size):
        column = [board[row][col] for row in range(size)]
        merged, gained, changed = move_and_merge(column)
        for row in range(size):
            new_board[row][col] = merged[row]
        gained_total += gained
        changed_any = changed_any or changed
    return new_board, gained_total, changed_any

def move_down(board):
    changed_any = False
    gained_total = 0
    new_board = [[0] * size for _ in range(size)]
    for col in range(size):
        column = [board[row][col] for row in range(size)]
        column.reverse()
        merged, gained, changed = move_and_merge(column)
        merged.reverse()
        for row in range(size):
            new_board[row][col] = merged[row]
        gained_total += gained
        changed_any = changed_any or changed
    return new_board, gained_total, changed_any

def apply_move(board, move):
    if move == "L":
        return move_left(board)
    if move == "R":
        return move_right(board)
    if move == "U":
        return move_up(board)
    if move == "D":
        return move_down(board)
    else:
        raise ValueError("Unknown move")

def legal_moves(board):
    moves = []
    for m in ("L", "R", "U", "D"):
        new_board, score, changed = apply_move(board, m)
        if changed:
            moves.append(m)
    return moves

# A random value on an empty tile can be 2 (90%) or 4 (10%). We generate the possible spawn states.
def spawns(board):
    empties = empty(board)
    if not empties:
        return [(1, board)]
    prob_tile = 1 / len(empties)
    states = []
    for row, col in empties:
        p2 = [r[:] for r in board]
        p2[row][col] = 2
        states.append((prob_tile * 0.9, p2))
        p4 = [r[:] for r in board]
        p4[row][col] = 4
        states.append((prob_tile * 0.1, p4))
    return states