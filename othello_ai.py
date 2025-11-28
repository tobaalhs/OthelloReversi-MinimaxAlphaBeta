# Othello AI Module - Minimax Algorithm Implementation
# This module provides AI opponents for the Othello game using the Minimax algorithm
# with optional Alpha-Beta pruning and visualization support.

import copy
import time
import othello

# AI Strategy Constants
STRATEGY_MINIMAX = 'minimax'
STRATEGY_GREEDY = 'greedy'

# Evaluation weights for board position scoring
CORNER_WEIGHT = 100      # Corners are highly valuable (permanent positions)
EDGE_WEIGHT = 10         # Edges are moderately valuable
MOBILITY_WEIGHT = 5      # Number of available moves is important
PIECE_COUNT_WEIGHT = 1   # Raw piece count has some value


class AIStats:
    """
    Class to track and store AI decision-making statistics for visualization.
    """
    def __init__(self):
        self.nodes_explored = 0
        self.current_depth = 0
        self.best_move = None
        self.best_score = None
        self.thinking_time = 0.0
        self.moves_evaluated = []  # List of (move, score) tuples

    def reset(self):
        """Reset all statistics for a new move calculation."""
        self.nodes_explored = 0
        self.current_depth = 0
        self.best_move = None
        self.best_score = None
        self.thinking_time = 0.0
        self.moves_evaluated = []


