#  Nelson Garrido // Cristobal Herrera
#  This and some edits to the other classses was made by us
#  Minimax with Alpha-Beta pruning used


import othello
import copy
import random
import time

# Heuristic Weights
CORNER_WEIGHT = 1000
MOBILITY_WEIGHT = 100
COIN_WEIGHT = 10

def get_best_move(game_state: othello.OthelloGame, depth: int = 4) -> dict:
    """
    Returns a dictionary with:
    - 'move': selected move (row, col)
    - 'best_moves': list of ALL moves tied for highest score
    - 'score': score
    - 'nodes': nodes explored
    - 'time': time taken
    - 'depth': depth searched
    """
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
        'depth': depth
    }

    if not valid_moves:
        return stats

    # Initialize best_score to negative infinity
    best_score = float('-inf')
    best_moves_list = []

    # Shuffle to ensure randomness if we just pick the first one, 
    # though now we will pick randomly from the list of ties at the end.
    random.shuffle(valid_moves)

    alpha = float('-inf')
    beta = float('inf')

    for move in valid_moves:
        row, col = move
        simulated_game = copy.deepcopy(game_state)
        
        try:
            simulated_game.move(row, col)
            score = minimax(simulated_game, depth - 1, alpha, beta, False, ai_turn, nodes_explored)
            
            # --- LOGIC TO TRACK TIES ---
            if score > best_score:
                best_score = score
                best_moves_list = [move] # Found a new high score, reset list
            elif score == best_score:
                best_moves_list.append(move) # Found a tie, add to list
            
            # Update alpha
            alpha = max(alpha, best_score)
                
        except othello.InvalidMoveException:
            continue

    end_time = time.time()
    
    # Pick one move from the best_moves_list to be the actual move
    selected_move = random.choice(best_moves_list) if best_moves_list else None

    stats['move'] = selected_move
    stats['best_moves'] = best_moves_list # Pass the list to the GUI
    stats['score'] = best_score
    stats['nodes'] = nodes_explored[0]
    stats['time'] = round(end_time - start_time, 4)

    print(f"AI Stats: {stats}")
    return stats


def minimax(game_state: othello.OthelloGame, depth: int, alpha: float, beta: float, 
            maximizing_player: bool, ai_color: str, nodes_count: list) -> float:
    
    nodes_count[0] += 1

    if depth == 0 or game_state.is_game_over():
        return evaluate_board(game_state, ai_color)

    current_turn = game_state.get_turn()
    valid_moves = game_state.get_valid_moves(current_turn)

    if not valid_moves:
        return evaluate_board(game_state, ai_color)

    if maximizing_player:
        max_eval = float('-inf')
        for move in valid_moves:
            simulated_game = copy.deepcopy(game_state)
            simulated_game.move(move[0], move[1])
            eval_score = minimax(simulated_game, depth - 1, alpha, beta, False, ai_color, nodes_count)
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
            eval_score = minimax(simulated_game, depth - 1, alpha, beta, True, ai_color, nodes_count)
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval


def evaluate_board(game_state: othello.OthelloGame, ai_color: str) -> float:
    opponent_color = othello.WHITE if ai_color == othello.BLACK else othello.BLACK
    
    ai_score = game_state.get_total_cells(ai_color)
    op_score = game_state.get_total_cells(opponent_color)
    coin_h = (ai_score - op_score) * COIN_WEIGHT

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
    corner_h = (ai_corners - op_corners) * CORNER_WEIGHT

    ai_moves = len(game_state.get_valid_moves(ai_color))
    op_moves = len(game_state.get_valid_moves(opponent_color))
    mobility_h = (ai_moves - op_moves) * MOBILITY_WEIGHT

    return coin_h + corner_h + mobility_h