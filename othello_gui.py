#  Kevan Hong-Nhan Nguyen 71632979.  ICS 32 Lab sec 9.  Project #5.

import othello
import othello_models
import othello_ai
import tkinter


#### NOTE! You can change the game's settings by going to the menu
#### bar and clicking on
####
#### Game > Game Settings
####
#### Otherwise, the game's settings will remain the same.
####
#### If you want to play a new game, you just click on
#### Game > New Game


# Default / Initial Game Settings
DEFAULT_ROWS = 8
DEFAULT_COLUMNS = 8
DEFAULT_FIRST_PLAYER = othello.BLACK
DEFAULT_TOP_LEFT_PLAYER = othello.WHITE
DEFAULT_VICTORY_TYPE = othello.MOST_CELLS
DEFAULT_GAME_MODE = othello_models.MODE_HUMAN_VS_HUMAN
DEFAULT_AI_STRATEGY = othello_ai.STRATEGY_MINIMAX
DEFAULT_AI_DEPTH = 3

# GUI Constants
BACKGROUND_COLOR = othello_models.BACKGROUND_COLOR
GAME_HEIGHT = 300
GAME_WIDTH = 300

class OthelloGUI:
    def __init__(self):
        # Initial Game Settings
        self._rows = DEFAULT_ROWS
        self._columns = DEFAULT_COLUMNS
        self._first_player = DEFAULT_FIRST_PLAYER
        self._top_left_player = DEFAULT_TOP_LEFT_PLAYER
        self._victory_type = DEFAULT_VICTORY_TYPE
        self._game_mode = DEFAULT_GAME_MODE
        self._ai_strategy = DEFAULT_AI_STRATEGY
        self._ai_depth = DEFAULT_AI_DEPTH


        # Create my othello gamestate here (drawn from the original othello game code)
        self._game_state = othello.OthelloGame(self._rows, self._columns,
                                               self._first_player, self._top_left_player,
                                               self._victory_type)

        # Create AI players (one for each color if needed)
        self._ai_black = othello_ai.OthelloAI(strategy=self._ai_strategy,
                                              max_depth=self._ai_depth,
                                              use_alpha_beta=True)
        self._ai_white = othello_ai.OthelloAI(strategy=self._ai_strategy,
                                              max_depth=self._ai_depth,
                                              use_alpha_beta=True)

        
        # Initialize all my widgets and window here
        self._root_window = tkinter.Tk()
        self._root_window.configure(background = BACKGROUND_COLOR)
        self._board = othello_models.GameBoard(self._game_state, GAME_WIDTH, GAME_HEIGHT, self._root_window)
        self._black_score = othello_models.Score(othello.BLACK, self._game_state, self._root_window)
        self._white_score = othello_models.Score(othello.WHITE, self._game_state, self._root_window)
        self._player_turn = othello_models.Turn(self._game_state, self._root_window)
        self._ai_stats_panel = othello_models.AIStatsPanel(self._root_window)

        # Flag to prevent multiple AI moves at once
        self._ai_thinking = False


        # Bind my game board with these two events.
        self._board.get_board().bind('<Configure>', self._on_board_resized)
        self._board.get_board().bind('<Button-1>', self._on_board_clicked)        


        # Create our menu that can be accessed at the top of the GUI
        self._menu_bar = tkinter.Menu(self._root_window)
        self._game_menu = tkinter.Menu(self._menu_bar, tearoff = 0)
        self._game_menu.add_command(label = 'New Game', command = self._new_game)
        self._game_menu.add_command(label = 'Game Settings', command = self._configure_game_settings)
        self._game_menu.add_separator()
        self._game_menu.add_command(label = 'Exit', command = self._root_window.destroy)
        self._menu_bar.add_cascade(label = 'Game', menu = self._game_menu)

        # Create game mode menu
        self._mode_menu = tkinter.Menu(self._menu_bar, tearoff = 0)
        self._mode_menu.add_command(label = 'Human vs Human', command = lambda: self._change_game_mode(othello_models.MODE_HUMAN_VS_HUMAN))
        self._mode_menu.add_command(label = 'Human vs AI', command = lambda: self._change_game_mode(othello_models.MODE_HUMAN_VS_AI))
        self._mode_menu.add_command(label = 'AI vs AI', command = lambda: self._change_game_mode(othello_models.MODE_AI_VS_AI))
        self._menu_bar.add_cascade(label = 'Game Mode', menu = self._mode_menu)
        

        # Layout all the widgets here using grid layout
        self._root_window.config(menu = self._menu_bar)
        self._black_score.get_score_label().grid(row = 0, column = 0,
                               sticky = tkinter.S)
        self._white_score.get_score_label().grid(row = 0, column = 1,
                               sticky = tkinter.S)
        self._board.get_board().grid(row = 1, column = 0, columnspan = 2,
                                     padx = 50, pady = 10,
                                     sticky = tkinter.N + tkinter.E + tkinter.S + tkinter.W)
        self._player_turn.get_turn_label().grid(row = 2, column = 0, columnspan = 2,
                               padx = 10, pady = 10)

        # Add AI statistics panel on the right side
        self._ai_stats_panel.get_frame().grid(row = 0, column = 2, rowspan = 3,
                                              padx = 10, pady = 10,
                                              sticky = tkinter.N + tkinter.S)


        # Configure the root window's row/column weight (from the grid layout)
        self._root_window.rowconfigure(0, weight = 1)
        self._root_window.rowconfigure(1, weight = 1)
        self._root_window.rowconfigure(2, weight = 1)
        self._root_window.columnconfigure(0, weight = 1)
        self._root_window.columnconfigure(1, weight = 1)
        self._root_window.columnconfigure(2, weight = 0)


    def start(self) -> None:
        ''' Runs the mainloop of the root window '''
        # Check if AI should make the first move
        self._root_window.after(500, self._check_ai_turn)
        self._root_window.mainloop()

    def _change_game_mode(self, new_mode: str) -> None:
        ''' Changes the game mode and starts a new game '''
        self._game_mode = new_mode
        self._new_game()

    def _is_ai_turn(self) -> bool:
        ''' Check if it's currently an AI player's turn '''
        current_turn = self._game_state.get_turn()

        if self._game_mode == othello_models.MODE_HUMAN_VS_HUMAN:
            return False
        elif self._game_mode == othello_models.MODE_AI_VS_AI:
            return True
        elif self._game_mode == othello_models.MODE_HUMAN_VS_AI:
            # In Human vs AI mode, AI is WHITE by default
            return current_turn == othello.WHITE
        return False

    def _check_ai_turn(self) -> None:
        ''' Check if it's AI's turn and make a move if needed '''
        if self._game_state.is_game_over() or self._ai_thinking:
            return

        if self._is_ai_turn():
            self._make_ai_move()
        else:
            # Schedule next check
            self._root_window.after(100, self._check_ai_turn)

    def _make_ai_move(self) -> None:
        ''' Make an AI move and update the board '''
        if self._ai_thinking or self._game_state.is_game_over():
            return

        self._ai_thinking = True
        current_player = self._game_state.get_turn()

        # Select the appropriate AI player
        if current_player == othello.BLACK:
            ai_player = self._ai_black
        else:
            ai_player = self._ai_white

        # Get the best move from AI
        best_move = ai_player.get_best_move(self._game_state, current_player)

        # Update AI statistics panel
        strategy_name = "Minimax (α-β)" if ai_player.use_alpha_beta else "Minimax"
        self._ai_stats_panel.update_stats(ai_player.get_stats(), strategy_name, self._ai_depth)

        # Show AI evaluation on board
        self._board.redraw_board(ai_player.get_stats().moves_evaluated)

        if best_move:
            # Make the move after a short delay to show statistics and visualization
            self._root_window.after(800, lambda: self._execute_ai_move(best_move))
        else:
            # No valid moves, switch turn
            self._ai_thinking = False
            self._game_state.switch_turn()
            self._player_turn.switch_turn(self._game_state)
            self._root_window.after(500, self._check_ai_turn)

    def _execute_ai_move(self, move: tuple) -> None:
        ''' Execute the AI's chosen move '''
        try:
            self._game_state.move(move[0], move[1])
            self._board.update_game_state(self._game_state)
            self._board.redraw_board()
            self._black_score.update_score(self._game_state)
            self._white_score.update_score(self._game_state)

            if self._game_state.is_game_over():
                self._player_turn.display_winner(self._game_state.return_winner())
            else:
                self._player_turn.switch_turn(self._game_state)

            self._ai_thinking = False

            # Check if next turn is also AI
            self._root_window.after(500, self._check_ai_turn)
        except:
            self._ai_thinking = False
            self._root_window.after(500, self._check_ai_turn)


    def _configure_game_settings(self) -> None:
        ''' Pops out an options window to configure the game settings '''
        dialog = othello_models.OptionDialog(self._rows, self._columns,
                                             self._first_player, self._top_left_player,
                                             self._victory_type)
        dialog.show()
        if dialog.was_ok_clicked():
            # If the user clicked 'OK', then change all of the current game
            # settings to whatever the user chose them to be
            self._rows = dialog.get_rows()
            self._columns = dialog.get_columns()
            self._first_player = dialog.get_first_player()
            self._top_left_player = dialog.get_top_left_player()
            self._victory_type = dialog.get_victory_type()

            # Create a new game with these settings now
            self._new_game()
            

    def _new_game(self) -> None:
        ''' Creates a new game with current _game_state settings '''
        self._game_state = othello.OthelloGame(self._rows, self._columns,
                                                   self._first_player, self._top_left_player,
                                                   self._victory_type)
        self._board.new_game_settings(self._game_state)
        self._board.redraw_board()
        self._black_score.update_score(self._game_state)
        self._white_score.update_score(self._game_state)
        self._player_turn.update_turn(self._game_state.get_turn())
        

    def _on_board_clicked(self, event: tkinter.Event) -> None:
        ''' Attempt to play a move on the board if it's valid '''
        # Ignore clicks if it's AI's turn or game is over
        if self._is_ai_turn() or self._game_state.is_game_over() or self._ai_thinking:
            return

        move = self._convert_point_coord_to_move(event.x, event.y)
        row = move[0]
        col = move[1]
        try:
            self._game_state.move(row, col)
            self._board.update_game_state(self._game_state)
            self._board.redraw_board()
            self._black_score.update_score(self._game_state)
            self._white_score.update_score(self._game_state)

            if self._game_state.is_game_over():
                self._player_turn.display_winner(self._game_state.return_winner())
            else:
                self._player_turn.switch_turn(self._game_state)
                # Check if next turn is AI
                self._root_window.after(100, self._check_ai_turn)
        except:
            pass

    def _convert_point_coord_to_move(self, pointx: int, pointy: int) -> None:
        ''' Converts canvas point to a move that can be inputted in the othello game '''
        row = int(pointy // self._board.get_cell_height())
        if row == self._board.get_rows():
            row -= 1
        col = int(pointx // self._board.get_cell_width())
        if col == self._board.get_columns():
            col -= 1
        return (row, col)
        

    def _on_board_resized(self, event: tkinter.Event) -> None:
        ''' Called whenever the canvas is resized '''
        self._board.redraw_board()

if __name__ == '__main__':
    OthelloGUI().start()



