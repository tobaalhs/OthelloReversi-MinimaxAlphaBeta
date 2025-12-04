#  BASE GAME MADE BY Kevan Hong-Nhan Nguyen
#  This was the one changed the most from the original files
#  Added buttons, fixed resizing, added a thread so the trainings happen without crashing the gui
#  Run this file


import othello
import othello_models
import othello_ai
import tkinter
import threading
import tkinter.simpledialog
import tkinter.messagebox 
import json

# Constants
DEFAULT_ROWS = 8
DEFAULT_COLUMNS = 8
DEFAULT_FIRST_PLAYER = othello.BLACK
DEFAULT_TOP_LEFT_PLAYER = othello.WHITE
DEFAULT_VICTORY_TYPE = othello.MOST_CELLS
BACKGROUND_COLOR = othello_models.BACKGROUND_COLOR
GAME_HEIGHT = 300
GAME_WIDTH = 300
SAVE_FILE = "othello_weights.json"

class OthelloGUI:
    def __init__(self):
        self._rows = DEFAULT_ROWS
        self._columns = DEFAULT_COLUMNS
        self._first_player = DEFAULT_FIRST_PLAYER
        self._top_left_player = DEFAULT_TOP_LEFT_PLAYER
        self._victory_type = DEFAULT_VICTORY_TYPE

        self._black_type = 'Human'
        self._white_type = 'Computer'
        
        self._game_state = othello.OthelloGame(self._rows, self._columns,
                                               self._first_player, self._top_left_player,
                                               self._victory_type)

        # gui stuff (i think we only added/edited some buttons)
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
        # added training option and others
        self._game_menu.add_separator()
        self._game_menu.add_command(label = 'Train Q-Learning', command = self._start_training)
        self._game_menu.add_separator()
        self._game_menu.add_command(label = 'Save Weights', command = self._save_weights)
        self._game_menu.add_command(label = 'Load Weights', command = self._load_weights)
        self._game_menu.add_separator()
        self._game_menu.add_command(label = 'Exit', command = self._root_window.destroy)
        self._menu_bar.add_cascade(label = 'Game', menu = self._game_menu)

        self._root_window.config(menu = self._menu_bar)
        
        # layout
        self._black_score.get_score_label().grid(row = 0, column = 0, sticky = tkinter.S)
        self._white_score.get_score_label().grid(row = 0, column = 1, sticky = tkinter.S)
        self._board.get_board().grid(row = 1, column = 0, columnspan = 2, padx = 20, pady = 10, sticky = tkinter.N + tkinter.E + tkinter.S + tkinter.W)
        self._player_turn.get_turn_label().grid(row = 2, column = 0, columnspan = 2, padx = 10, pady = 10)
        self._stats_view.get_frame().grid(row = 0, column = 2, rowspan = 3, padx = 20, pady = 10, sticky = tkinter.N + tkinter.W)

        self._root_window.rowconfigure(0, weight = 0)
        self._root_window.rowconfigure(1, weight = 1)
        self._root_window.rowconfigure(2, weight = 0)
        self._root_window.columnconfigure(0, weight = 1)
        self._root_window.columnconfigure(1, weight = 1)
        self._root_window.columnconfigure(2, weight = 0)
        #added
        self._learned_weights = None
        self._is_training = False
        self._load_weights(silent=True)

    def start(self): self._root_window.mainloop()

    def _configure_game_settings(self):
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
            

    def _new_game(self):
        self._game_state = othello.OthelloGame(self._rows, self._columns,
                                                   self._first_player, self._top_left_player,
                                                   self._victory_type)
        self._board.new_game_settings(self._game_state)
        self._board.redraw_board()
        self._black_score.update_score(self._game_state)
        self._white_score.update_score(self._game_state)
        self._player_turn.update_turn(self._game_state.get_turn())
        #added
        self._stats_view.reset_weights() 
        w = self._learned_weights if self._learned_weights else othello_ai.DEFAULT_WEIGHTS
        self._stats_view.set_weights(w)
        self._stats_view.update_stats(None)
        self._check_for_ai_turn()
        

    def _on_board_clicked(self, event):
        # if the ai is training or if its an ai vs ai match, then nothing happens when clicking
        if self._is_training: return
        current_turn = self._game_state.get_turn()
        if (current_turn == othello.BLACK and self._black_type == 'Computer') or \
           (current_turn == othello.WHITE and self._white_type == 'Computer'):
            return

        move = self._board.get_clicked_cell(event.x, event.y)
        if move:
            row, col = move
            try:
                self._game_state.move(row, col)
                self._post_move_process()
            except:
                pass

    def _on_board_resized(self, event): self._board.redraw_board()

    def _post_move_process(self):
        self._board.update_game_state(self._game_state)
        self._board.redraw_board()
        self._black_score.update_score(self._game_state)
        self._white_score.update_score(self._game_state)
        
        if self._game_state.is_game_over():
            self._player_turn.display_winner(self._game_state.return_winner())
        else:
            self._player_turn.switch_turn(self._game_state)
            self._check_for_ai_turn() #added

    #new functions 

    def _check_for_ai_turn(self): #self explanatory
        if self._is_training: return
        current_turn = self._game_state.get_turn()
        is_black_ai = (current_turn == othello.BLACK and self._black_type == 'Computer')
        is_white_ai = (current_turn == othello.WHITE and self._white_type == 'Computer')
        if is_black_ai or is_white_ai:
            self._root_window.after(100, self._calculate_ai_turn)

    def _calculate_ai_turn(self):
        if self._game_state.is_game_over(): return
        current_turn = self._game_state.get_turn()
        is_black_ai = (current_turn == othello.BLACK and self._black_type == 'Computer')
        is_white_ai = (current_turn == othello.WHITE and self._white_type == 'Computer')
        if not (is_black_ai or is_white_ai): return

        # set weights, either previous or default if there are none
        w = self._learned_weights if self._learned_weights else othello_ai.DEFAULT_WEIGHTS
        
        # run ai with 0 exploration, so it always choses best moves
        ai_result = othello_ai.get_best_move(self._game_state, weights=w, exploration=0)
        
        # update view
        self._stats_view.set_weights(w)
        self._stats_view.update_stats(ai_result)

        move = ai_result['move'] 
        best_moves = ai_result['best_moves']
        
        if move:
            self._board.set_best_moves(best_moves, move)
            self._board.redraw_board()
            self._root_window.after(1000, lambda: self._execute_ai_move(move))
        else:
            self._execute_ai_move(None)

    def _execute_ai_move(self, move):
        self._board.set_best_moves([], None)
        if move:
            row, col = move
            try:
                self._game_state.move(row, col)
            except othello.InvalidMoveException:
                pass 
        self._post_move_process()

    #  training related

    def _start_training(self): #selecting option to start and asking for number of iterations
        count = tkinter.simpledialog.askinteger("Q-Learning", 
                                                "Enter training iterations (Self-Play):\n"
                                                "Recommended: 1000+",
                                                parent=self._root_window,
                                                minvalue=10, maxvalue=50000)
        if count:
            start_weights = None
            if self._learned_weights:
                use_existing = tkinter.messagebox.askyesno("Training Mode", 
                                "Continue training with existing weights?\n"
                                "YES = Keep current\n"
                                "NO = Reset to Defaults")
                if use_existing:
                    start_weights = self._learned_weights

            # disables the board and starts a thread to do background training so gui doesn't freeze or crash
            self._is_training = True
            self._root_window.title(f"Othello - Q-LEARNING {count} GAMES... (Board Disabled)")
            
            t = threading.Thread(target=self._run_training_background, args=(count, start_weights))
            t.daemon = True 
            t.start()

    def _run_training_background(self, iterations, start_weights): 
        #function called by the thread, updates gui's stats and calls for training function
        def on_progress(current, total, weights, exploration_info, duration, last_q_value):
            self._root_window.after(0, lambda: self._update_training_stats(current, total, weights, exploration_info, duration, last_q_value))

        best_weights = othello_ai.train_ai(iterations, on_progress, starting_weights=start_weights)
        self._learned_weights = best_weights
        
        self._root_window.after(0, self._on_training_complete)

    def _update_training_stats(self, current, total, weights, exploration_info, duration, last_q_value):
        # sends new info to gui
        self._stats_view.set_weights(weights)
        stats_msg = {
            'algorithm': 'Q-Learn',
            'iteration': f'{current}/{total}',
            'time': f'{duration:.4f}',
            'rate': f'{exploration_info}',
            'Q value': last_q_value,
            'move': 'Training...',
            'best_moves': [],
            'weights': weights 
        }
        self._stats_view.update_stats(stats_msg)

    def _on_training_complete(self): # windows with alert to tell you training finished
        self._is_training = False
        self._root_window.title("Othello - Training Complete!")
        print(f"Final Q-Weights: {self._learned_weights}")
        self._save_weights()
        tkinter.messagebox.showinfo("Done", "Q-Learning Complete! Weights saved.")
        self._new_game()

    def _save_weights(self): # saves weights to othello_weights.json
        if not self._learned_weights: return
        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump(self._learned_weights, f)
            print("Weights saved to JSON.")
        except Exception as e:
            print(f"Error saving: {e}")

    def _load_weights(self, silent=False): # loads weights from othello_weights.json
        try:
            with open(SAVE_FILE, 'r') as f:
                self._learned_weights = json.load(f)
            
            self._stats_view.set_weights(self._learned_weights)
            self._stats_view.update_stats(None)

            if not silent:
                tkinter.messagebox.showinfo("Load", "Previous weights loaded successfully!")
                self._new_game()
        except Exception as e:
            self._learned_weights = othello_ai.DEFAULT_WEIGHTS
            if not silent:
                tkinter.messagebox.showerror("Error", "No saved weights found.")

if __name__ == '__main__':
    OthelloGUI().start()