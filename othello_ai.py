#  Nelson Garrido // Cristobal Herrera
#  New class for everything related to the machine learning side


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
DEFAULT_WEIGHTS = {'corner': 10.0, 'mobility': 1.0, 'coin': 0.1}

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
    """
    Calculates Q(s, a) using Linear Function Approximation.
    Q(s, a) = w1*f1 + w2*f2 ...
    
    Returns: (Total Q value, Dictionary of Feature Values)
    """
    row, col = move
    # Simulate the move to see the resulting state (s')
    sim_game = copy.deepcopy(game_state)
    try:
        sim_game.move(row, col)
    except:
        return -1000, {}

    features = extract_features(sim_game, player_color)
    
    q_value = (weights['corner'] * features['corner'] + 
               weights['mobility'] * features['mobility'] + 
               weights['coin'] * features['coin'])
    
    return q_value, features


def extract_features(game_state, player_color):
    """
    Extracts the feature vector from the board state.
    Features:
    1. Corner: Do we own corners? (High value)
    2. Mobility: How many moves do we have?
    3. Coin: How many pieces do we have?
    """
    opponent = othello.WHITE if player_color == othello.BLACK else othello.BLACK
    
    # Feature 1: Coin Parity (Normalized -1 to 1)
    my_coins = game_state.get_total_cells(player_color)
    op_coins = game_state.get_total_cells(opponent)
    total_coins = my_coins + op_coins
    coin_feat = (my_coins - op_coins) / (total_coins + 1)

    # Feature 2: Mobility (Normalized approx)
    my_moves = len(game_state.get_valid_moves(player_color))
    op_moves = len(game_state.get_valid_moves(opponent))
    total_moves = my_moves + op_moves
    mobility_feat = 0
    if total_moves > 0:
        mobility_feat = (my_moves - op_moves) / total_moves

    # Feature 3: Corners (Most Important)
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
    
    corner_feat = (my_corners - op_corners) # Range -4 to 4

    return {'coin': coin_feat, 'mobility': mobility_feat, 'corner': corner_feat}


# ---------------------------------------------------------
#  Q-LEARNING TRAINING LOOP
# ---------------------------------------------------------

def train_ai(episodes, progress_callback, starting_weights=None):
    """
    Trains the AI by playing against itself (Self-Play).
    Updates weights using the Q-Learning Update Rule (Bellman).
    """
    if starting_weights:
        weights = starting_weights.copy()
    else:
        weights = DEFAULT_WEIGHTS.copy()

    exploration = EXPRATE_START
    wins = 0

    for episode in range(1, episodes + 1):
        start_time = time.time()

        game = othello.OthelloGame(8, 8, othello.BLACK, othello.WHITE, othello.MOST_CELLS)
        
        # History stores tuples: (state_features, reward_received_later)
        # However, for TD(0) we update step-by-step. 
        # For simplicity in this structure, we will use a "Last State" memory.
        
        last_features = {othello.BLACK: None, othello.WHITE: None}

        last_q_value = 0
        
        while not game.is_game_over():
            turn = game.get_turn()
            
            # 1. Choose Action (A) from State (S)
            stats = get_best_move(game, weights, exploration)
            move = stats['move']

            # Capture the Q value from the move decision
            if stats['Q value'] is not None:
                last_q_value = stats['Q value']
            
            if move:
                # Calculate features for Current State S (before move processed completely)
                # Actually, Q(s,a) depends on the state *after* the move in our approximation
                # So we use the features computed inside get_best_move or recompute them
                
                # We execute the move
                game.move(move[0], move[1])
                
                # Now we are in state S'. 
                # We calculate the features of S' relative to the player who just moved.
                current_features = extract_features(game, turn)
                
                # 2. Update Weights for the PREVIOUS move of this player
                # Q(s,a) -> r + gamma * max Q(s', a')
                # Since this is "Approximate", we update weights using Gradient Descent
                
                prev_feat = last_features[turn]
                if prev_feat is not None:
                    # Reward for intermediate steps is usually 0, unless game over
                    reward = 0 
                    
                    # Estimate Q(s') (The value of the state we just landed in)
                    # For current player, the board is now flip-flopped, but extract_features handles logic
                    # We approximate max Q(s', a') simply by the value of current state
                    q_current_state = (weights['corner'] * current_features['corner'] +
                                       weights['mobility'] * current_features['mobility'] +
                                       weights['coin'] * current_features['coin'])
                    
                    q_last_state = (weights['corner'] * prev_feat['corner'] +
                                    weights['mobility'] * prev_feat['mobility'] +
                                    weights['coin'] * prev_feat['coin'])
                    
                    # TD Error = (Reward + Gamma * Estimate_Future) - Estimate_Current
                    target = reward + GAMMA * q_current_state
                    error = target - q_last_state
                    
                    # Update Weights: w = w + alpha * error * feature_value
                    for key in weights:
                        weights[key] += ALPHA * error * prev_feat[key]

                # Store current features to be updated next turn
                last_features[turn] = current_features
                
            else:
                game.switch_turn()

        # 3. Terminal State Update (Game Over)
        winner = game.return_winner()
        for player in [othello.BLACK, othello.WHITE]:
            prev_feat = last_features[player]
            if prev_feat:
                if winner == player:
                    reward = 1.0
                    if player == othello.BLACK: wins += 1 # Track black wins for stats
                elif winner is None:
                    reward = 0.0 # Tie
                else:
                    reward = -1.0 # Loss
                
                # Calculate final Q value (which was the prediction)
                q_last = (weights['corner'] * prev_feat['corner'] +
                          weights['mobility'] * prev_feat['mobility'] +
                          weights['coin'] * prev_feat['coin'])
                
                # Target is just the Reward (no future state)
                error = reward - q_last
                
                for key in weights:
                    weights[key] += ALPHA * error * prev_feat[key]

        # Decay exploration
        if exploration > EXPRATE_MIN:
            exploration *= EXPRATE_DECAY

        # 2. Stop Timer
        end_time = time.time()
        duration = end_time - start_time
            
        # Update GUI periodically
        if episode % 10 == 0 or episode == 1: 
            # updates only every 10 games finished to make it faster
            # updating the gui every time would slow the training
            progress_callback(episode, episodes, weights, f"{exploration:.3f}", duration, last_q_value)
            
    return weights