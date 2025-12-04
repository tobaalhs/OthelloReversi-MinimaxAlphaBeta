import numpy as np
import othello
import copy
import time
import random
import pickle

_model_cache = None

def load_model(model_path='othello_model.pkl'):
    """Load ML model (cached)"""
    global _model_cache
    if _model_cache is None:
        with open(model_path, 'rb') as f:
            _model_cache = pickle.load(f)
    return _model_cache

def board_to_vector(board, player):
    """Convert board to vector from player's perspective"""
    vector = []
    opponent = othello.WHITE if player == othello.BLACK else othello.BLACK

    for row in board:
        for cell in row:
            if cell == player:
                vector.append(1)
            elif cell == opponent:
                vector.append(-1)
            else:
                vector.append(0)
    return np.array(vector, dtype=np.float32)

def get_ml_move(game_state, model_path='othello_model.pkl'):
    """
    ML-based move selection
    Returns same format as othello_ai.get_best_move()
    """
    start_time = time.time()

    try:
        model = load_model(model_path)
    except Exception as e:
        print(f"Error loading ML model: {e}")
        return {
            'move': None,
            'best_moves': [],
            'score': 0,
            'nodes': 0,
            'time': 0,
            'depth': 0
        }

    current_turn = game_state.get_turn()
    valid_moves = game_state.get_valid_moves(current_turn)

    if not valid_moves:
        return {
            'move': None,
            'best_moves': [],
            'score': 0,
            'nodes': 0,
            'time': 0,
            'depth': 0
        }

    move_scores = []

    for move in valid_moves:
        row, col = move
        simulated_game = copy.deepcopy(game_state)

        try:
            simulated_game.move(row, col)
            board_vec = board_to_vector(simulated_game.get_board(), current_turn)
            board_vec = board_vec.reshape(1, -1)

            score = model.predict(board_vec)[0]
            move_scores.append((move, float(score)))

        except Exception:
            move_scores.append((move, -999))

    move_scores.sort(key=lambda x: x[1], reverse=True)

    best_score = move_scores[0][1]
    best_moves = [m for m, s in move_scores if abs(s - best_score) < 0.01]
    selected_move = random.choice(best_moves)

    end_time = time.time()

    stats = {
        'move': selected_move,
        'best_moves': best_moves,
        'score': best_score,
        'nodes': len(valid_moves),
        'time': round(end_time - start_time, 4),
        'depth': 0
    }

    print(f"ML Stats: {stats}")
    return stats
