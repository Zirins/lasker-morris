import os
import sys
import math
import time
import re
from google import genai
from dotenv import load_dotenv

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

# Define invalid board positions
INVALID = {
    "a2",
    "a3",
    "a5",
    "a6",
    "b1",
    "b3",
    "b5",
    "b7",
    "c1",
    "c2",
    "c6",
    "c7",
    "d4",
    "e1",
    "e2",
    "e6",
    "e7",
    "f1",
    "f3",
    "f5",
    "f7",
    "g2",
    "g3",
    "g5",
    "g6",
}

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

def is_board_empty(board):
    return all(value is None for value in board.values())

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
    else:
        my_positions = [p for p, occupant in board.items() if occupant == color]
        can_fly = (len(my_positions) == 3)
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

def extract_move_from_text(text):
    start = text.find("~")
    end = text.rfind("~")
    if start != -1 and end != -1 and start < end:
        move_str = text[start + 1:end].strip()
        parts = move_str.split()
        if len(parts) == 3:
            return tuple(parts)
    return None

def hey_google(state, chat):

    #for attempt in range(5):
    if is_board_empty(state["board"]):
        prompt = f"""Since we are moving first, we will now provide the format for the empty board.
           
           Board:
           {state["board"]}
           What move should we open with?
            """
    else:
        prompt  = f"""This is the new game state after the other player made their move:
        
            Board:
            {state["board"]}
            What is the best move from this new position?
            """

    try:
        response = chat.send_message(prompt)
        llm_output = response.text.strip()

        # Extract a valid move from the LLM's response
        match = re.search(r'~(\S+) (\S+) (\S+)~', llm_output)
        match = match.group(0).replace("~","")
        if match:
            move = match.split()
            # print(f"LLM Suggested Move: {move}")

            if tuple(move) in generate_moves(state):
                return move
            else:
                for i in range(1,5):
                    prompt = "The move you suggested is invalid. Please choose a valid move."
                    response = chat.send_message(prompt)
                    llm_output = response.text.strip()
                    match = re.search(r'~(\S+) (\S+) (\S+)~', llm_output)
                    match = match.group(0).replace("~", "")
                    match = match.group(0).replace("~", "")
                    if match:
                        move = match.split()
                        #   print(f"LLM Suggested Move: {move}")

                        if tuple(move) in generate_moves(state):
                            return move
                valid_moves = generate_moves(state) # ai was not cooking
                return valid_moves[0] if valid_moves else ("h1", "a1", "r0")
        #print(f"LLM gave an invalid move, Falling back to a random move")


    except Exception as e:
        print(f"Error calling Gemini API: {e}")


        valid_moves = generate_moves(state)
        return valid_moves[0] if valid_moves else ("h1", "a1", "r0")

    # print(response.text)
    move = response.text
    return move

def main():
    board = create_initial_board()
    load_dotenv()
    in_hand = {"blue": 10, "orange": 10}
    state = {"board": board, "in_hand": in_hand, "current_player": "blue"}
    api_key = os.environ.get("API_KEY")

    client = genai.Client(api_key = api_key)
    chat = client.chats.create(model="gemini-2.0-flash")
    color = sys.stdin.readline().strip()
    if color not in ["blue", "orange"]:
        return


    prompt = """ I am about to play a text-based game of Lasker Morris and I want to make the best move possible.
    The board uses coordinates like a chessboard: `a1` is the bottom-left, and `g7` is the top-right. 
    Moves must use **ONLY valid board positions**:
    ["a1", "a4", "a7", "b2", "b4", "b6", "c3", "c4", "c5", "d1", "d2", "d3", "d5", "d6", "d7", "e3", "e4", "e5", "f2", "f4", "f6", "g1", "g4", "g7"].
    
    ###  **Move Format**
    - **Placing a piece** (if still in hand): `"h1 d2 r0"` (for blue) OR `"h2 d2 r0"` (for orange).  
    - **Moving a piece**: `"d2 d3 r0"` (normal move, no mill formed).  
    - **Moving + forming a mill**: `"d2 d3 a7"` (removes opponent's stone at `a7`).
    - **If you form a mill, YOU MUST REMOVE** an opponent's stone.
    - **If no mill is formed, use `"r0"` as the third value**.
    
    ###  **How to Respond**
    - **ONLY output the move** inside `~` tildes.  
    - **Example Correct Output:** `~h1 d2 r0~` or `~d2 d3 a7~`  
    - **DO NOT include explanations, reasoning, or anything else.**  
    
    I will now provide the board state and game information. Respond with your move.
    """
    init = chat.send_message(prompt)
    #print(init.text)

    # Blue always starts
    if color == "blue":
        prompt = "We are the blue player, which means we are moving first. My next prompt will contain the format for the empty board"
        chat.send_message(prompt)
        # print(response.text)
        best_move = hey_google(state, chat)
        s, t, r = best_move
        print(f"{s} {t} {r}", flush=True)
        state = apply_move(state, s, t, r)
    else:
        prompt = "We are the orange player, which means we are moving second. My next prompt will contain the game state after blue's opening move."
        chat.send_message(prompt)
        #print(response.text)

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
            best_move = hey_google(state, chat)
            s, t, r = best_move
            print(f"{s} {t} {r}", flush=True)
            state = apply_move(state, s, t, r)
        except EOFError:
            break

if __name__ == "__main__":
    main()
