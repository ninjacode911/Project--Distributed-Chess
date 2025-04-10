import pygame
import socket
import threading

# Chess Constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
WHITE = (240, 217, 181)
BROWN = (181, 136, 99)

piece_moves = {
    'P': lambda x, y, nx, ny, board: (nx == x and ny == y - 1 and board[ny][nx] == ' ') or \
                                      (nx == x and ny == y - 2 and y == 6 and board[ny][nx] == ' ' and board[y-1][x] == ' ') or \
                                      (abs(nx - x) == 1 and ny == y - 1 and board[ny][nx].islower()),
    'p': lambda x, y, nx, ny, board: (nx == x and ny == y + 1 and board[ny][nx] == ' ') or \
                                      (nx == x and ny == y + 2 and y == 1 and board[ny][nx] == ' ' and board[y+1][x] == ' ') or \
                                      (abs(nx - x) == 1 and ny == y + 1 and board[ny][nx].isupper()),
    'R': lambda x, y, nx, ny, board: x == nx or y == ny,
    'r': lambda x, y, nx, ny, board: x == nx or y == ny,
    'N': lambda x, y, nx, ny, board: (abs(nx - x), abs(ny - y)) in [(1, 2), (2, 1)],
    'n': lambda x, y, nx, ny, board: (abs(nx - x), abs(ny - y)) in [(1, 2), (2, 1)],
    'B': lambda x, y, nx, ny, board: abs(nx - x) == abs(ny - y),
    'b': lambda x, y, nx, ny, board: abs(nx - x) == abs(ny - y),
    'Q': lambda x, y, nx, ny, board: x == nx or y == ny or abs(nx - x) == abs(ny - y),
    'q': lambda x, y, nx, ny, board: x == nx or y == ny or abs(nx - x) == abs(ny - y),
    'K': lambda x, y, nx, ny, board: max(abs(nx - x), abs(ny - y)) == 1,
    'k': lambda x, y, nx, ny, board: max(abs(nx - x), abs(ny - y)) == 1,
}

def create_board():
    board = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
    board[0] = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
    board[1] = ['p'] * COLS
    board[6] = ['P'] * COLS
    board[7] = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
    return board

class ChessGame:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Distributed Chess Game")
        self.board = create_board()
        self.running = True
        self.clock = pygame.time.Clock()
        self.selected_piece = None

    def draw_board(self):
        for row in range(ROWS):
            for col in range(COLS):
                color = WHITE if (row + col) % 2 == 0 else BROWN
                pygame.draw.rect(self.window, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                piece = self.board[row][col]
                if piece != ' ':
                    font = pygame.font.SysFont(None, 70)
                    text = font.render(piece, True, (100, 100, 100))
                    self.window.blit(text, (col * SQUARE_SIZE + 20, row * SQUARE_SIZE + 10))

    def handle_click(self, pos):
        col = pos[0] // SQUARE_SIZE
        row = pos[1] // SQUARE_SIZE
        if self.selected_piece:
            x, y, piece = self.selected_piece
            if (x, y) != (col, row) and piece_moves.get(piece, lambda *args: False)(x, y, col, row, self.board):
                self.board[y][x] = ' '
                self.board[row][col] = piece
            self.selected_piece = None
        elif self.board[row][col] != ' ':
            self.selected_piece = (col, row, self.board[row][col])

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())
            self.window.fill((0, 0, 0))
            self.draw_board()
            pygame.display.update()
            self.clock.tick(60)
        pygame.quit()

# Server Code
def handle_client(conn):
    try:
        board_state = {"message": "Game running"}
        conn.sendall(str(board_state).encode('utf-8'))
    except:
        pass
    finally:
        conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 5555))
    server.listen(2)
    print("Server started, waiting for connections...")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn,))
        thread.start()

if __name__ == "__main__":
    game = ChessGame()
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    game.run()
