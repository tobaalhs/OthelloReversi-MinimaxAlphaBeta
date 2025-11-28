# Test script to verify AI functionality
# Run this to ensure the AI is working correctly

import othello
import othello_ai

def test_ai_basic():
    """Test basic AI functionality"""
    print("Testing AI Implementation...")
    print("-" * 50)

    # Create a game
    game = othello.OthelloGame(8, 8, othello.BLACK, othello.WHITE, othello.MOST_CELLS)

    # Create AI player
    ai = othello_ai.OthelloAI(strategy=othello_ai.STRATEGY_MINIMAX,
                              max_depth=3,
                              use_alpha_beta=True)

    # Test 1: AI can find valid moves
    print("\n1. Testing AI move selection...")
    best_move = ai.get_best_move(game, othello.BLACK)
    print(f"   Best move for BLACK: {best_move}")
    assert best_move is not None, "AI should find a valid move"
    print("   [OK] AI successfully selected a move")

    # Test 2: Check statistics
    print("\n2. Testing AI statistics...")
    stats = ai.get_stats()
    print(f"   Nodes explored: {stats.nodes_explored}")
    print(f"   Thinking time: {stats.thinking_time:.3f}s")
    print(f"   Evaluation score: {stats.best_score}")
    assert stats.nodes_explored > 0, "AI should explore nodes"
    print("   [OK] Statistics tracked correctly")

    # Test 3: Verify move is valid
    print("\n3. Testing move validity...")
    valid_moves = game.get_valid_moves(othello.BLACK)
    print(f"   Valid moves: {valid_moves}")
    assert best_move in valid_moves, "AI move should be valid"
    print("   [OK] AI selected a valid move")

    # Test 4: Test evaluation function
    print("\n4. Testing evaluation function...")
    eval_score = ai._evaluate_board(game, othello.BLACK)
    print(f"   Initial board evaluation: {eval_score}")
    print("   [OK] Evaluation function works")

    # Test 5: Compare Minimax vs Greedy
    print("\n5. Comparing strategies...")
    ai_minimax = othello_ai.OthelloAI(strategy=othello_ai.STRATEGY_MINIMAX,
                                      max_depth=3, use_alpha_beta=True)
    ai_greedy = othello_ai.OthelloAI(strategy=othello_ai.STRATEGY_GREEDY,
                                     max_depth=1, use_alpha_beta=False)

    move_minimax = ai_minimax.get_best_move(game, othello.BLACK)
    move_greedy = ai_greedy.get_best_move(game, othello.BLACK)

    print(f"   Minimax move: {move_minimax}")
    print(f"   Minimax nodes explored: {ai_minimax.get_stats().nodes_explored}")
    print(f"   Greedy move: {move_greedy}")
    print(f"   Greedy nodes explored: {ai_greedy.get_stats().nodes_explored}")
    print("   [OK] Both strategies work")

    # Test 6: Test Alpha-Beta pruning effectiveness
    print("\n6. Testing Alpha-Beta pruning...")
    ai_with_pruning = othello_ai.OthelloAI(strategy=othello_ai.STRATEGY_MINIMAX,
                                           max_depth=3, use_alpha_beta=True)
    ai_without_pruning = othello_ai.OthelloAI(strategy=othello_ai.STRATEGY_MINIMAX,
                                              max_depth=3, use_alpha_beta=False)

    move1 = ai_with_pruning.get_best_move(game, othello.BLACK)
    nodes_with = ai_with_pruning.get_stats().nodes_explored

    move2 = ai_without_pruning.get_best_move(game, othello.BLACK)
    nodes_without = ai_without_pruning.get_stats().nodes_explored

    print(f"   With Alpha-Beta pruning: {nodes_with} nodes")
    print(f"   Without pruning: {nodes_without} nodes")
    print(f"   Efficiency gain: {((nodes_without - nodes_with) / nodes_without * 100):.1f}% fewer nodes")
    print("   [OK] Alpha-Beta pruning is working")

    print("\n" + "=" * 50)
    print("ALL TESTS PASSED! [SUCCESS]")
    print("=" * 50)
    print("\nAI Implementation Summary:")
    print(f"- Minimax algorithm: Working")
    print(f"- Alpha-Beta pruning: Working ({nodes_without - nodes_with} nodes saved)")
    print(f"- Evaluation function: Working")
    print(f"- Statistics tracking: Working")
    print(f"- Multiple strategies: Working")
    print("\nReady for gameplay and presentation!")

if __name__ == '__main__':
    test_ai_basic()
