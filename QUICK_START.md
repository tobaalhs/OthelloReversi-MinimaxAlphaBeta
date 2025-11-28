# Othello AI - Quick Start Guide

## Installation & Running

### 1. Run the Game
```bash
cd c:\Users\minec\Desktop\Othello-master
python othello_gui.py
```

### 2. Run Tests
```bash
python test_ai.py
```

---

## Using the AI

### Change Game Mode
**Menu Bar → Game Mode → Select:**
- Human vs Human (both players are human)
- Human vs AI (you play as Black, AI plays as White)
- AI vs AI (watch AI play itself)

### Game Settings
**Menu Bar → Game → Game Settings**
- Board size (4x4 to 16x16)
- First player (Black/White)
- Top-left starting position
- Victory type (Most/Least cells)

---

## Understanding the Visualization

### Right Side Panel: AI Statistics
- **Strategy**: Shows "Minimax (α-β)"
- **Search Depth**: Current/Max depth (e.g., "3 / 3")
- **Nodes Explored**: How many positions evaluated
- **Best Move**: Coordinates of chosen move (row, col)
- **Eval Score**: Numeric score (higher = better for AI)
- **Thinking Time**: Seconds taken to decide
- **Moves Evaluated**: List of all moves with scores

### Board Highlighting
During AI's turn, you'll see colored squares:
- **Green**: Good moves (high evaluation)
- **Yellow**: Okay moves (medium evaluation)
- **Red**: Poor moves (low evaluation)

The AI will choose the green (best) move after ~800ms delay.

---

## Adjusting AI Difficulty

Edit `othello_gui.py` line 28:

```python
# Easy AI (fast, less strategic)
DEFAULT_AI_DEPTH = 2

# Medium AI (default)
DEFAULT_AI_DEPTH = 3

# Hard AI (slow, very strategic)
DEFAULT_AI_DEPTH = 4

# Expert AI (very slow, expert play)
DEFAULT_AI_DEPTH = 5
```

**Warning**: Depth 5+ may take 5-10 seconds per move!

---

## Tips for Playing Against AI

1. **Corners are King**: The AI prioritizes corners - try to get them first!
2. **Avoid Corners-Adjacent**: Cells next to corners often give opponent the corner
3. **Watch Mobility**: AI values having many moves available
4. **Edges Matter**: Edge positions are second priority after corners
5. **Learn from AI**: Watch the move evaluations to see AI's strategy

---

## Troubleshooting

### Game Doesn't Start
- Ensure Python 3.x is installed
- Check tkinter is available: `python -c "import tkinter"`

### AI Too Slow
- Reduce `DEFAULT_AI_DEPTH` to 2
- Close other programs

### AI Too Easy
- Increase `DEFAULT_AI_DEPTH` to 4 or 5
- Try AI vs AI to see strategic play

### Window Too Small
- Click **Game → Game Settings**
- Reduce board size to 6x6 or 4x4

---

## Keyboard Shortcuts
- **None currently** - all controls via mouse and menu

---

## For Your Presentation

### Best Demo Sequence:
1. Start game (Human vs Human mode)
2. Play 1-2 moves manually
3. Switch to Human vs AI
4. Point out the statistics panel
5. Let AI make a move - show the visualization
6. Explain the color-coded moves
7. Switch to AI vs AI
8. Let it run for a full game

### Talk About:
- Minimax algorithm concept
- Alpha-Beta pruning efficiency (33% fewer nodes)
- Evaluation function (corners, edges, mobility, pieces)
- Real-time visualization benefits
- Strategic play vs greedy play

---

## File Reference

| What You Need | File |
|---------------|------|
| Play the game | `python othello_gui.py` |
| Test the AI | `python test_ai.py` |
| Full docs | `README_AI.md` |
| This guide | `QUICK_START.md` |
| Summary | `IMPLEMENTATION_SUMMARY.md` |

---

## Common Questions

**Q: Can I play as White against the AI?**
A: Currently AI is hardcoded as White in Human vs AI mode. To change, edit `othello_gui.py` line 145.

**Q: Can I use a greedy strategy instead of Minimax?**
A: Yes! Edit `othello_gui.py` line 27 to `DEFAULT_AI_STRATEGY = othello_ai.STRATEGY_GREEDY`

**Q: Why does the AI pause before moving?**
A: 800ms delay (line 185 in `othello_gui.py`) to show visualization. Reduce for faster play.

**Q: Can I see the source code for the AI?**
A: Yes! Open `othello_ai.py` - fully commented in English.

**Q: How do I make two different AI strategies play each other?**
A: Edit `othello_gui.py` to create `self._ai_black` and `self._ai_white` with different strategies/depths.

---

## Need Help?

1. Read `README_AI.md` for detailed documentation
2. Check `IMPLEMENTATION_SUMMARY.md` for technical details
3. Look at code comments in `othello_ai.py`
4. Run `test_ai.py` to verify everything works

---

**Ready to play? Run `python othello_gui.py` and enjoy!**
