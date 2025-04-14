import pygame
import time
import cv2
from checkers import Board, minimax, WHITE, BLACK, get_all_moves, simulate_move, Piece
import arm
from arm import move_to_square
from gui import draw_board
import json
import numpy as np
import arm

WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Dáma- počítač vs človek')


def square_to_index(square):
    col = ord(square[0]) - ord('a')
    row = 8 - int(square[1])
    return row, col


def load_sqdict(path='sqdict.json'):
    with open(path, 'r') as f:
        raw = json.load(f)
    return {k: np.array(v, dtype=np.int32) for k, v in raw.items()}


def get_piece_centers(frame, lower_hsv, upper_hsv):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    centers = []
    for cnt in contours:
        if cv2.contourArea(cnt) > 100:
            M = cv2.moments(cnt)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                centers.append((cx, cy))
    return centers


def assign_centers_to_squares(centers, sqdict):
    square_map = {square: 0 for square in sqdict}
    for center in centers:
        for square, poly in sqdict.items():
            if cv2.pointPolygonTest(poly, center, False) >= 0:
                square_map[square] += 1
                break
    return square_map


def diff_piece_states(before, after):
    start = None
    end = None
    for sq in before:
        if before[sq] > after[sq]:
            start = sq
        if before[sq] < after[sq]:
            end = sq
    return start, end


def sync_physical_to_board(board, state_map):
    for row in board.board:
        for idx, piece in enumerate(row):
            if piece != 0 and piece.color == BLACK:
                row[idx] = 0

    for square, count in state_map.items():
        if count >= 1:
            r, c = square_to_index(square)
            board.board[r][c] = Piece(r, c, BLACK)


def main():
    clock = pygame.time.Clock()
    board = Board()
    turn = BLACK

    cap = cv2.VideoCapture(0)
    sqdict = load_sqdict()
    state_before = None

    lower_blue = np.array([100, 100, 70])
    upper_blue = np.array([130, 255, 255])

    run = True
    ai_has_moved = False

    while run:
        clock.tick(5)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r and turn == BLACK:
                ret, frame = cap.read()
                if not ret:
                    print("Kamera nedostupná.")
                    continue
                centers = get_piece_centers(frame, lower_blue, upper_blue)
                current_state = assign_centers_to_squares(centers, sqdict)

                if state_before is None:
                    state_before = current_state.copy()
                    sync_physical_to_board(board, current_state)
                    draw_board(WIN, board)
                    print("Prvý snímok uložený a stav synchronizovaný. Pohni figúrkou a znova stlač R.")
                else:
                    start, end = diff_piece_states(state_before, current_state)
                    if start and end:
                        print(f"Zistený pohyb: {start} -> {end}")
                        r1, c1 = square_to_index(start)
                        r2, c2 = square_to_index(end)
                        piece = board.get_piece(r1, c1)
                        if piece and piece.color == BLACK:
                            valid = board.get_valid_moves(piece)
                            move = valid.get((r2, c2))
                            if move is not None:
                                board.move(piece, r2, c2)
                                board.remove(move) 
                                turn = WHITE
                                ai_has_moved = False
                                draw_board(WIN, board)
                            else:
                                print("Neplatný ťah podľa pravidiel dámy.")
                        else:
                            print("Neplatná figúrka.")
                    else:
                        print("Nepodarilo sa rozpoznať platný pohyb.")
                    state_before = None

        if board.winner():
            print("Víťaz:", board.winner())
            time.sleep(3)
            break

        if turn == WHITE and not ai_has_moved:
            _, new_board, ai_move, skipped = minimax(board, 2, True, None)
            board = new_board
            draw_board(WIN, board)

            if ai_move:
                start, end = ai_move
                s_row, s_col = start
                e_row, e_col = end

                start_sq = chr(ord('a') + s_col) + str(8 - s_row)
                end_sq = chr(ord('a') + e_col) + str(8 - e_row)
                print(f"Robot vykonáva ťah: {start_sq} -> {end_sq}")

                if skipped:
                    arm.move_to(start_sq, grasp=True)
                    arm.move_to(end_sq, drop=True)

                    for skipped_piece in skipped:
                        captured_sq = chr(ord('a') + skipped_piece.col) + str(8 - skipped_piece.row)
                        print(f"Robot odnáša vyradenú figúrku z {captured_sq}")
                        arm.move_to(captured_sq, grasp=True)
                        move_to_square(arm.ser, "home", arm.square_map, drop=True, lift_after_drop=False)
                else:
                    arm.move_from_to(start_sq, end_sq)

            ai_has_moved = True
            turn = BLACK




    cap.release()
    pygame.quit()


if __name__ == "__main__":
    arm.init() 
    main()
