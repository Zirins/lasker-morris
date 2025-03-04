import sys
import math
import time

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

MILLS = [
    # Horizontal lines
    ["a1", "a4", "a7"],
    ["b2", "b4", "b6"],
    ["c3", "c4", "c5"],
    ["d1", "d2", "d3"],
    ["d5", "d6", "d7"],
    ["e3", "e4", "e5"],
    ["f2", "f4", "f6"],
    ["g1", "g4", "g7"],
    # Vertical lines
    ["a1", "d1", "g1"],
    ["b2", "d2", "f2"],
    ["c3", "d3", "e3"],
    ["a4", "b4", "c4"],
    ["e4", "f4", "g4"],
    ["c5", "d5", "e5"],
    ["b6", "d6", "f6"],
    ["a7", "d7", "g7"]
]

def create_initial_board():
    valid_points = [
        "a7", "d7", "g7",
        "b6", "d6", "f6",
        "c5", "d5", "e5",
        "a4", "b4", "c4", "e4", "f4", "g4",
        "c3", "d3", "e3",
        "b2", "d2", "f2",
        "a1", "d1", "g1"
    ]
    board = {}
    for pt in valid_points:
        board[pt] = None
    return board

def hand_src(color):
    return "h1" if color == "blue" else "h2"

def count_on_board(board, color):
    return sum(1 for occupant in board.values() if occupant == color)

def is_stone_in_mill(board, location, color):
    for triple in MILLS:
        if location in triple:
            if all(board[t] == color for t in triple):
                return True
    return False

def can_remove_this_stone(board, pos, opp):
    """
    Stones in mills cannot be removed unless all opp pieces are in mills
    """
    if not is_stone_in_mill(board, pos, opp):
        return True
    for p, occupant in board.items():
        if occupant == opp and not is_stone_in_mill(board, p, opp):
            return False
    return True

def possible_removals(board, opp):
    removables = []
    for pos, occupant in board.items():
        if occupant == opp and can_remove_this_stone(board, pos, opp):
            removables.append(pos)
    return removables

def forms_mill_after_placement(board, point, color):
    old = board[point]
    board[point] = color
    res = is_stone_in_mill(board, point, color)
    board[point] = old
    return res

