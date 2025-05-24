import streamlit as st
import copy
import math

st.set_page_config(layout="wide")

def initial():
    return [
        ["r", "n", "b", "q", "k", "b", "n", "r"],
        ["p"] * 8,
        ["."] * 8,
        ["."] * 8,
        ["."] * 8,
        ["."] * 8,
        ["P"] * 8,
        ["R", "N", "B", "Q", "K", "B", "N", "R"]
    ]

def evaluate(board):
    values = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 100,
              "p": -1, "n": -3, "b": -3, "r": -5, "q": -9, "k": -100}
    score = 0
    for row in board:
        for piece in row:
            score += values.get(piece, 0)
    return score

def terminal(board):
    return not any("K" in row for row in board) or not any("k" in row for row in board)

def in_bounds(i, j):
    return 0 <= i < 8 and 0 <= j < 8

def is_opponent(piece, white_turn):
    return (white_turn and piece.islower()) or (not white_turn and piece.isupper())

def is_friend(piece, white_turn):
    return (white_turn and piece.isupper()) or (not white_turn and piece.islower())

def generate_moves(board, white_turn):
    moves = []
    directions = {
        "P": [(-1, 0)], "p": [(1, 0)],
        "N": [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
              (1, -2), (1, 2), (2, -1), (2, 1)],
        "B": [(-1, -1), (-1, 1), (1, -1), (1, 1)],
        "R": [(-1, 0), (1, 0), (0, -1), (0, 1)],
        "Q": [(-1, -1), (-1, 1), (1, -1), (1, 1),
              (-1, 0), (1, 0), (0, -1), (0, 1)],
        "K": [(-1, -1), (-1, 1), (1, -1), (1, 1),
              (-1, 0), (1, 0), (0, -1), (0, 1)]
    }

    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if piece == "." or not is_friend(piece, white_turn):
                continue

            piece_type = piece.upper()
            dirs = directions.get(piece_type, [])
            steps = 1 if piece_type in "KNP" else 8

            for dx, dy in dirs:
                for step in range(1, steps + 1):
                    ni, nj = i + dx * step, j + dy * step
                    if not in_bounds(ni, nj):
                        break
                    target = board[ni][nj]
                    if is_friend(target, white_turn):
                        break
                    if piece_type == "P":
                        if dy == 0 and target == ".":
                            moves.append(((i, j), (ni, nj)))
                        elif dy != 0 and target != "." and is_opponent(target, white_turn):
                            moves.append(((i, j), (ni, nj)))
                        break
                    else:
                        moves.append(((i, j), (ni, nj)))
                        if target != ".":
                            break
    return moves

def apply_move(board, move):
    (i1, j1), (i2, j2) = move
    new_board = copy.deepcopy(board)
    new_board[i2][j2] = new_board[i1][j1]
    new_board[i1][j1] = "."
    # Promotion
    if new_board[i2][j2] == "P" and i2 == 0:
        new_board[i2][j2] = "Q"
    if new_board[i2][j2] == "p" and i2 == 7:
        new_board[i2][j2] = "q"
    return new_board

def minimax(board, depth, alpha, beta, maximizing):
    if terminal(board) or depth == 0:
        return evaluate(board), None

    best_move = None
    moves = generate_moves(board, white_turn=maximizing)

    if maximizing:
        max_eval = -math.inf
        for move in moves:
            eval, _ = minimax(apply_move(board, move), depth - 1, alpha, beta, False)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = math.inf
        for move in moves:
            eval, _ = minimax(apply_move(board, move), depth - 1, alpha, beta, True)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move

def board_to_unicode(piece):
    symbols = {
        "K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙",
        "k": "♚", "q": "♛", "r": "♜", "b": "♝", "n": "♞", "p": "♟", ".": "·"
    }
    return symbols.get(piece, piece)

# === Streamlit ===

if "board" not in st.session_state:
    st.session_state.board = initial()
    st.session_state.selected = None
    st.session_state.turn_white = True
    st.session_state.message = ""

st.title("♟️ شطرنج Streamlit")

st.write("اختر خانة ثم خانة أخرى لتحريك قطعة. الأبيض أنت. الأسود ذكاء اصطناعي.")

# طباعة اللوحة
for i in range(8):
    cols = st.columns(8)
    for j in range(8):
        piece = st.session_state.board[i][j]
        btn = board_to_unicode(piece)
        if cols[j].button(btn, key=f"{i}-{j}"):
            if st.session_state.selected:
                move = (st.session_state.selected, (i, j))
                if move in generate_moves(st.session_state.board, white_turn=st.session_state.turn_white):
                    st.session_state.board = apply_move(st.session_state.board, move)
                    st.session_state.selected = None
                    st.session_state.turn_white = not st.session_state.turn_white
                    st.session_state.message = ""
                    # AI turn
                    if not st.session_state.turn_white:
                        _, ai_move = minimax(st.session_state.board, 3, -math.inf, math.inf, False)
                        if ai_move:
                            st.session_state.board = apply_move(st.session_state.board, ai_move)
                        st.session_state.turn_white = True
                else:
                    st.session_state.selected = None
                    st.session_state.message = "❌ حركة غير صحيحة"
            else:
                if piece != "." and is_friend(piece, st.session_state.turn_white):
                    st.session_state.selected = (i, j)

if terminal(st.session_state.board):
    st.header("🏁 نهاية اللعبة")
    if not any("k" in row for row in st.session_state.board):
        st.success("🎉 فزت! الملك الأسود تم أسره.")
    elif not any("K" in row for row in st.session_state.board):
        st.error("❌ خسرت. الملك الأبيض تم أسره.")
    st.stop()


if st.session_state.selected:
    st.info(f"اختر خانة للانتقال إليها من {st.session_state.selected}")
if st.session_state.message:
    st.warning(st.session_state.message)