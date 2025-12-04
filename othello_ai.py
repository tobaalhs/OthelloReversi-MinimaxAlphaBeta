#  Nelson Garrido // Cristobal Herrera
#  New file for everything related to the machine learning side


import othello
import random
import copy
import time

# constants
ALPHA = 0.01  # learning rate
GAMMA = 0.90  # discount factor (how much value future vs immediate rewards)
# exploration rate (chance of doing a random move)
EXPRATE_START = 1.0
EXPRATE_MIN = 0.1
EXPRATE_DECAY = 0.995

# Default starting weights if no previous values, these will be adjusted while learning
DEFAULT_WEIGHTS = {'corner': 10.0, 'mobility': 1.0, 'pieces': 0.1}

def get_best_move(game_state: othello.OthelloGame, weights: dict = None, exploration: float = 0) -> dict:
    if weights is None: weights = DEFAULT_WEIGHTS
    
    start_time = time.time()
    turn = game_state.get_turn()
    valid_moves = game_state.get_valid_moves(turn)

    stats = {
        'move': None,
        'best_moves': [],
        'Q value': 0,
        'time': 0,
        'weights': weights,
    }

    if not valid_moves:
        return stats

    # exploration vs exploitation
    # if random < exploration = random move
    if random.random() < exploration:
        selected_move = random.choice(valid_moves)
        q_val, _ = calculate_q_value(game_state, selected_move, turn, weights) #just for display
        stats['move'] = selected_move
        stats['Q value'] = q_val
        return stats
    # else pick highest Q value move (exploitation)
    best_score = float('-inf')
    best_moves = []

    # finds highest Q values from valid moves
    for move in valid_moves:
        q_val, _ = calculate_q_value(game_state, move, turn, weights)
        if q_val > best_score:
            best_score = q_val
            best_moves = [move]
        elif q_val == best_score:
            best_moves.append(move)

    # chooses a random move from moves with same Q value
    selected_move = random.choice(best_moves) if best_moves else None 

    end_time = time.time()
    stats['move'] = selected_move
    stats['best_moves'] = best_moves
    stats['Q value'] = best_score
    stats['time'] = round(end_time - start_time, 4)
    
    return stats


def calculate_q_value(game_state, move, player_color, weights):
    # Q = wc*fc + wm*fm + wp*fp
    # f being the information after the move (feature values)

    row, col = move
    # simulate the move to see the resulting state
    sim_game = copy.deepcopy(game_state)
    try:
        sim_game.move(row, col)
    except:
        return -1000, {}

    features = extract_features(sim_game, player_color)
    
    q_value = (weights['corner'] * features['corner'] + 
               weights['mobility'] * features['mobility'] + 
               weights['pieces'] * features['pieces'])
    
    return q_value, features


def extract_features(game_state, player_color):
    # calculation of the feature values
    opponent = othello.WHITE if player_color == othello.BLACK else othello.BLACK
    
    # Pieces (Normalized)
    my_pieces = game_state.get_total_cells(player_color)
    op_pieces = game_state.get_total_cells(opponent)
    total_pieces = my_pieces + op_pieces
    pieces_feat = 0
    if total_pieces > 0:
        pieces_feat = (my_pieces - op_pieces) / total_pieces

    # Mobility (Normalized)
    my_moves = len(game_state.get_valid_moves(player_color))
    op_moves = len(game_state.get_valid_moves(opponent))
    total_moves = my_moves + op_moves
    mobility_feat = 0
    if total_moves > 0:
        mobility_feat = (my_moves - op_moves) / total_moves

    # Corners (Most Important, normalized)
    rows = game_state.get_rows()
    cols = game_state.get_columns()
    corners = [(0, 0), (0, cols-1), (rows-1, 0), (rows-1, cols-1)]
    my_corners = 0
    op_corners = 0
    board = game_state.get_board()
    
    for r, c in corners:
        if board[r][c] == player_color:
            my_corners += 1
        elif board[r][c] == opponent:
            op_corners += 1
    
    corner_feat = (my_corners - op_corners)/4

    return {'pieces': pieces_feat, 'mobility': mobility_feat, 'corner': corner_feat}


# TRAINING LOOP
def train_ai(iterations, progress_callback, starting_weights=None):
    # ai plays agains itself and alters the weights, which then the opposite ai (the same) uses intstantly and alters as well

    if starting_weights:
        weights = starting_weights.copy()
        exploration = 0.35 #already trained, so lower randomness to not disrupt previous learnings but still having chance to explore
    else:
        weights = DEFAULT_WEIGHTS.copy()
        exploration = EXPRATE_START #knows nothing

    for iteration in range(1, iterations + 1):
        start_time = time.time()

        game = othello.OthelloGame(8, 8, othello.BLACK, othello.WHITE, othello.MOST_CELLS)
        
        last_features = {othello.BLACK: None, othello.WHITE: None}
        last_q_value = 0
        
        # when game is not finished, play the game, store current state, calculate error and update weights
        while not game.is_game_over():
            turn = game.get_turn()
            
            # play the game basically
            stats = get_best_move(game, weights, exploration)
            move = stats['move']

            if stats['Q value'] is not None:
                last_q_value = stats['Q value']
            
            if move:                
                # execute the move
                game.move(move[0], move[1])

                current_features = extract_features(game, turn)
                
                prev_feat = last_features[turn]
                if prev_feat is not None:
                    # all this is better explained in the report tbh
                    q_current_state = (weights['corner'] * current_features['corner'] +
                                       weights['mobility'] * current_features['mobility'] +
                                       weights['pieces'] * current_features['pieces'])
                    
                    q_last_state = (weights['corner'] * prev_feat['corner'] +
                                    weights['mobility'] * prev_feat['mobility'] +
                                    weights['pieces'] * prev_feat['pieces'])
                    
                    # Error = (Gamma * Estimate_Future) - Estimate_Current
                    error = (GAMMA * q_current_state) - q_last_state
                    
                    # update Weights: w = w + (alpha * error * feature_value)
                    for key in weights:
                        weights[key] += ALPHA * error * prev_feat[key]

                # store current features for next turn
                last_features[turn] = current_features
                
            else:
                game.switch_turn()

        # when game finishes, do the same but we add the reward to it, error's formula changes slightly
        winner = game.return_winner()
        for player in [othello.BLACK, othello.WHITE]:
            prev_feat = last_features[player]
            if prev_feat:
                if winner == player:
                    reward = 1.0 # Win
                elif winner is None:
                    reward = 0.0 # Tie
                else:
                    reward = -1.0 # Loss

                q_last = (weights['corner'] * prev_feat['corner'] +
                          weights['mobility'] * prev_feat['mobility'] +
                          weights['pieces'] * prev_feat['pieces'])
                
                # changed error
                error = reward - q_last
                
                for key in weights: # same weight update as before
                    weights[key] += ALPHA * error * prev_feat[key]

        # lower exploration
        if exploration > EXPRATE_MIN:
            exploration *= EXPRATE_DECAY

        # end time
        end_time = time.time()
        duration = end_time - start_time
            
        # Update GUI every 10 finished games, updating the gui every time would slow the training
        if iteration % 10 == 0 or iteration == 1: 
            progress_callback(iteration, iterations, weights, f"{exploration:.3f}", duration, last_q_value)
            
    return weights