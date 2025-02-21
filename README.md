# lasker-morris
# ok now this is epic

## Setup

Follow these steps to set up the project:

1. **Clone the repository**
   ```sh
   git clone <your-repo-url>
   cd <your-repo-name>
   ```

2. **Create a virtual environment**
   ```sh
   python -m venv venv
   ```

3. **Activate the virtual environment**
    - **Windows (PowerShell)**:
      ```sh
      .\venv\Scripts\Activate
      ```
    - **macOS/Linux**:
      ```sh
      source venv/bin/activate
      ```

4. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

---

### **Additional Notes**
- Activate the virtual environment before running the project.
- To deactivate the virtual environment, run:
  ```sh
  deactivate
  ```

Contributions

Benson - Wrote most helper functions for mills, move generations, and algorithm/heuristics improvements.
Ethan - Helped debug and create heuristics with shawn and wrote the valid move function
Shawn: created evaluate function, spent an unfortunate amount of time debugging, worked on mill detection

These are the algorithms and utilities/evaluations:

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

    mycount = count_on_board(board, color)
    oppcount = count_on_board(board, opp)

    # Mobility evaluation.
    my_moves = generate_moves(state)
    alt_state = clone_state(state)
    alt_state["current_player"] = opp
    opp_moves = generate_moves(alt_state)

    # Center control bonus.
    center_positions = ["d5", "d3", "c4", "e4"]
    center_score = sum(1 if board[pos] == color else -1 if board[pos] == opp else 0 for pos in center_positions)
    for pos in center_positions:
        if board.get(pos) == color:
            center_score += 1
        elif board.get(pos) == opp:
            center_score -= 1

    # Bonus for stones that are part of a mill.
    my_mill_bonus = sum(20 for pos, occupant in board.items() if occupant == color and is_stone_in_mill(board, pos, color))
    opp_mill_penalty = sum(30 for pos, occupant in board.items() if occupant == opp and is_stone_in_mill(board, pos, opp))

    score += 2 * (mycount - oppcount)
    score += (len(my_moves) - len(opp_moves))
    score += center_score
    score += my_mill_bonus - opp_mill_penalty

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

Results: Draw