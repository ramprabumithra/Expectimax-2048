# ai_player.py
# AI agent for 2048 game using Expectimax search technique.
from __future__ import annotations
import math
from game_engine import new_board, size, legal_moves, apply_move, spawns

# Snake pattern weights so that the larger-valued tiles end up in corners.
# Highest value ends up in top-left corner, mimicing mobile-game behaviour.
snake_weights = (
    (4**15, 4**14, 4**13, 4**12),
    (4**8,  4**9,  4**10,  4**11),
    (4**7,  4**6,  4**5,   4**4),
    (4**0,  4**1,  4**2,   4**3),
)

# Configuration of storing weights and search depth in Expectimax technique.
class conf2048:
    def __init__(self):
        self.depth = 3
        self.weight_empty = 200
        self.weight_boardpos = 1
        self.weight_sim = 0.05
        self.weight_block = 200

# Empty tiles are essential for the game's progression.
def count_empty(board):
    count = 0
    for row in range(size):
        for col in range(size):
            if board[row][col] == 0:
                count += 1
    return count

# We ensure similar values between neighbouring tiles so that the game-playing is smoother and the larger-values end up in the corners.
def board_sim(board):
    sim_score = 0
    for row in range(size):
        for col in range(size):
            current_val = board[row][col]
            if current_val == 0:
                continue
            # Tile values grow exponentially (2,4,8,16,32,64,...), so we use logs for comparing the tile similarities.
            log_current = math.log(current_val, 2)
            if row + 1 < size and board[row + 1][col] != 0:
                sim_score += abs(log_current - math.log(board[row + 1][col], 2))
            if col + 1 < size and board[row][col + 1] != 0:
                sim_score += abs(log_current - math.log(board[row][col + 1], 2))
    return sim_score

# Evaluation of board position
def evaluate_board(board, config: conf2048):
    empty_tiles = count_empty(board)
    snake = snake_score(board)
    sim_penalty = board_sim(board) 
    blocking_penalty = blocking_tile(board)
    return ( # We combine all the heuristics with their respective weights to get the final score for current board state.
        config.weight_boardpos * snake
        + config.weight_empty * empty_tiles
        - config.weight_sim * sim_penalty
        - config.weight_block * blocking_penalty
    )

# We use Expectimax instead of minimax as the game environment is stochastic (new tiles spawn randomly).
def best_move(board, config: conf2048):
    cache = {} # We create a Cache to store all the previous states and values for faster code computation.
    def expectimax_val(board, depth, player_turn):
        key = (tuple(map(tuple, board)), depth, player_turn)
        if key in cache:
            return cache[key]
        moves = legal_moves(board)
        if depth <= 0 or not moves:
            result = evaluate_board(board, config)
            cache[key] = result
            return result
        if player_turn:
            best_val = -1e18
            for move in moves:
                new_board, _, _ = apply_move(board, move)
                value = expectimax_val(new_board, depth - 1, False)
                best_val = max(best_val, value)
            cache[key] = best_val
            return best_val
        else:
            expected_val = 0
            for prob, next_board in spawns(board):
                # We calculate the expected value of the random tile by finding the avg. of all possible values weighted by their probabilities.
                expected_val += prob * expectimax_val(next_board, depth - 1, True)
            cache[key] = expected_val
            return expected_val

    moves = legal_moves(board)
    if not moves:
        return None
    best_action = moves[0]
    best_score = -1e18 # We make the best score very low initially so that any score from player is higher than it.
    for move in moves:
        new_board, _, _ = apply_move(board, move)
        value = expectimax_val(new_board, config.depth - 1, False)
        if value > best_score:
            best_score = value
            best_action = move
    return best_action

# Snake pattern assigns a higher weight to corners and lower to centre, so that the larger values move to corners of board.
def snake_score(board):
    score = 0
    for row in range(size):
        for col in range(size):
            tile = board[row][col]
            if tile:
                score += snake_weights[row][col] * math.log(tile, 2)
    return score

# We penalise the blocking tiles, because they prevent the merging of similar-valued tiles.
def blocking_tile(board):
    penalty = 0
    for row in range(size):
        for col in range(size - 1):
            if board[row][col] < board[row][col + 1]:
                penalty += 1
    return penalty