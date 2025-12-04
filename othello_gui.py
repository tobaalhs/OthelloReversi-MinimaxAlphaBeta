#  BASE GAME MADE BY Kevan Hong-Nhan Nguyen
#  Main class, combines game logic and interface

import othello
import othello_models
import othello_ai
import othello_ml
import tkinter

# Default / Initial Game Settings
DEFAULT_ROWS = 8
DEFAULT_COLUMNS = 8
DEFAULT_FIRST_PLAYER = othello.BLACK
DEFAULT_TOP_LEFT_PLAYER = othello.WHITE
DEFAULT_VICTORY_TYPE = othello.MOST_CELLS

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

        # Player settings
        self._black_type = 'Human'
        self._white_type = 'Human'
        
        self._game_state = othello.OthelloGame(self._rows, self._columns,
                                               self._first_player, self._top_left_player,
                                               self._victory_type)

        
        self._root_window = tkinter.Tk()
        self._root_window.configure(background = BACKGROUND_COLOR)
        self._board = othello_models.GameBoard(self._game_state, GAME_WIDTH, GAME_HEIGHT, self._root_window)
        self._black_score = othello_models.Score(othello.BLACK, self._game_state, self._root_window)
        self._white_score = othello_models.Score(othello.WHITE, self._game_state, self._root_window)
        self._player_turn = othello_models.Turn(self._game_state, self._root_window)
        
        self._stats_view = othello_models.StatsView(self._root_window)

        self._board.get_board().bind('<Configure>', self._on_board_resized)
        self._board.get_board().bind('<Button-1>', self._on_board_clicked)        


        self._menu_bar = tkinter.Menu(self._root_window)
        self._game_menu = tkinter.Menu(self._menu_bar, tearoff = 0)
        self._game_menu.add_command(label = 'New Game', command = self._new_game)
        self._game_menu.add_command(label = 'Game Settings', command = self._configure_game_settings)
        self._game_menu.add_separator()
        self._game_menu.add_command(label = 'Exit', command = self._root_window.destroy)
        self._menu_bar.add_cascade(label = 'Game', menu = self._game_menu)
        

        self._root_window.config(menu = self._menu_bar)
        
        # --- LAYOUT: SIDE-BY-SIDE ---
        
        # LEFT SIDE
        self._black_score.get_score_label().grid(row = 0, column = 0, sticky = tkinter.S)
        self._white_score.get_score_label().grid(row = 0, column = 1, sticky = tkinter.S)
        
        self._board.get_board().grid(row = 1, column = 0, columnspan = 2,
                                     padx = 20, pady = 10,
                                     sticky = tkinter.N + tkinter.E + tkinter.S + tkinter.W)
        
        self._player_turn.get_turn_label().grid(row = 2, column = 0, columnspan = 2, padx = 10, pady = 10)
        
        # RIGHT SIDE - Stats View
        self._stats_view.get_frame().grid(row = 0, column = 2, rowspan = 3, 
                                          padx = 20, pady = 10, 
                                          sticky = tkinter.N + tkinter.W)

        self._root_window.rowconfigure(0, weight = 0)
        self._root_window.rowconfigure(1, weight = 1)
        self._root_window.rowconfigure(2, weight = 0)
        
        self._root_window.columnconfigure(0, weight = 1)
        self._root_window.columnconfigure(1, weight = 1)
        self._root_window.columnconfigure(2, weight = 0)


    def start(self) -> None:
        self._root_window.mainloop()


    def _configure_game_settings(self) -> None:
        dialog = othello_models.OptionDialog(self._rows, self._columns,
                                             self._first_player, self._top_left_player,
                                             self._victory_type,
                                             self._black_type, self._white_type)
        dialog.show()
        if dialog.was_ok_clicked():
            self._rows = dialog.get_rows()
            self._columns = dialog.get_columns()
            self._first_player = dialog.get_first_player()
            self._top_left_player = dialog.get_top_left_player()
            self._victory_type = dialog.get_victory_type()
            
            self._black_type = dialog.get_black_type()
            self._white_type = dialog.get_white_type()

            self._new_game()
            

    def _new_game(self) -> None:
        self._game_state = othello.OthelloGame(self._rows, self._columns,
                                                   self._first_player, self._top_left_player,
                                                   self._victory_type)
        self._board.new_game_settings(self._game_state)
        self._board.redraw_board()
        self._black_score.update_score(self._game_state)
        self._white_score.update_score(self._game_state)
        self._player_turn.update_turn(self._game_state.get_turn())

        self._check_for_ai_turn()
        

    def _on_board_clicked(self, event: tkinter.Event) -> None:
        current_turn = self._game_state.get_turn()
        if (current_turn == othello.BLACK and self._black_type in ['Computer', 'ML Player']) or \
           (current_turn == othello.WHITE and self._white_type in ['Computer', 'ML Player']):
            return

        # --- FIX: Use the model's geometry logic ---
        move = self._board.get_clicked_cell(event.x, event.y)
        
        if move:
            row, col = move
            try:
                self._game_state.move(row, col)
                self._post_move_process()
            except:
                pass

    def _on_board_resized(self, event: tkinter.Event) -> None:
        self._board.redraw_board()

    def _post_move_process(self):
        """ Updates UI and handles turn switching logic """
        self._board.update_game_state(self._game_state)
        self._board.redraw_board()
        self._black_score.update_score(self._game_state)
        self._white_score.update_score(self._game_state)
        
        if self._game_state.is_game_over():
            self._player_turn.display_winner(self._game_state.return_winner())
        else:
            self._player_turn.switch_turn(self._game_state)
            self._check_for_ai_turn()

    def _check_for_ai_turn(self):
        """ Checks if the current turn belongs to a Computer or ML Player """
        current_turn = self._game_state.get_turn()

        is_black_ai = (current_turn == othello.BLACK and self._black_type in ['Computer', 'ML Player'])
        is_white_ai = (current_turn == othello.WHITE and self._white_type in ['Computer', 'ML Player'])

        if is_black_ai or is_white_ai:
            self._root_window.after(100, self._calculate_ai_turn)

    def _calculate_ai_turn(self):
        """ Phase 1: AI Thinks and Highlights Choice """
        if self._game_state.is_game_over():
            return

        current_turn = self._game_state.get_turn()
        is_black_computer = (current_turn == othello.BLACK and self._black_type == 'Computer')
        is_white_computer = (current_turn == othello.WHITE and self._white_type == 'Computer')
        is_black_ml = (current_turn == othello.BLACK and self._black_type == 'ML Player')
        is_white_ml = (current_turn == othello.WHITE and self._white_type == 'ML Player')

        if not (is_black_computer or is_white_computer or is_black_ml or is_white_ml):
            return

        # 1. Run AI or ML
        if is_black_ml or is_white_ml:
            ai_result = othello_ml.get_ml_move(self._game_state)
        else:
            ai_result = othello_ai.get_best_move(self._game_state)
        self._stats_view.update_stats(ai_result)

        move = ai_result['move'] 
        best_moves = ai_result['best_moves']
        
        if move:
            # 2. Highlight: Pass both list and single selection
            self._board.set_best_moves(best_moves, move)
            self._board.redraw_board()
            
            # 3. Wait 1 second
            self._root_window.after(1000, lambda: self._execute_ai_move(move))
        else:
            self._execute_ai_move(None)

    def _execute_ai_move(self, move):
        """ Phase 2: Actual Execution """
        # Clear highlights
        self._board.set_best_moves([], None)
        
        if move:
            row, col = move
            try:
                self._game_state.move(row, col)
            except othello.InvalidMoveException:
                pass 

        self._post_move_process()

if __name__ == '__main__':
    OthelloGUI().start()