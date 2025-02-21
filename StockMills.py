import sys
import math
import time

###############################################################################
#   my_lasker_player.py - Lasker Morris AI using Minimax + Alpha-Beta +
#   Iterative Deepening
###############################################################################

# Adjacency: Must match referee's notion of neighbors
ADJACENCY = {
    "a1": ["a4", "d1"],
    "a4": ["a1", "a7", "b4"],
    "a7": ["a4", "d7"],
    "b2": ["b4", "d2"],
    "b4": ["b2", "b6", "a4", "c4"],
    "b6": ["b4", "d6"],
    "c3": ["c4", "d3"],
    "c4": ["c3", "c5", "b4"],
    "c5": ["c4", "d5"],
    "d1": ["a1", "g1", "d2"],
    "d2": ["d1", "b2", "d3", "f2"],
    "d3": ["d2", "c3", "e3"],
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
    "g4": ["g1", "f4", "g7"],
    "g7": ["d7", "g4"],
}

# Mills: Must match referee's set
MILLS = [
    # Horizontal lines
    ["a1","a4","a7"],
    ["b2","b4","b6"],
    ["c3","c4","c5"],
    ["d1","d2","d3"],
    ["d5","d6","d7"],
    ["e3","e4","e5"],
    ["f2","f4","f6"],
    ["g1","g4","g7"],
    # Vertical lines
    ["a1","d1","g1"],
    ["b2","d2","f2"],
    ["c3","d3","e3"],
    ["a4","b4","c4"],
    ["e4","f4","g4"],
    ["c5","d5","e5"],
    ["b6","d6","f6"],
    ["a7","d7","g7"]
]

def create_initial_board():
    """
    Initialize a dictionary containing ONLY the 24 valid intersections.
    Each key points to either None, 'blue', or 'orange'.
    """
    valid_points = [
        "a7","d7","g7",
        "b6","d6","f6",
        "c5","d5","e5",
        "a4","b4","c4","e4","f4","g4",
        "c3","d3","e3",
        "b2","d2","f2",
        "a1","d1","g1"
    ]
    board = {}
    for pt in valid_points:
        board[pt] = None
    return board

def hand_src(color):
    """Returns 'h1' if color == 'blue', 'h2' if color == 'orange'."""
    return "h1" if color == "blue" else "h2"

def count_on_board(board, color):
    """Count how many stones 'color' has on the board."""
    return sum(1 for _, occupant in board.items() if occupant == color)

def is_stone_in_mill(board, point, color):
    """Check if the stone at 'point' is part of a fully formed mill."""
    for triple in MILLS:
        if point in triple:
            if all(board[t] == color for t in triple):
                return True
    return False

def can_remove_this_stone(board, pos, opp):
    """
    Stone removal rule:
    - If the stone is not in a mill, removable.
    - If it's in a mill, only removable if ALL opp stones are in mills.
    """
    if not is_stone_in_mill(board, pos, opp):
        return True
    # Stone is in a mill => check if opp has a stone not in a mill
    for p, occupant in board.items():
        if occupant == opp and not is_stone_in_mill(board, p, opp):
            return False
    return True

def possible_removals(board, opp):
    """
    Return a list of positions of opp stones that can be removed,
    obeying the "cannot remove from mill if there's a stone not in a mill" rule.
    """
    removables = []
    for pos, occupant in board.items():
        if occupant == opp:
            if can_remove_this_stone(board, pos, opp):
                removables.append(pos)
    return removables

def forms_mill_after_placement(board, point, color):
    """Place a stone at 'point' temporarily, check mill, then revert."""
    old = board[point]
    board[point] = color
    res = is_stone_in_mill(board, point, color)
    board[point] = old
    return res

def forms_mill_after_move(board, source, target, color):
    """Move stone from 'source' to 'target' temporarily, check mill, then revert."""
    old_src = board[source]
    old_tgt = board[target]
    board[source] = None
    board[target] = color
    res = is_stone_in_mill(board, target, color)
    board[source] = old_src
    board[target] = old_tgt
    return res

