# Othello AI Implementation - Minimax with Visualization

## Overview

This project implements an intelligent AI opponent for Othello/Reversi using the **Minimax algorithm** with **Alpha-Beta pruning**. The implementation includes real-time visualization of the AI's decision-making process, making it perfect for educational purposes and demonstrating how game-tree search algorithms work.

## Features

### AI Implementation
- **Minimax Algorithm**: Full minimax implementation with configurable search depth (default: 3 levels)
- **Alpha-Beta Pruning**: Optimization that significantly reduces the number of nodes explored
- **Intelligent Evaluation Function**: Considers multiple strategic factors:
  - **Corner Control** (Weight: 100): Corners are the most valuable positions
  - **Edge Control** (Weight: 10): Edge positions provide strategic advantages
  - **Mobility** (Weight: 5): Number of available moves
  - **Piece Count** (Weight: 1): Total pieces on the board

### Game Modes
1. **Human vs Human**: Traditional two-player mode
2. **Human vs AI**: Play against the AI (Human plays Black, AI plays White)
3. **AI vs AI**: Watch two AI players compete

### Real-Time Visualization
- **AI Statistics Panel**: Shows live data during AI thinking:
  - Current strategy (Minimax with α-β pruning)
  - Search depth progression
  - Total nodes explored
  - Best move found
  - Evaluation score
  - Thinking time
  - Complete list of evaluated moves with scores

- **Board Highlighting**: Color-coded visualization of AI-evaluated moves:
  - **Green**: High-value moves (good positions)
  - **Yellow**: Medium-value moves (neutral positions)
  - **Red**: Low-value moves (poor positions)

## File Structure

```
othello-master/
├── othello.py           # Core game logic and rules
├── othello_gui.py       # Main GUI with AI integration
├── othello_models.py    # GUI components and AI stats panel
├── othello_ai.py        # Minimax AI implementation (NEW)
└── README_AI.md         # This documentation file (NEW)
```

## How to Run

### Requirements
- Python 3.x
- tkinter (usually included with Python)

### Running the Game
```bash
python othello_gui.py
```

### Changing Game Mode
1. Launch the game
2. Click on **Game Mode** in the menu bar
3. Select:
   - **Human vs Human** - Traditional two-player
   - **Human vs AI** - Play against the computer
   - **AI vs AI** - Watch AI vs AI match

### Adjusting Game Settings
1. Click **Game > Game Settings**
2. Configure:
   - Board size (4x4 to 16x16)
   - First player
   - Starting position
   - Victory condition (most/least cells)

## AI Implementation Details

### Minimax Algorithm

The Minimax algorithm works by:

1. **Tree Search**: Explores possible future game states up to a specified depth
2. **Recursive Evaluation**: Each node (game state) is evaluated recursively
3. **Maximizing/Minimizing**:
   - AI tries to maximize its score
   - Opponent tries to minimize AI's score
4. **Best Move Selection**: Chooses the move leading to the best guaranteed outcome

### Alpha-Beta Pruning

Alpha-Beta pruning improves performance by:
- Skipping branches that cannot affect the final decision
- Reducing nodes explored by ~50% or more
- Maintaining the same result as pure Minimax
- Enabling deeper search in the same time

### Evaluation Function

The evaluation function scores board positions based on:

```python
score = (corners_diff × 100) +
        (edges_diff × 10) +
        (mobility_diff × 5) +
        (pieces_diff × 1)
```

Where `_diff` represents (AI value - Opponent value)

**Strategic Reasoning:**
- **Corners**: Cannot be flipped, highest priority
- **Edges**: Harder to flip, good defensive positions
- **Mobility**: More moves = more opportunities
- **Pieces**: Important in endgame, less critical early

## Code Architecture

### othello_ai.py

**Main Classes:**
- `OthelloAI`: Main AI player class
  - `get_best_move()`: Returns the best move for current position
  - `_minimax()`: Pure minimax implementation
  - `_minimax_alpha_beta()`: Optimized version with pruning
  - `_evaluate_board()`: Board position evaluation

