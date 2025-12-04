import numpy as np
import othello
import othello_ai
import copy
import random
import pickle
from sklearn.neural_network import MLPRegressor

def board_to_vector(board, player):
    """Convert 8x8 board to 64-element vector from player's perspective"""
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

def generate_training_games(n_games=1000, use_random_opponent=True):
    """Generate training data from games"""
    print(f"Generating {n_games} training games...")
    training_data = []

    for game_num in range(n_games):
        if (game_num + 1) % 100 == 0:
            print(f"  Game {game_num + 1}/{n_games}")

        game = othello.OthelloGame(8, 8, othello.BLACK, othello.WHITE, othello.MOST_CELLS)
        game_positions = []

        while not game.is_game_over():
            current_turn = game.get_turn()
            valid_moves = game.get_valid_moves(current_turn)

            if not valid_moves:
                break

            board_vector = board_to_vector(game.get_board(), current_turn)
            game_positions.append((board_vector, current_turn))

            if use_random_opponent and random.random() > 0.5:
                move = random.choice(valid_moves)
            else:
                ai_result = othello_ai.get_best_move(game, depth=2)
                move = ai_result['move']
                if not move:
                    move = random.choice(valid_moves)

            game.move(move[0], move[1])

        winner = game.return_winner()

        if winner == othello.BLACK:
            outcome = 1
        elif winner == othello.WHITE:
            outcome = -1
        else:
            outcome = 0

        for board_vec, player in game_positions:
            if player == othello.WHITE:
                outcome_adjusted = -outcome
            else:
                outcome_adjusted = outcome
            training_data.append((board_vec, outcome_adjusted))

    print(f"Generated {len(training_data)} training positions")
    return training_data

def create_model():
    """Create neural network model using scikit-learn"""
    model = MLPRegressor(
        hidden_layer_sizes=(128, 64),
        activation='relu',
        solver='adam',
        max_iter=100,
        random_state=42,
        verbose=True,
        early_stopping=True,
        validation_fraction=0.2
    )
    return model

def train_model(n_games=3000):
    """Generate data and train model"""
    training_data = generate_training_games(n_games)

    X = np.array([x[0] for x in training_data])
    y = np.array([x[1] for x in training_data], dtype=np.float32)

    print(f"\nTraining data shape: X={X.shape}, y={y.shape}")
    print("\nCreating and training model...")

    model = create_model()
    model.fit(X, y)

    with open('othello_model.pkl', 'wb') as f:
        pickle.dump(model, f)

    print("\nModel saved as 'othello_model.pkl'")
    return model

if __name__ == '__main__':
    print("Starting ML training for Othello...")
    print("This will take several minutes...\n")

    model = train_model(n_games=3000)

    print("\nTraining complete!")
    print(f"Model score: {model.best_validation_score_ if hasattr(model, 'best_validation_score_') else 'N/A'}")