def generate_moves(state):
    """
    Generate all valid moves for state['current_player'] as a list of
    (source, target, remove).
    """
    board = state["board"]
    color = state["current_player"]
    opp = "blue" if color == "orange" else "orange"

    in_hand = state["in_hand"][color]
    moves = []

    # 1) If we still have stones in hand, place from hand to any empty board point
    if in_hand > 0:
        for point, occupant in board.items():
            if occupant is None:
                # If placing here forms a mill
                if forms_mill_after_placement(board, point, color):
                    remove_list = possible_removals(board, opp)
                    for rpos in remove_list:
                        moves.append((hand_src(color), point, rpos))
                else:
                    moves.append((hand_src(color), point, "r0"))
    else:
        # 2) Move one of our on-board stones
        my_positions = [p for p, occupant in board.items() if occupant == color]
        my_count = len(my_positions)

        # If exactly 3 on board, we can "fly" anywhere. If >3, move only to adjacent.
        can_fly = (my_count == 3)

        for src in my_positions:
            if can_fly:
                # Move to any empty point
                for tgt, occupant in board.items():
                    if occupant is None:
                        if forms_mill_after_move(board, src, tgt, color):
                            remove_list = possible_removals(board, opp)
                            for rpos in remove_list:
                                moves.append((src, tgt, rpos))
                        else:
                            moves.append((src, tgt, "r0"))
            else:
                # Only to adjacent
                neighbors = ADJACENCY.get(src, [])
                for tgt in neighbors:
                    if board[tgt] is None:
                        if forms_mill_after_move(board, src, tgt, color):
                            remove_list = possible_removals(board, opp)
                            for rpos in remove_list:
                                moves.append((src, tgt, rpos))
                        else:
                            moves.append((src, tgt, "r0"))
    return moves

def apply_move(state, source, target, remove):
    """
    Applies (source -> target, remove) to produce a new game state,
    decrementing the in-hand if from 'h1'/'h2', removing stones if needed.
    """
    new_s = clone_state(state)
    board = new_s["board"]
    color = new_s["current_player"]

    # If from hand (h1 or h2), reduce the player's hand
    if source.startswith("h"):
        new_s["in_hand"][color] -= 1
    else:
        board[source] = None

    board[target] = color

    # If remove != 'r0', remove that stone
    if remove != "r0":
        board[remove] = None

    # Switch turn
    new_s["current_player"] = "blue" if color == "orange" else "orange"
    return new_s

def clone_state(state):
    """Return a copy of the state so we don't mutate the original."""
    board_copy = dict(state["board"])
    in_hand_copy = dict(state["in_hand"])
    return {
        "board": board_copy,
        "in_hand": in_hand_copy,
        "current_player": state["current_player"]
    }

def is_terminal(state):
    """
    Basic terminal check:
      - If 'blue' <= 2 stones or 'orange' <= 2 stones => game ends
      - If current player has no moves => game ends
    """
    board = state["board"]
    cblue = count_on_board(board, "blue")
    corange = count_on_board(board, "orange")
    if state["in_hand"]["blue"] == 0 and cblue <= 2:
        return True
    if state["in_hand"]["orange"] == 0 and corange <= 2:
        return True

    # If current player cannot move
    moves = generate_moves(state)
    return (len(moves) == 0)

def utility(state):
    """
    If terminal, +∞ if current_player is effectively the 'winner',
    -∞ if the current_player lost, else 0 for a tie (rare in Lasker).
    """
    board = state["board"]
    color = state["current_player"]
    opp = "blue" if color == "orange" else "orange"

    mycount = count_on_board(board, color)
    oppcount = count_on_board(board, opp)

    # If we have <=2 => we lose
    if mycount <= 2:
        return -999999
    # If opp <= 2 => we win
    if oppcount <= 2:
        return 999999

    # No moves => we lose
    if not generate_moves(state):
        return -999999

    return 0

def evaluate(state):
    """
    Heuristic evaluation for non-terminal states:
     - piece difference
     - mobility difference
    Additional factors can be added for potential mills, blocking, etc.
    """
    board = state["board"]
    color = state["current_player"]
    opp = "blue" if color == "orange" else "orange"
    score = 0

    mycount = count_on_board(board, color)
    oppcount = count_on_board(board, opp)

    # Mobility for me
    my_moves = generate_moves(state)

    # Mobility for opp
    alt_state = clone_state(state)
    alt_state["current_player"] = opp
    opp_moves = generate_moves(alt_state)

    center_positions = ["d5", "d3", "c4", "e4"]
    center_score = sum(1 if board[pos] == color else -1 if board[pos] == opp else 0 for pos in center_positions)
    for item in my_moves:
        if is_stone_in_mill(board, item, color):
            score += 20
    for item in opp_moves:
        if is_stone_in_mill(board, item, opp):
            score -= 30

    # Weighted sum
    score += 2*(mycount - oppcount) + (len(my_moves) - len(opp_moves)) + center_score
    return score

