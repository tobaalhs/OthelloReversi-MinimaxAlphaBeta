import othello
import tkinter

# (Colors and Constants remain the same)
BACKGROUND_COLOR = '#696969'
GAME_COLOR = '#006000'
FONT = ('Helvetica', 30)
DIALOG_FONT = ('Helvetica', 20)
STATS_FONT = ('Helvetica', 12)  # Reduced slightly to fit more text
PLAYERS = {othello.BLACK: 'Black', othello.WHITE: 'White'}
VICTORY_TYPES = {othello.MOST_CELLS: 'Most Cells', othello.LEAST_CELLS: 'Least Cells'}

# (GameBoard class remains unchanged - assume it is here)
class GameBoard:
    def __init__(self, game_state, game_width, game_height, root_window):
        self._game_state = game_state
        self._rows = self._game_state.get_rows()
        self._cols = self._game_state.get_columns()
        self._board = tkinter.Canvas(master = root_window, width = game_width, height = game_height, background = GAME_COLOR)
        self._best_moves = []
        self._selected_move = None
        self._side = 0
        self._offset_x = 0
        self._offset_y = 0

    def new_game_settings(self, game_state):
        self._game_state = game_state
        self._rows = self._game_state.get_rows()
        self._cols = self._game_state.get_columns()
        self._best_moves = []
        self._selected_move = None

    def set_best_moves(self, best_moves, selected_move):
        self._best_moves = best_moves
        self._selected_move = selected_move

    def redraw_board(self):
        self._board.delete(tkinter.ALL)
        w = self.get_board_width()
        h = self.get_board_height()
        self._side = min(w, h)
        self._offset_x = (w - self._side) / 2
        self._offset_y = (h - self._side) / 2
        self._redraw_valid_moves()
        self._redraw_cells()
        self._redraw_lines()

    def _redraw_lines(self):
        cell_w = self.get_cell_width()
        cell_h = self.get_cell_height()
        for row in range(1, self._rows):
            y = self._offset_y + row * cell_h
            self._board.create_line(self._offset_x, y, self._offset_x + self._side, y)
        for col in range(1, self._cols):
            x = self._offset_x + col * cell_w
            self._board.create_line(x, self._offset_y, x, self._offset_y + self._side)
        self._board.create_rectangle(self._offset_x, self._offset_y, self._offset_x + self._side, self._offset_y + self._side)

    def _redraw_cells(self):
        for row in range(self._rows):
            for col in range(self._cols):
                if self._game_state.get_board()[row][col] != othello.NONE:
                    self._draw_cell(row, col)
                
    def _draw_cell(self, row, col):
        x1 = self._offset_x + col * self.get_cell_width()
        y1 = self._offset_y + row * self.get_cell_height()
        x2 = x1 + self.get_cell_width()
        y2 = y1 + self.get_cell_height()
        self._board.create_oval(x1, y1, x2, y2, fill = PLAYERS[self._game_state.get_board()[row][col]])                               

    def update_game_state(self, game_state):
        self._game_state = game_state

    def get_cell_width(self): return self._side / self.get_columns()
    def get_cell_height(self): return self._side / self.get_rows()
    def get_board_width(self): return float(self._board.winfo_width())
    def get_board_height(self): return float(self._board.winfo_height())
    
    def get_clicked_cell(self, x, y):
        if x < self._offset_x or x > self._offset_x + self._side: return None
        if y < self._offset_y or y > self._offset_y + self._side: return None
        col = int((x - self._offset_x) // self.get_cell_width())
        row = int((y - self._offset_y) // self.get_cell_height())
        if 0 <= row < self._rows and 0 <= col < self._cols: return (row, col)
        return None

    def get_rows(self): return self._rows
    def get_columns(self): return self._cols
    def get_board(self): return self._board
    
    def _redraw_valid_moves(self):
        valid_moves = self._game_state.get_valid_moves(self._game_state.get_turn())
        for row, col in valid_moves:
            fill_color = 'yellow'
            if (row, col) in self._best_moves: fill_color = 'orange'
            if (row, col) == self._selected_move: fill_color = 'cyan'
            x1 = self._offset_x + col * self.get_cell_width()
            y1 = self._offset_y + row * self.get_cell_height()
            x2 = x1 + self.get_cell_width()
            y2 = y1 + self.get_cell_height()
            self._board.create_rectangle(x1, y1, x2, y2, fill = fill_color, outline = fill_color)


class StatsView:
    def __init__(self, root_window):
        self._frame = tkinter.Frame(master = root_window, background=BACKGROUND_COLOR, padx=10, pady=10)
        
        self._label = tkinter.Label(master = self._frame, 
                                    text = "AI Stats\nWaiting...", 
                                    background=BACKGROUND_COLOR, 
                                    fg='white', 
                                    font=STATS_FONT,
                                    justify=tkinter.LEFT,
                                    width=30,   # Widen for split view
                                    height=30,  # Taller for 2 sets of weights
                                    anchor='nw') 
        self._label.pack(anchor=tkinter.W)
        
        # --- NEW: Store weights separately ---
        self._black_weights = None
        self._white_weights = None

    def get_frame(self):
        return self._frame
    
    # --- NEW: Helper to store weights per player ---
    def set_weights(self, color, weights):
        if color == othello.BLACK:
            self._black_weights = weights
        elif color == othello.WHITE:
            self._white_weights = weights

    def reset_weights(self):
        self._black_weights = None
        self._white_weights = None

    def _format_weights(self, w):
        if not w: return "Human / Default"
        # Abbreviate to fit: C=Corner, M=Mobility, $=Coin
        return f"C:{int(w.get('corner',0))}  M:{int(w.get('mobility',0))}  $:{int(w.get('coin',0))}"

    def update_stats(self, stats: dict):
        if not stats: return
        
        if stats['best_moves']:
            best_moves_str = "\n".join([str(m) for m in stats['best_moves']])
        else:
            best_moves_str = "None"
        
        # Format the dual weight display
        black_str = self._format_weights(self._black_weights)
        white_str = self._format_weights(self._white_weights)

        text = (f"AI STATISTICS\n"
                f"----------------\n"
                f"Depth:   {stats.get('depth', '-')}\n"
                f"Nodes:   {stats.get('nodes', '-')}\n"
                f"Time:    {stats.get('time', '-')}s\n"
                f"Score:   {stats.get('score', 0):.1f}\n\n"
                f"--- WEIGHTS ---\n"
                f"[BLACK]\n{black_str}\n\n"
                f"[WHITE]\n{white_str}\n\n"
                f"----------------\n"
                f"Selected Move:\n{stats['move']}\n\n"
                f"Top Moves:\n{best_moves_str}")
        
        self._label['text'] = text

# (Score, Turn, OptionDialog remain unchanged - copy from previous file)
class Score:
    def __init__(self, color, game_state, root_window):
        self._player = color
        self._score = game_state.get_total_cells(self._player)
        self._score_label = tkinter.Label(master = root_window, text = self._score_text(), background = BACKGROUND_COLOR, fg = PLAYERS[color], font = FONT)
    def update_score(self, game_state):
        self._score = game_state.get_total_cells(self._player)
        self._change_score_text()
    def get_score_label(self): return self._score_label
    def get_score(self): return self._score
    def _change_score_text(self): self._score_label['text'] =  self._score_text()
    def _score_text(self): return PLAYERS[self._player] + ' - ' + str(self._score)

class Turn:
    def __init__(self, game_state, root_window):
        self._player = game_state.get_turn()
        self._turn_label = tkinter.Label(master = root_window, text = self._turn_text(), background = BACKGROUND_COLOR, fg = PLAYERS[self._player], font = FONT)
    def display_winner(self, winner):
        if winner == None:
            victory_text = 'Tie game. Nobody wins!'
            text_color = 'BLACK'
        else:
            victory_text = PLAYERS[winner] + ' player wins!'
            text_color = PLAYERS[winner]
        self._turn_label['text'] = victory_text
        self._turn_label['fg'] = text_color
    def switch_turn(self, game_state):
        self._player = game_state.get_turn()
        self.change_turn_text()
    def change_turn_text(self):
        self._turn_label['text'] = self._turn_text()
        self._turn_label['fg'] = PLAYERS[self._player]
    def get_turn_label(self): return self._turn_label
    def update_turn(self, turn):
        self._player = turn
        self.change_turn_text()
    def _turn_text(self): return PLAYERS[self._player] + " player's turn"

class OptionDialog:
    def __init__(self, current_rows, current_columns, current_first_player, current_top_left_player, current_victory_type, current_black_type, current_white_type):
        self._dialog_window = tkinter.Toplevel()
        self._row_column_option_list = (4, 6, 8, 10 ,12, 14, 16)
        self._player_option_list = ('Black', 'White')
        self._victory_option_list = ('Most Cells', 'Least Cells')
        self._mode_list = ('Play as Black (vs AI)', 'Play as White (vs AI)', 'AI vs AI')

        self._rows = current_rows
        self._columns = current_columns
        self._first_player = current_first_player
        self._top_left_player = current_top_left_player
        self._victory_type = current_victory_type
        
        if current_black_type == 'Human' and current_white_type == 'Computer': self._current_mode = 'Play as Black (vs AI)'
        elif current_black_type == 'Computer' and current_white_type == 'Human': self._current_mode = 'Play as White (vs AI)'
        else: self._current_mode = 'AI vs AI'
        self._black_type = current_black_type 
        self._white_type = current_white_type

        # (Layout code...)
        self._row_frame = tkinter.Frame(master = self._dialog_window)
        tkinter.Label(self._row_frame, text='Rows:', font=DIALOG_FONT).grid(row=0, column=0, sticky=tkinter.E)
        self._rows_var = tkinter.IntVar(value=current_rows)
        tkinter.OptionMenu(self._row_frame, self._rows_var, *self._row_column_option_list).grid(row=0, column=1, sticky=tkinter.W)
        self._row_frame.grid(row=0, column=0, padx=10, pady=5, sticky=tkinter.W)

        self._col_frame = tkinter.Frame(master = self._dialog_window)
        tkinter.Label(self._col_frame, text='Columns:', font=DIALOG_FONT).grid(row=0, column=0, sticky=tkinter.E)
        self._cols_var = tkinter.IntVar(value=current_columns)
        tkinter.OptionMenu(self._col_frame, self._cols_var, *self._row_column_option_list).grid(row=0, column=1, sticky=tkinter.W)
        self._col_frame.grid(row=0, column=1, padx=10, pady=5, sticky=tkinter.W)

        self._first_frame = tkinter.Frame(master = self._dialog_window)
        tkinter.Label(self._first_frame, text='First Player:', font=DIALOG_FONT).grid(row=0, column=0, sticky=tkinter.E)
        self._first_var = tkinter.StringVar(value=PLAYERS[current_first_player])
        tkinter.OptionMenu(self._first_frame, self._first_var, *self._player_option_list).grid(row=0, column=1, sticky=tkinter.W)
        self._first_frame.grid(row=1, column=0, padx=10, pady=5, sticky=tkinter.W)

        self._vic_frame = tkinter.Frame(master = self._dialog_window)
        tkinter.Label(self._vic_frame, text='Victory Type:', font=DIALOG_FONT).grid(row=0, column=0, sticky=tkinter.E)
        self._vic_var = tkinter.StringVar(value=VICTORY_TYPES[current_victory_type])
        tkinter.OptionMenu(self._vic_frame, self._vic_var, *self._victory_option_list).grid(row=0, column=1, sticky=tkinter.W)
        self._vic_frame.grid(row=1, column=1, padx=10, pady=5, sticky=tkinter.W)

        self._mode_frame = tkinter.Frame(master = self._dialog_window)
        tkinter.Label(self._mode_frame, text='Game Mode:', font=DIALOG_FONT).grid(row=0, column=0, sticky=tkinter.E)
        self._mode_var = tkinter.StringVar(value=self._current_mode)
        tkinter.OptionMenu(self._mode_frame, self._mode_var, *self._mode_list).grid(row=0, column=1, sticky=tkinter.W)
        self._mode_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky=tkinter.W)

        self._tl_frame = tkinter.Frame(master = self._dialog_window)
        tkinter.Label(self._tl_frame, text='Top-Left Center:', font=DIALOG_FONT).grid(row=0, column=0, sticky=tkinter.E)
        self._tl_var = tkinter.StringVar(value=PLAYERS[current_top_left_player])
        tkinter.OptionMenu(self._tl_frame, self._tl_var, *self._player_option_list).grid(row=0, column=1, sticky=tkinter.W)
        self._tl_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

        self._button_frame = tkinter.Frame(master = self._dialog_window)
        self._ok_button = tkinter.Button(self._button_frame, text='OK', font=DIALOG_FONT, command=self._on_ok_button)
        self._ok_button.grid(row=0, column=0, padx=10)
        self._cancel_button = tkinter.Button(self._button_frame, text='Cancel', font=DIALOG_FONT, command=self._on_cancel_button)
        self._cancel_button.grid(row=0, column=1, padx=10)
        self._button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        self._ok_clicked = False

    def show(self):
        self._dialog_window.grab_set()
        self._dialog_window.wait_window()
    def was_ok_clicked(self): return self._ok_clicked
    def get_rows(self): return self._rows_var.get()
    def get_columns(self): return self._cols_var.get()
    def get_first_player(self): return self._first_var.get()[0]
    def get_top_left_player(self): return self._tl_var.get()[0]
    def get_victory_type(self): return self._vic_var.get()[0]
    def get_black_type(self): 
        mode = self._mode_var.get()
        if mode == 'Play as Black (vs AI)': return 'Human'
        if mode == 'Play as White (vs AI)': return 'Computer'
        return 'Computer' 
    def get_white_type(self): 
        mode = self._mode_var.get()
        if mode == 'Play as Black (vs AI)': return 'Computer'
        if mode == 'Play as White (vs AI)': return 'Human'
        return 'Computer' 
    def _on_ok_button(self):
        self._ok_clicked = True
        self._dialog_window.destroy()
    def _on_cancel_button(self):
        self._dialog_window.destroy()