- `AIStats`: Tracks statistics for visualization
  - Nodes explored
  - Current depth
  - Best move/score
  - Thinking time
  - All evaluated moves

### Integration with GUI (othello_gui.py)

**New Methods:**
- `_change_game_mode()`: Switch between game modes
- `_is_ai_turn()`: Check if AI should move
- `_check_ai_turn()`: Periodic check for AI moves
- `_make_ai_move()`: Get AI decision and update visualization
- `_execute_ai_move()`: Execute the chosen move

**AI Move Flow:**
```
1. Check if AI's turn
2. Get best move from AI (Minimax calculation)
3. Update statistics panel
4. Show move evaluations on board (color-coded)
5. Wait 800ms for visualization
6. Execute the move
7. Update game state
8. Check next turn
```

### Visualization (othello_models.py)

**New Classes:**
- `AIStatsPanel`: Statistics display panel
  - Real-time updates during AI thinking
  - Scrollable list of evaluated moves
  - Color-coded values for easy reading

**Enhanced GameBoard:**
- `_redraw_ai_evaluated_moves()`: Color-codes AI move evaluations
- Dynamic highlighting based on normalized scores

## Performance

### Typical Performance Metrics
- **Depth 3**: ~100-500 nodes explored, 0.1-0.5 seconds
- **Depth 4**: ~1000-5000 nodes explored, 0.5-2 seconds
- **Depth 5**: ~10000+ nodes explored, 2-10 seconds

*Performance varies based on board state and branching factor*

### Alpha-Beta Pruning Impact
- **Without pruning**: Explores all nodes in tree
- **With pruning**: Typically explores 50-75% fewer nodes
- **Same result**: Guaranteed to find same best move

## Educational Value

This implementation is ideal for:

1. **Learning Game AI**: See Minimax algorithm in action
2. **Algorithm Visualization**: Real-time statistics and highlighting
3. **Strategy Analysis**: Compare different evaluation strategies
4. **Performance Study**: Observe pruning effectiveness
5. **Academic Presentations**: Clear code with English comments

## Future Enhancements

Potential improvements:
- [ ] Variable difficulty levels (adjust depth)
- [ ] Iterative deepening for time-controlled search
- [ ] Transposition tables for position caching
- [ ] Opening book for early game
- [ ] Endgame solver for perfect play near end
- [ ] Machine learning evaluation function
- [ ] Slow-motion mode with step-by-step visualization
- [ ] Move hints for human players
- [ ] Game replay and analysis tools

## Comparing Strategies

You can easily add a greedy strategy comparison:

**Greedy Strategy** (already implemented):
- Only looks one move ahead
- Chooses move that captures most pieces immediately
- Fast but short-sighted

**Minimax Strategy**:
- Looks multiple moves ahead
- Considers opponent's responses
- Makes strategic sacrifices for long-term gain

Try both in AI vs AI mode to see the difference!

## Technical Notes

### Threading Consideration
Currently uses `tkinter.after()` for delays, which keeps GUI responsive without true threading. For deeper searches, could implement:
```python
import threading
# Run AI calculation in background thread
# Update GUI from main thread
```

### Game State Copying
Uses `copy.deepcopy()` to simulate moves:
```python
test_game = copy.deepcopy(game_state)
test_game.move(row, col)
# Original game_state unchanged
```

### Move Ordering
Currently evaluates moves in order found. Potential optimization:
- Evaluate corner moves first
- Sort by previous depth scores
- Try best move from previous iteration first

## Credits

- **Original Game**: Kevan Hong-Nhan Nguyen (ICS 32 Lab Project #5)
- **AI Implementation**: Minimax with Alpha-Beta pruning and visualization
- **Algorithm**: Based on classic game theory (Von Neumann, McCarthy)

## License

Educational/Academic use. Code and comments in English for international accessibility.

## Contact

For questions about the AI implementation or suggestions for improvements, please refer to the code comments or academic materials on game-tree search algorithms.

---

**Enjoy playing against the AI! May the best strategist win!** 🎮