def forms_mill_after_move(board, source, target, color):
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
    Generate all valid moves for player state as a list of tuples.
    """
    board = state["board"]
    color = state["current_player"]
    opp = "blue" if color == "orange" else "orange"
    in_hand = state["in_hand"][color]
    moves = []

    if in_hand > 0:
        for point, occupant in board.items():
            if occupant is None:
                if forms_mill_after_placement(board, point, color):
                    remove_list = possible_removals(board, opp)
                    for rpos in remove_list:
                        moves.append((hand_src(color), point, rpos))
                else:
                    moves.append((hand_src(color), point, "r0"))

    my_positions = [p for p, occupant in board.items() if occupant == color]
    can_fly = (len(my_positions) + in_hand == 3)

    for src in my_positions:
        if can_fly:
            for tgt, occupant in board.items():
                if occupant is None:
                    if forms_mill_after_move(board, src, tgt, color):
                        remove_list = possible_removals(board, opp)
                        for rpos in remove_list:
                            moves.append((src, tgt, rpos))
                    else:
                        moves.append((src, tgt, "r0"))
        else:
            for tgt in ADJACENCY.get(src, []):
                if board[tgt] is None:
                    if forms_mill_after_move(board, src, tgt, color):
                        remove_list = possible_removals(board, opp)
                        for rpos in remove_list:
                            moves.append((src, tgt, rpos))
                    else:
                        moves.append((src, tgt, "r0"))
    return moves

def apply_move(state, source, target, remove):
    new_state = clone_state(state)
    board = new_state["board"]
    color = new_state["current_player"]

    if source.startswith("h"):
        new_state["in_hand"][color] -= 1
    else:
        board[source] = None

    board[target] = color

    if remove != "r0":
        board[remove] = None

    new_state["current_player"] = "blue" if color == "orange" else "orange"
    return new_state

def clone_state(state):
    """Return a deep copy of the state."""
    return {
        "board": dict(state["board"]),
        "in_hand": dict(state["in_hand"]),
        "current_player": state["current_player"]
    }

def is_terminal(state):
    board = state["board"]
    cblue = count_on_board(board, "blue")
    corange = count_on_board(board, "orange")
    if state["in_hand"]["blue"] == 0 and cblue <= 2:
        return True
    if state["in_hand"]["orange"] == 0 and corange <= 2:
        return True
    return len(generate_moves(state)) == 0

def utility(state):
    board = state["board"]
    color = state["current_player"]
    opp = "blue" if color == "orange" else "orange"
    mycount = count_on_board(board, color)
    oppcount = count_on_board(board, opp)

    if mycount <= 2:
        return -999999
    if oppcount <= 2:
        return 999999
    if not generate_moves(state):
        return -999999
    return 0


def evaluate(state):
    board = state["board"]
    color = state["current_player"]
    opp = "blue" if color == "orange" else "orange"
    score = 0

    # Mill-based scoring
    player_mills = sum(1 for pos, occupant in board.items() if occupant == color and is_stone_in_mill(board, pos, color))
    opp_mills = sum(1 for pos, occupant in board.items() if occupant == opp and is_stone_in_mill(board, pos, opp))
    score += 100 * (player_mills - opp_mills)

    # Potential Mills
    player_potential_mills = sum(1 for pos in board if board[pos] == color and forms_mill_after_placement(board, pos, color))
    opponent_potential_mills = sum(1 for pos in board if board[pos] == color and forms_mill_after_placement(board, pos, opp))
    score += 100 * (player_potential_mills - opponent_potential_mills) # Reward for setting up mills

    # Positional advantage
    position_weights = {
        'b2': 3, 'f4': 3, 'd2': 3, 'd6': 3,  # High value for center
        'a4': 2, 'g4': 2, 'd1': 2, 'd7': 2,  # Medium value for edges
        'a7': 1, 'g7': 1, 'a1': 1, 'g1': 1   # Low value for corners
    }
    for pos, occupant in board.items():
        if occupant == color:
            score += position_weights.get(pos, 0)
        else:
            score -= position_weights.get(pos, 0)
        if state["in_hand"] == 0 and is_stone_in_mill(board, pos, color):
            score -= 15

    # Mobility (number of legal moves)
    player_mobility = len(generate_moves(state))
    temp_state = clone_state(state)
    temp_state["current_player"] = opp
    opponent_mobility = len(generate_moves(temp_state))
    score += 10 * (player_mobility - opponent_mobility)

    return score


def evaluate_or_utility(state):
    if is_terminal(state):
        return utility(state)
    return evaluate(state)

def minimax_alpha_beta(state, alpha, beta, depth, max_depth, maximizing, start_time, time_limit):
    if time.time() - start_time >= time_limit:
        return evaluate_or_utility(state), None
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
            val, _ = minimax_alpha_beta(nxt_state, alpha, beta, depth + 1, max_depth, False, start_time, time_limit)
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
        for (src, tgt, rem) in moves:
            nxt_state = apply_move(state, src, tgt, rem)
            val, _ = minimax_alpha_beta(nxt_state, alpha, beta, depth + 1, max_depth, True, start_time, time_limit)
            if val < worst_val:
                worst_val = val
                worst_move = (src, tgt, rem)
            beta = min(beta, worst_val)
            if beta <= alpha:
                break
        return worst_val, worst_move

def iterative_deepening(state, max_iter_depth, time_limit):
    start = time.time()
    best_val_global = -math.inf
    best_move_global = None

    for depth in range(1, max_iter_depth + 1):
        if time.time() - start >= time_limit:
            break
        val, move = minimax_alpha_beta(state, -math.inf, math.inf, 0, depth, True, start, time_limit)
        if time.time() - start >= time_limit:
            break
        if move is not None:
            best_val_global = val
            best_move_global = move
    return best_val_global, best_move_global

def main():
    board = create_initial_board()
    in_hand = {"blue": 10, "orange": 10}
    state = {"board": board, "in_hand": in_hand, "current_player": "blue"}

    color = sys.stdin.readline().strip()
    if color not in ["blue", "orange"]:
        return

    # Blue always starts
    if color == "blue":
        _, best_move = iterative_deepening(state, max_iter_depth=4, time_limit=4.5)
        if not best_move:
            moves = generate_moves(state)
            best_move = moves[0] if moves else ("h1", "a4", "r0")
        s, t, r = best_move
        print(f"{s} {t} {r}", flush=True)
        state = apply_move(state, s, t, r)

    while True:
        try:
            line = sys.stdin.readline().strip()
            if not line or line.startswith("END"):
                break

            # Get opponent's move
            parts = line.split()
            if len(parts) == 3:
                o_src, o_tgt, o_rem = parts
                state = apply_move(state, o_src, o_tgt, o_rem)

            # Calculate our move
            state["current_player"] = color
            _, best_move = iterative_deepening(state, max_iter_depth=10, time_limit=4.5)
            if not best_move:
                moves = generate_moves(state)
                best_move = moves[0] if moves else ("h1", "a4", "r0")
            s, t, r = best_move
            print(f"{s} {t} {r}", flush=True)
            state = apply_move(state, s, t, r)
        except EOFError:
            break

if __name__ == "__main__":
    main()