class OthelloAI:
    """
    AI player for Othello game using Minimax algorithm with Alpha-Beta pruning.
    Provides move selection and board evaluation for AI opponents.
    """

    def __init__(self, strategy=STRATEGY_MINIMAX, max_depth=3, use_alpha_beta=True):
        """
        Initialize the AI player.

        Args:
            strategy: AI strategy to use (minimax or greedy)
            max_depth: Maximum search depth for minimax algorithm (3-4 recommended)
            use_alpha_beta: Whether to use alpha-beta pruning optimization
        """
        self.strategy = strategy
        self.max_depth = max_depth
        self.use_alpha_beta = use_alpha_beta
        self.stats = AIStats()

    def get_best_move(self, game_state: othello.OthelloGame, player: str):
        """
        Get the best move for the given player using the selected strategy.

        Args:
            game_state: Current game state
            player: Player color (BLACK or WHITE)

        Returns:
            Tuple (row, col) representing the best move, or None if no moves available
        """
        self.stats.reset()
        start_time = time.time()

        valid_moves = game_state.get_valid_moves(player)

        if not valid_moves:
            return None

        if self.strategy == STRATEGY_GREEDY:
            best_move = self._greedy_move(game_state, player, valid_moves)
        else:  # STRATEGY_MINIMAX
            best_move = self._minimax_move(game_state, player, valid_moves)

        self.stats.thinking_time = time.time() - start_time
        self.stats.best_move = best_move

        return best_move

    def _greedy_move(self, game_state: othello.OthelloGame, player: str, valid_moves: list):
        """
        Greedy strategy: choose the move that flips the most pieces immediately.

        Args:
            game_state: Current game state
            player: Player color
            valid_moves: List of valid moves

        Returns:
            Best move according to greedy strategy
        """
        best_move = None
        best_score = float('-inf')

        for move in valid_moves:
            # Simulate the move
            test_game = self._copy_game_state(game_state)
            test_game.move(move[0], move[1])

            # Evaluate based on piece count
            score = test_game.get_total_cells(player)
            self.stats.nodes_explored += 1
            self.stats.moves_evaluated.append((move, score))

            if score > best_score:
                best_score = score
                best_move = move

        self.stats.best_score = best_score
        return best_move

    def _minimax_move(self, game_state: othello.OthelloGame, player: str, valid_moves: list):
        """
        Minimax strategy: use minimax algorithm to find the best move.

        Args:
            game_state: Current game state
            player: Player color
            valid_moves: List of valid moves

        Returns:
            Best move according to minimax algorithm
        """
        best_move = None
        best_score = float('-inf')
        alpha = float('-inf')
        beta = float('+inf')

        for move in valid_moves:
            # Simulate the move
            test_game = self._copy_game_state(game_state)
            test_game.move(move[0], move[1])

            # Use minimax to evaluate this move
            if self.use_alpha_beta:
                score = self._minimax_alpha_beta(test_game, self.max_depth - 1,
                                                 False, player, alpha, beta)
            else:
                score = self._minimax(test_game, self.max_depth - 1, False, player)

            self.stats.moves_evaluated.append((move, score))

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, best_score)

        self.stats.best_score = best_score
        return best_move

    def _minimax(self, game_state: othello.OthelloGame, depth: int,
                 is_maximizing: bool, ai_player: str):
        """
        Minimax algorithm implementation without alpha-beta pruning.

        Args:
            game_state: Current game state
            depth: Remaining search depth
            is_maximizing: True if maximizing player's turn, False otherwise
            ai_player: The AI player's color

        Returns:
            Evaluation score for this position
        """
        self.stats.nodes_explored += 1
        self.stats.current_depth = self.max_depth - depth

        current_player = game_state.get_turn()

        # Base case: reached max depth or game over
        if depth == 0 or game_state.is_game_over():
            return self._evaluate_board(game_state, ai_player)

        valid_moves = game_state.get_valid_moves(current_player)

        # If no valid moves, switch player and continue
        if not valid_moves:
            test_game = self._copy_game_state(game_state)
            test_game.switch_turn()
            return self._minimax(test_game, depth - 1, not is_maximizing, ai_player)

        if is_maximizing:
            max_eval = float('-inf')
            for move in valid_moves:
                test_game = self._copy_game_state(game_state)
                test_game.move(move[0], move[1])
                eval_score = self._minimax(test_game, depth - 1, False, ai_player)
                max_eval = max(max_eval, eval_score)
            return max_eval
        else:
            min_eval = float('+inf')
            for move in valid_moves:
                test_game = self._copy_game_state(game_state)
                test_game.move(move[0], move[1])
                eval_score = self._minimax(test_game, depth - 1, True, ai_player)
                min_eval = min(min_eval, eval_score)
            return min_eval

    def _minimax_alpha_beta(self, game_state: othello.OthelloGame, depth: int,
                           is_maximizing: bool, ai_player: str, alpha: float, beta: float):
        """
        Minimax algorithm with Alpha-Beta pruning for better performance.

        Args:
            game_state: Current game state
            depth: Remaining search depth
            is_maximizing: True if maximizing player's turn, False otherwise
            ai_player: The AI player's color
            alpha: Alpha value for pruning
            beta: Beta value for pruning

        Returns:
            Evaluation score for this position
        """
        self.stats.nodes_explored += 1
        self.stats.current_depth = self.max_depth - depth

        current_player = game_state.get_turn()

        # Base case: reached max depth or game over
        if depth == 0 or game_state.is_game_over():
            return self._evaluate_board(game_state, ai_player)

        valid_moves = game_state.get_valid_moves(current_player)

        # If no valid moves, switch player and continue
        if not valid_moves:
            test_game = self._copy_game_state(game_state)
            test_game.switch_turn()
            return self._minimax_alpha_beta(test_game, depth - 1, not is_maximizing,
                                           ai_player, alpha, beta)

        if is_maximizing:
            max_eval = float('-inf')
            for move in valid_moves:
                test_game = self._copy_game_state(game_state)
                test_game.move(move[0], move[1])
                eval_score = self._minimax_alpha_beta(test_game, depth - 1, False,
                                                     ai_player, alpha, beta)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval
        else:
            min_eval = float('+inf')
            for move in valid_moves:
                test_game = self._copy_game_state(game_state)
                test_game.move(move[0], move[1])
                eval_score = self._minimax_alpha_beta(test_game, depth - 1, True,
                                                     ai_player, alpha, beta)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval

    def _evaluate_board(self, game_state: othello.OthelloGame, ai_player: str):
        """
        Evaluate the board position for the AI player.
        Higher scores are better for the AI player.

        Evaluation criteria:
        1. Corner control (very important - corners can't be flipped)
        2. Edge control (moderately important)
        3. Mobility (number of valid moves available)
        4. Piece count (less important in early/mid game)

        Args:
            game_state: Current game state
            ai_player: The AI player's color

        Returns:
            Evaluation score (higher is better for AI)
        """
        opponent = othello.BLACK if ai_player == othello.WHITE else othello.WHITE

        # Check if game is over
        if game_state.is_game_over():
            winner = game_state.return_winner()
            if winner == ai_player:
                return 10000  # AI wins
            elif winner == opponent:
                return -10000  # AI loses
            else:
                return 0  # Tie

        score = 0
        board = game_state.get_board()
        rows = game_state.get_rows()
        cols = game_state.get_columns()

        # 1. Corner control
        corners = [
            (0, 0), (0, cols-1),
            (rows-1, 0), (rows-1, cols-1)
        ]
        ai_corners = 0
        opp_corners = 0
        for r, c in corners:
            if board[r][c] == ai_player:
                ai_corners += 1
            elif board[r][c] == opponent:
                opp_corners += 1
        score += (ai_corners - opp_corners) * CORNER_WEIGHT

        # 2. Edge control (excluding corners)
        ai_edges = 0
        opp_edges = 0
        # Top and bottom edges
        for c in range(1, cols-1):
            if board[0][c] == ai_player:
                ai_edges += 1
            elif board[0][c] == opponent:
                opp_edges += 1
            if board[rows-1][c] == ai_player:
                ai_edges += 1
            elif board[rows-1][c] == opponent:
                opp_edges += 1
        # Left and right edges
        for r in range(1, rows-1):
            if board[r][0] == ai_player:
                ai_edges += 1
            elif board[r][0] == opponent:
                opp_edges += 1
            if board[r][cols-1] == ai_player:
                ai_edges += 1
            elif board[r][cols-1] == opponent:
                opp_edges += 1
        score += (ai_edges - opp_edges) * EDGE_WEIGHT

        # 3. Mobility (number of valid moves)
        ai_mobility = len(game_state.get_valid_moves(ai_player))
        opp_mobility = len(game_state.get_valid_moves(opponent))
        score += (ai_mobility - opp_mobility) * MOBILITY_WEIGHT

        # 4. Piece count
        ai_pieces = game_state.get_total_cells(ai_player)
        opp_pieces = game_state.get_total_cells(opponent)
        score += (ai_pieces - opp_pieces) * PIECE_COUNT_WEIGHT

        return score

    def _copy_game_state(self, game_state: othello.OthelloGame):
        """
        Create a deep copy of the game state for simulation.

        Args:
            game_state: Game state to copy

        Returns:
            Deep copy of the game state
        """
        return copy.deepcopy(game_state)

    def get_stats(self):
        """
        Get the current AI statistics.

        Returns:
            AIStats object with current statistics
        """
        return self.stats
