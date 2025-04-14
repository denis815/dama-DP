import copy

ROWS, COLS = 8, 8
WHITE = "white"
BLACK = "black"


class Piece:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False

    def make_king(self):
        self.king = True

    def move(self, row, col):
        self.row = row
        self.col = col

    def __repr__(self):
        return f"{'W' if self.color == WHITE else 'B'}{'K' if self.king else ''}"


class Board:
    def __init__(self):
        self.board = []
        self.white_left = self.black_left = 12
        self.create_board()

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if (row + col) % 2 == 1:
                    if row < 3:
                        self.board[row].append(Piece(row, col, BLACK))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, WHITE))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)

    def get_piece(self, row, col):
        return self.board[row][col]

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = 0, piece
        piece.move(row, col)
        if (row == 0 and piece.color == WHITE) or (row == ROWS - 1 and piece.color == BLACK):
            piece.make_king()

    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece != 0:
                if piece.color == WHITE:
                    self.white_left -= 1
                else:
                    self.black_left -= 1

    def get_all_pieces(self, color):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    pieces.append(piece)
        return pieces

    def get_valid_moves(self, piece):
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.color == WHITE or piece.king:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
        if piece.color == BLACK or piece.king:
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))

        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break

            current = self.board[r][left]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last

                if last:
                    if step == -1:
                        row = max(r - 3, -1)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, left - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, left + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]
            left -= 1
        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break

            current = self.board[r][right]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last

                if last:
                    if step == -1:
                        row = max(r - 3, -1)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, right - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, right + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]
            right += 1
        return moves

    def winner(self):
        if self.white_left <= 0:
            return BLACK
        elif self.black_left <= 0:
            return WHITE
        return None


def minimax(position, depth, max_player, game):
    if depth == 0 or position.winner() is not None:
        return evaluate(position), position, None, []

    if max_player:
        max_eval = float('-inf')
        best_move = None
        best_action = None
        best_skipped = []
        for move, start, end, skipped in get_all_moves(position, WHITE, game):
            evaluation, _, _, _ = minimax(move, depth - 1, False, game)
            if evaluation > max_eval:
                max_eval = evaluation
                best_move = move
                best_action = (start, end)
                best_skipped = skipped
        return max_eval, best_move, best_action, best_skipped

    else:
        min_eval = float('inf')
        best_move = None
        best_action = None
        best_skipped = []
        for move, start, end, skipped in get_all_moves(position, BLACK, game):
            evaluation, _, _, _ = minimax(move, depth - 1, True, game)
            if evaluation < min_eval:
                min_eval = evaluation
                best_move = move
                best_action = (start, end)
                best_skipped = skipped
        return min_eval, best_move, best_action, best_skipped


def evaluate(board):
    return board.white_left - board.black_left


def simulate_move(piece, move, board, skipped):
    board.move(piece, move[0], move[1])
    if skipped:
        board.remove(skipped)
    return board


def get_all_moves(board, color, game):
    moves = []
    for piece in board.get_all_pieces(color):
        valid_moves = board.get_valid_moves(piece)
        for move, skipped in valid_moves.items():
            temp_board = copy.deepcopy(board)
            temp_piece = temp_board.get_piece(piece.row, piece.col)
            new_board = simulate_move(temp_piece, move, temp_board, skipped)
            moves.append((new_board, (piece.row, piece.col), move, skipped))
    return moves

