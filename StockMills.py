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

def create_initial_board():
    board = {
        'a7': '', 'd7': '', 'g7': '',
        'b6': '', 'd6': '', 'f6': '',
        'c5': '', 'd5': '', 'e5': '',
        'a4': '', 'b4': '', 'c4': '', 'e4': '', 'f4': '', 'g4': '',
        'c3': '', 'd3': '', 'e3': '',
        'b2': '', 'd2': '', 'f2': '',
        'a1': '', 'd1': '', 'g1': ''
    }
    return board

def check_mill(board, point, color):
    """
    Returns True if placing/moving a stone of 'color' at 'point' forms a mill.
    We only need to check lines that include 'point'
    """
    for trio in MILLS:
        if point in trio:
            stones_count = 0
            for p in trio:  # check if all points in the trio have the same color
                if p == point:
                    stones_count += 1
                elif board[p] == color:
                    stones_count += 1
            if stones_count == 3:
                return True
    return False

def count_on_board(board, color): # Potential optimization for single call
    return sum(1 for _, occupant in board.items() if occupant == color)

def hand_src(color):
    return "h1" if color == "blue" else "h2"

def is_terminal(state):
    board = state["board"]
    cblue = count_on_board(board, "blue")
    corange = count_on_board(board, "orange")
    return cblue <= 2 or corange <= 2

def is_stone_is_mill(board, point, color):
    for trio in MILLS:
        if point in trio and all(board[t] == color for t in trio):
            return True
    return False


def can_remove_this_stone(board, pos, opp):
    if not is_stone_is_mill(board, pos, opp):
        return True

    for p, occupant in board.items():
        if occupant == opp:
            if not is_stone_is_mill(board, p, opp):
                return False
    return True


def possible_removals(board, opp):
    # gather all stones of the opponent
    removables = []
    for pos, occupant in board.items():
        if occupant == opp:
            if can_remove_this_stone(board, pos, opp):
                removables.append(pos)
    return removables

def form_mill_after_placement(board, point, color):
    old = board[point]
    board[point] = color
    res = check_mill(board, point, color)
    board[point] = old
    return res

def form_mill_after_move(board, source, target, color):
    old_src = board[source]
    old_tgt = board[target]
    board[source] = None
    board[target] = color
    res = check_mill(board, target, color)
    board[source] = old_src
    board[target] = old_tgt
    return res


def generate_moves(state):
    # Generate all valid moves (source, target, remove) moves for current player
    board = state["board"]
    color = state["current_player"]
    opp = "blue" if color == "orange" else "orange"

    in_hand = state["in_hand"][color]
    moves = []

    # 1) If we still have stones in hand, place from hand to any empty spots
    if in_hand > 0:
        for point, occupant in board.items():
            if occupant is None:
                if form_mill_after_placement(board, point, color):
                    remove_list = possible_removals(board, opp)
                    for rpos in remove_list:
                        moves.append((hand_src(color), point, rpos))
                else:
                    moves.append((hand_src(color), point, None))
    else:
        # 2) Move existing stone
        my_positions = [p for p, occupant in board.items() if occupant == color]
        my_count = len(my_positions)
        can_fly = (my_count == 3)

        for src in my_positions:
            if can_fly:
                # can move to any emty point
                for tgt, occupant in board.items():
                    if occupant is None:
                        if form_mill_after_move(board, src, tgt, color):
                            remove_list = possible_removals(board, opp)
                            for rpos in remove_list:
                                moves.append((src, tgt, rpos))
                        else:
                            moves.append((src, tgt, None))
            else: # normal adjacent move
                neighbors = NEIGHBORS.get(src, [])
                for tgt in neighbors:
                    if board[tgt] is None:
                        if form_mill_after_move(board, src, tgt, color):
                            remove_list = possible_removals(board, opp)
                            for rpos in remove_list:
                                moves.append((src, tgt, rpos))
                            else:
                                moves.append((src, tgt, "r0"))
    return moves

def apply_move(state, source, target, remove):
    new_s = clone_state(state)
    board = new_s["board"]
    color = new_s["current_player"]

    if source.startswith('h'):
        new_s["in_hand"][color] -= 1
    else:
        board[source] = None

    board[target] = color
    if remove != "r0":
        board[remove] = None

    new_s['current player'] = "blue" if color == "orange" else "orange"
    return new_s

def clone_state(state):
    """ Create a copy of the board so we don't mutate the original """
    new_board = dict(state["board"])
    new_in_hand = dict( state["in_hand"])
    return {
        "board": new_board,
        "in_hand": new_in_hand,
        "current_player": state["current_player"]
    }

# def validMove(board, move):
#     for key, value in board.items():
#         if move == key:
#             if board[move] == '':
#                 return True
#     return False

def make_move(board, move, symbol):
    new_board = board.copy()
    new_board[move] = symbol
    return new_board

