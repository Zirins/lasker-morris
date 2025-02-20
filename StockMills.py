import sys

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

    board = {f"{r}{c}": ' ' for r in ['a','b','c'] for c in ['1','2','3']}

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

            _, move = minimax(board, 0, True, float('-inf'), float('inf'), player_symbol, opponent_symbol)
            print(move, flush=True)
            board[move] = player_symbol
        except EOFError:
            break

if __name__ == '__main__':
    main()