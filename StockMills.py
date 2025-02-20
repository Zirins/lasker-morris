import sys
import math
import time

NEIGHBORS = {
    "a1": ["a4", "d1"],
    "a4": ["a1", "a7", "b4"],
    "a7": ["a4", "d7"],
    "b2": ["b4", "d2"],
    "b4": ["b2", "b6", "a4", "c4"],
    "b6": ["b4", "d6"],
    "c3": ["c4", "d3"],
    "c4": ["c3", "c5", "b4"],
    "c5": ["c4", "d5"],
    "d1": ["a1", "d2", "g1"],
    "d2": ["b2", "d1", "d3", "f2"],
    "d3": ["c3", "d2", "e3"],
    "d5": ["c5", "d6", "e5"],
    "d6": ["b6", "d5", "d7", "f6"],
    "d7": ["a7", "d6", "g7"],
    "e3": ["d3", "e4"],
    "e4": ["e3", "e5", "f4"],
    "e5": ["d5", "e4"],
    "f2": ["d2", "f4"],
    "f4": ["e4", "f2", "f6", "g4"],
    "f6": ["d6", "f4"],
    "g1": ["d1", "g4"],
    "g4": ["f4", "g1", "g7"],
    "g7": ["d7", "g4"],
}

MILLS = [
    # Horizontal mills
    ["a1", "a4", "a7"],
    ["b2", "b4", "b6"],
    ["c3", "c4", "c5"],
    ["d1", "d2", "d3"],
    ["d5", "d6", "d7"],
    ["e3", "e4", "e5"],
    ["f2", "f4", "f6"],
    ["g1", "g4", "g7"],
    # Vertical mills
    ["a1", "d1", "g1"],
    ["b2", "d2", "f2"],
    ["c3", "d3", "e3"],
    ["a4", "b4", "c4"],
    ["e4", "f4", "g4"],
    ["c5", "d5", "e5"],
    ["b6", "d6", "f6"],
    ["a7", "d7", "g7"],
]





def check_mill(board, point, color):
    """
    Returns True if placing/moving a stone of 'color' at 'point' forms a mill.
    We only need to check lines that include 'point'
    :param board:
    :param point:
    :param color:
    :return:
    """
    for trio in MILLS:
        if point in trio:
            stones_count = 0
            for p in trio: # check if all points in the trio have the same color
                if p == point:
                    stones_count += 1
                elif board[p] == color:
                    stones_count += 1
            if stones_count == 3:
                return True
    return False









def check_win(board, symbol):
    # Check rows
    for row in ['a', 'b', 'c']:
        if board[f"{row}1"] == symbol and board[f"{row}2"] == symbol and board[f"{row}3"] == symbol:
            return True
    # Check columns
    for col in ['1', '2', '3']:
        if board[f"a{col}"] == symbol and board[f"b{col}"] == symbol and board[f"c{col}"] == symbol:
            return True
    # Check diagonals
    if board['a1'] == symbol and board['b2'] == symbol and board['c3'] == symbol:
        return True
    if board['a3'] == symbol and board['b2'] == symbol and board['c1'] == symbol:
        return True
    return False

def is_draw(board):
    return ' ' not in board.values()

def get_empty_cells(board):
    return [cell for cell, val in board.items() if val == ' ']

def make_move(board, move, symbol):
    new_board = board.copy()
    new_board[move] = symbol
    return new_board

def minimax(board, depth, is_maximizing, alpha, beta, player_symbol, opponent_symbol):
    if check_win(board, player_symbol):
        return (100 - depth, None)
    if check_win(board, opponent_symbol):
        return (-100 + depth, None)
    if is_draw(board):
        return (0, None)

    if is_maximizing:
        best_value = float('-inf')
        best_move = None
        for move in get_empty_cells(board):
            new_board = make_move(board, move, player_symbol)
            value, _ = minimax(new_board, depth+1, False, alpha, beta, player_symbol, opponent_symbol)
            if value > best_value:
                best_value, best_move = value, move
            alpha = max(alpha, best_value)
            if beta <= alpha:
                break
        return (best_value, best_move)
    else:
        best_value = float('inf')
        best_move = None
        for move in get_empty_cells(board):
            new_board = make_move(board, move, opponent_symbol)
            value, _ = minimax(new_board, depth+1, True, alpha, beta, player_symbol, opponent_symbol)
            if value < best_value:
                best_value, best_move = value, move
            beta = min(beta, best_value)
            if beta <= alpha:
                break
        return (best_value, best_move)

def main():
    player_color = sys.stdin.readline().strip()
    if player_color not in ['blue', 'orange']:
        return

    player_symbol = 'B' if player_color == 'blue' else 'O'
    opponent_symbol = 'O' if player_color == 'blue' else 'B'

    # Define invalid board positions
    # self.invalid_fields: Set[str] = {
    #     "a2",
    #     "a3",
    #     "a5",
    #     "a6",
    #     "b1",
    #     "b3",
    #     "b5",
    #     "b7",
    #     "c1",
    #     "c2",
    #     "c6",
    #     "c7",
    #     "d4",
    #     "e1",
    #     "e2",
    #     "e6",
    #     "e7",
    #     "f1",
    #     "f3",
    #     "f5",
    #     "f7",
    #     "g2",
    #     "g3",
    #     "g5",
    #     "g6",
    # }

    #board = {f"{r}{c}": ' ' for r in ['a','b','c'] for c in ['1','2','3']}
    board = {
        'a7': '', 'd7': '', 'g7': '',
        'b6': '', 'd6': '', 'f6': '',
        'c5': '', 'd5': '', 'e5': '',
        'a4': '', 'b4': '', 'c4': '', 'e4': '', 'f4': '', 'g4': '',
        'c3': '', 'd3': '', 'e3': '',
        'b2': '', 'd2': '', 'f2': '',
        'a1': '', 'd1': '', 'g1': ''
    }

    if player_color == 'blue':
        _, move = minimax(board, 0, True, float('-inf'), float('inf'), player_symbol, opponent_symbol)
        print(move, flush=True)
        board[move] = player_symbol

    while True:
        try:
            line = sys.stdin.readline().strip()
            if not line or line.startswith('END'):
                break

            opponent_move = line
            if opponent_move in board and board[opponent_move] == ' ':
                board[opponent_move] = opponent_symbol

            start = time.time()
            _, move = minimax(board, 0, True, float('-inf'), float('inf'), player_symbol, opponent_symbol)
            end = time.time()
            elapsed = end - start

            print(move, flush=True)
            board[move] = player_symbol
        except EOFError:
            break

if __name__ == '__main__':
    main()