def score_board(state, move):
    board = state["board"]
    symbol = state["current_player"]
    if symbol == 'B':
        opp_symbol = 'O'
    else:
        opp_symbol = 'B'

    # initialize based on remaining pieces, may need depth check as well
    piece_advantage = 3 * (count_on_board(board, symbol) - count_on_board(board, opp_symbol))
    score = piece_advantage + 2 * state["in_hand"]

    #value from our piece
    if check_mill(board, move, symbol): # create mill with move
        score += 5
        for value in NEIGHBORS[move]:
            if board[value] == '' and check_mill(board, value, symbol): # potential sliding mill
                score += 10
    if move == 'd5' or move == 'd3' or move == 'c4' or move == 'e4': # occupy middle junctions
        score += 1


    if(move[])
    #value from blocking something the opp is doing

    board[move] = opp_symbol
    if check_mill(board, opp_symbol, move): # block opponents mill
        score += 10
        for value in NEIGHBORS[move]:
            if board[value] == '' and check_mill(board, value, opp_symbol): # block potential sliding mill
                score += 20 # should only be possible when placing

    board[move] = symbol
    return score

#
# def evaluate(state):
#     """
#     Non-terminal evaluation:
#         10*(myCount - oppCount) + 2*(myMoves - oppMoves)
#     :param state:
#     :return:
#     """
#
#     my_count = count_on_board(state, color)
#     opp_count

def utility(state):
    board = state["board"]
    color = state["current_player"]
    opo = "blue" if color == "orange" else "orange"

    my_count = count_on_board(board, color)
    opp_count = count_on_board(board, opo)

    if my_count <= 2:
        return -math.inf
    if opp_count <= 2:
        return math.inf
    # no moves = lost
    if not generate_moves(state):
        return -math.inf

    return 0

def evaluate_or_utility(state):
    if is_terminal(state):
        return utility(state)
    return score_board(state)


def minimax(state, alpha, beta, depth, max_depth, maximizing, start_time, time_limit):
    if time.time() - start_time >= limit - 0.05:
       return score_board(state, pre), None

    if depth >= max_depth or is_terminal(states):
        return (evaluate_or_utility(state), None)

    moves = generate_moves(state)


    if maximizing:
        best_value = float('-inf')
        best_move = None
        for (src, tgt, rem) in moves:
            nxt = apply_move(state, src, tgt, rem)
            val, _ = minimax(nxt, alpha, beta, depth + 1, max_depth, False, start_time, time_limit)
            if val > best_val:
                best_val = val
                best_move = (src, tgt, rem)
            alpha = max(alpha, val)
            if beta <= alpha:
                break
        return best_val, best_move
    else:
        worst_val = math.inf
        worst_move = None
        for (src, tgt, rem) in moves:
            nxt = apply_move(state, src, tgt, rem)
            val, _ = minimax(nxt, alpha, beta, depth + 1, max_depth, True, start_time, time_limit)

            if val < worst_val:
                worst_val = val
                worst_move = (src, tgt, rem)
            beta = min(beta, val)
            if beta <= alpha:
                break
        return worst_val, worst_move

def iterative_deepening(state, max_iter_depth, time_limit):
    """Repeated alpha-beta search from depth = 1... max_iter_depth until time runs out"""
    start = time.time()
    best_val_global = -math.inf
    best_move_global = None

    for depth in range (1, max_iter_depth+1):
        if time.time() - start >= time_limit:
            break
        val, move = minimax(state, -math.inf, math.inf, 0, depth, True, start, time_limit, None)

        if time.time() - start >= time_limit:
            break
        if move is not None:
            best_val_global = val
            best_move_global = move

        return best_val_global, best_move_global


def main():
    color = sys.stdin.readline().strip()

    # player_symbol = 'B' if color == 'blue' else 'O'
    # opponent_symbol = 'O' if color == 'blue' else 'B'

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

    board = create_initial_board()
    in_hand =  {"blue": 10, "orange": 10}
    state = {
        "board": board,
        "in_hand": in_hand,
        "current_player": color
    }

    if color == 'blue':
        _, best_move = iterative_deepening(board, max_iter_depth=6, time_limit=4.5)
        if not best_move:
            all_moves = generate_moves(state)
            best_move = all_moves[0] if all_moves else ("h1", "a4", "r0")
            s, t, r= best_move

            # DEBUG
            print(f"[DEBUG] First move (blue): {s} {t} {r}", file=sys.stderr)
            print(f"{s} {t} {r}", flush=True)
            state = apply_move(state, s, t, r)

    while True:
        try:
            line = sys.stdin.readline().strip()
            if not line or line.startswith('END'):
                break

            # Opponent move
            opponent_move = line.split()
            if len(opponent_move) == 3:
                o_src, o_tgt, o_rem = opponent_move
                # Debug
                print(f"[DEBUG] Opponent move: {o_src} {o_tgt} {o_rem}", file=sys.stderr)
                state = apply_move(state, o_src, o_tgt, o_rem)

            # Our turn
            state["current_player"] = color
            _, best_move = iterative_deepening(state, max_iter_depth=6, time_limit=4.5)
            if not best_move:
                all_moves = generate_moves(state)
                best_move = all_moves[0] if all_moves else ("h1","a4","r0")

            s, t, r = best_move
            print(f"[DEBUG] My next move: {s} {t} {r}", file=sys.stderr)
            print(f"{s} {t} {r}", flush=True)
            state = apply_move(state, s, t, r)

        except EOFError:
            break

if __name__ == '__main__':
    main()
