import pygame
import time
from checkers import Board, minimax, WHITE, BLACK

WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS


WHITE_COLOR = (255, 255, 255)
BLACK_COLOR = (0, 0, 0)
LIGHT_BROWN = (238, 178, 102)
DARK_BROWN = (89, 44, 0)

pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Dáma- človek vs počítač')

def draw_board(win, board_obj):
    win.fill((0, 0, 0))
    for row in range(ROWS):
        for col in range(COLS):
            color = DARK_BROWN if (row + col) % 2 == 1 else LIGHT_BROWN
            pygame.draw.rect(win, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    for row in range(ROWS):
        for col in range(COLS):
            piece = board_obj.board[row][col]
            if piece != 0:
                center = (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2)
                radius = SQUARE_SIZE // 2 - 10
                if piece.color == WHITE:
                    pygame.draw.circle(win, WHITE_COLOR, center, radius)
                else:
                    pygame.draw.circle(win, BLACK_COLOR, center, radius)

                if piece.king:
                    pygame.draw.circle(win, (255, 215, 0), center, radius // 2, 2)

    pygame.display.update()


def main():
    run = True
    clock = pygame.time.Clock()
    board = Board()
    turn = WHITE
    move_count = 0

    while run:
        clock.tick(5)
        draw_board(WIN, board)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        if board.winner() or move_count > 100:
            break

        _, new_board, _, _ = minimax(board, 2, turn == WHITE, None)
        if new_board is None:
            break

        board = new_board
        turn = BLACK if turn == WHITE else WHITE
        move_count += 1

    draw_board(WIN, board)
    winner = board.winner()
    print("Víťaz:", winner if winner else "Draw")
    time.sleep(5)
    pygame.quit()


if __name__ == "__main__":
    main()