def evaluate_or_utility(state):
    """Return utility if terminal, otherwise heuristic evaluation."""
    if is_terminal(state):
        return utility(state)
    return evaluate(state)

def minimax_alpha_beta(state, alpha, beta, depth, max_depth, maximizing, start_time, time_limit):
    """
    Depth-limited alpha-beta.
    'maximizing' is True if it's the current_player's perspective,
    'start_time','time_limit' used for time check.
    """
    # Time check
    if time.time() - start_time >= time_limit:
        return evaluate_or_utility(state), None

    # Depth or terminal check
    if depth >= max_depth or is_terminal(state):
        return evaluate_or_utility(state), None

    moves = generate_moves(state)
    if not moves:
        return evaluate_or_utility(state), None

    if maximizing:
        best_val = -math.inf
        best_move = None
        for (src, tgt, rem) in moves:
            nxt_state = apply_move(state, src, tgt, rem)
            val, _ = minimax_alpha_beta(nxt_state, alpha, beta,
                                        depth+1, max_depth,
                                        False, start_time, time_limit)
            if val > best_val:
                best_val = val
                best_move = (src, tgt, rem)
            alpha = max(alpha, best_val)
            if beta <= alpha:
                break
        return best_val, best_move
    else:
        worst_val = math.inf
        worst_move = None
        # For the minimizing perspective, we must "simulate" the opponent's moves
        for (src, tgt, rem) in moves:
            nxt_state = apply_move(state, src, tgt, rem)
            val, _ = minimax_alpha_beta(nxt_state, alpha, beta,
                                        depth+1, max_depth,
                                        True, start_time, time_limit)
            if val < worst_val:
                worst_val = val
                worst_move = (src, tgt, rem)
            beta = min(beta, worst_val)
            if beta <= alpha:
                break
        return worst_val, worst_move

def iterative_deepening(state, max_iter_depth, time_limit):
    """
    Iterative deepening from depth=1..max_iter_depth until we run out of time.
    Returns the best move from the deepest fully completed search.
    """
    start = time.time()
    best_val_global = -math.inf
    best_move_global = None

    for depth in range(1, max_iter_depth+1):
        if time.time() - start >= time_limit:
            break
       # print(depth)
        val, move = minimax_alpha_beta(state, -math.inf, math.inf,
                                       0, depth,
                                       True, start, time_limit)
        if time.time() - start >= time_limit:
            break
        # print (move)
        # print (val)
        if move is not None:
            if val > best_val_global:
                best_val_global = val
                best_move_global = move
    return best_val_global, best_move_global

def main():
    board = create_initial_board()
    in_hand = {"blue": 10, "orange": 10}
    state = {
        "board": board,
        "in_hand": in_hand,
        "current_player": "blue"
    }

    color = sys.stdin.readline().strip()
    if color not in ["blue", "orange"]:
        return

    # If we're first (blue), produce a move immediately
    if color == "blue":
        _, best_move = iterative_deepening(state, max_iter_depth=4, time_limit=4.5)
        # If no move found, fallback
        if not best_move:
            print("fallback move")
            all_moves = generate_moves(state)
            best_move = all_moves[0] if all_moves else ("h1","a4","r0")
        s, t, r = best_move
        print(f"{s} {t} {r}", flush=True)
        state = apply_move(state, s, t, r)
    while True:
        try:
            line = sys.stdin.readline().strip()
            if not line:
                break
            if line.startswith("END"):
                break

            # Opponent's move
            parts = line.split()
            # print (parts)
            if len(parts) == 3:
                o_src, o_tgt, o_rem = parts
                # Apply opponent move
                state = apply_move(state, o_src, o_tgt, o_rem)

            # Now our turn
            state["current_player"] = color
            _, best_move = iterative_deepening(state, max_iter_depth=4, time_limit=4.5)
            if not best_move:
                print("fallback move")
                all_moves = generate_moves(state)
                best_move = all_moves[0] if all_moves else ("h1","a4","r0")

            s, t, r = best_move
            print(f"{s} {t} {r}", flush=True)
            state = apply_move(state, s, t, r)

        except EOFError:
            break

if __name__ == "__main__":
    main()
