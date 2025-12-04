#  Nelson Garrido // Cristobal Herrera
#  This and some edits to the other classses was made by us
#  Minimax with Alpha-Beta pruning used

import othello
import copy
import random
import time

# Default "Baseline" Weights (The Teacher / Standard AI)
DEFAULT_WEIGHTS = {'corner': 1000, 'mobility': 100, 'coin': 10}

def get_best_move(game_state: othello.OthelloGame, depth: int = 4, weights: dict = None) -> dict:
    """ Returns best move. Accepts optional 'weights' for ML. """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    start_time = time.time()
    nodes_explored = [0]
    
    ai_turn = game_state.get_turn()
    valid_moves = game_state.get_valid_moves(ai_turn)

    stats = {
        'move': None,
        'best_moves': [],
        'score': 0,
        'nodes': 0,
        'time': 0,
        'depth': depth,
        'weights': weights # <--- ADDED: Return weights to be displayed in GUI
    }

    if not valid_moves:
        return stats

    best_score = float('-inf')
    best_moves_list = []
    
    random.shuffle(valid_moves)
    alpha = float('-inf')
    beta = float('inf')

    for move in valid_moves:
        row, col = move
        simulated_game = copy.deepcopy(game_state)
        
        try:
            simulated_game.move(row, col)
            score = minimax(simulated_game, depth - 1, alpha, beta, False, ai_turn, nodes_explored, weights)
            
            if score > best_score:
                best_score = score
                best_moves_list = [move] 
            elif score == best_score:
                best_moves_list.append(move)
            
            alpha = max(alpha, best_score)
                
        except othello.InvalidMoveException:
            continue

    end_time = time.time()
    selected_move = random.choice(best_moves_list) if best_moves_list else None

    stats['move'] = selected_move
    stats['best_moves'] = best_moves_list
    stats['score'] = best_score
    stats['nodes'] = nodes_explored[0]
    stats['time'] = round(end_time - start_time, 4)

    return stats


def minimax(game_state, depth, alpha, beta, maximizing_player, ai_color, nodes_count, weights):
    # ( ... NO CHANGES TO MINIMAX FUNCTION ... )
    # Keep the existing minimax code exactly as it was in your file
    nodes_count[0] += 1

    if depth == 0 or game_state.is_game_over():
        return evaluate_board(game_state, ai_color, weights)

    current_turn = game_state.get_turn()
    valid_moves = game_state.get_valid_moves(current_turn)

    if not valid_moves:
        return evaluate_board(game_state, ai_color, weights)

    if maximizing_player:
        max_eval = float('-inf')
        for move in valid_moves:
            simulated_game = copy.deepcopy(game_state)
            simulated_game.move(move[0], move[1])
            eval_score = minimax(simulated_game, depth - 1, alpha, beta, False, ai_color, nodes_count, weights)
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break 
        return max_eval

    else:
        min_eval = float('inf')
        for move in valid_moves:
            simulated_game = copy.deepcopy(game_state)
            simulated_game.move(move[0], move[1])
            eval_score = minimax(simulated_game, depth - 1, alpha, beta, True, ai_color, nodes_count, weights)
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval

def evaluate_board(game_state: othello.OthelloGame, ai_color: str, weights: dict) -> float:
    # ( ... NO CHANGES TO EVALUATE FUNCTION ... )
    # Keep the existing evaluate code exactly as it was
    opponent_color = othello.WHITE if ai_color == othello.BLACK else othello.BLACK
    
    ai_score = game_state.get_total_cells(ai_color)
    op_score = game_state.get_total_cells(opponent_color)
    coin_h = (ai_score - op_score) * weights['coin']

    rows = game_state.get_rows()
    cols = game_state.get_columns()
    corners = [(0, 0), (0, cols-1), (rows-1, 0), (rows-1, cols-1)]
    ai_corners = 0
    op_corners = 0
    board = game_state.get_board()
    for r, c in corners:
        if board[r][c] == ai_color:
            ai_corners += 1
        elif board[r][c] == opponent_color:
            op_corners += 1
    corner_h = (ai_corners - op_corners) * weights['corner']

    ai_moves = len(game_state.get_valid_moves(ai_color))
    op_moves = len(game_state.get_valid_moves(opponent_color))
    mobility_h = (ai_moves - op_moves) * weights['mobility']

    return coin_h + corner_h + mobility_h


# ---------------------------------------------------------
# UPDATED: BACKGROUND TRAINING LOGIC
# ---------------------------------------------------------

def train_ai(iterations, progress_callback, starting_weights=None):
    """
    Run 'iterations' of training.
    If starting_weights is None, we start with RANDOM values.
    If starting_weights is provided, we Continue Training from there.
    """
    
    # 1. INITIALIZATION LOGIC
    if starting_weights is None:
        # Start completely random (Corrected as requested)
        current_weights = {
            'corner': random.uniform(0, 2000),   # Random start 0 to 2000
            'mobility': random.uniform(0, 500),  # Random start 0 to 500
            'coin': random.uniform(0, 100)       # Random start 0 to 100
        }
    else:
        # Keep training existing brain
        current_weights = starting_weights.copy()
    
    wins = 0

    for i in range(iterations):
        # 2. Create a Challenger (Mutation)
        candidate_weights = current_weights.copy()
        
        # Pick one trait to mutate
        trait = random.choice(list(candidate_weights.keys()))
        mutation = random.randint(-50, 50)
        candidate_weights[trait] += mutation
        
        # 3. Play Match: Candidate (Black) vs Teacher (White)
        winner = play_headless_match(candidate_weights, DEFAULT_WEIGHTS, depth=2)
        
        # 4. Selection
        if winner == othello.BLACK:
            current_weights = candidate_weights
            wins += 1
        
        progress_callback(i + 1, iterations, current_weights, wins)
        
    return current_weights


def play_headless_match(weights_black, weights_white, depth):
    # ( ... NO CHANGES HERE ... )
    game = othello.OthelloGame(8, 8, othello.BLACK, othello.WHITE, othello.MOST_CELLS)
    while not game.is_game_over():
        turn = game.get_turn()
        w = weights_black if turn == othello.BLACK else weights_white
        res = get_best_move(game, depth=depth, weights=w)
        move = res['move']
        if move:
            game.move(move[0], move[1])
        else:
            game.switch_turn()
    return game.return_winner()