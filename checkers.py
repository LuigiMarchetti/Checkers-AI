import pygame
import random

# Definição das cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# CONSTANTES
WIDTH = 700
HEIGHT = 700
MARK_SIZE = 50

class Game:
    def __init__(self):
        self.status = 'playing'
        self.turn = 0  # 0 para jogador humano, 1 para IA
        self.players = ['x', 'o']
        self.selected_token = None
        self.jumping = False
        pygame.display.set_caption("%s's turn" % self.players[self.turn])
        self.game_board = [['x', '-', 'x', '-', 'x', '-', 'x', '-'],
                           ['-', 'x', '-', 'x', '-', 'x', '-', 'x'],
                           ['x', '-', 'x', '-', 'x', '-', 'x', '-'],
                           ['-', '-', '-', '-', '-', '-', '-', '-'],
                           ['-', '-', '-', '-', '-', '-', '-', '-'],
                           ['-', 'o', '-', 'o', '-', 'o', '-', 'o'],
                           ['o', '-', 'o', '-', 'o', '-', 'o', '-'],
                           ['-', 'o', '-', 'o', '-', 'o', '-', 'o']]

    def evaluate_click(self, mouse_pos):
        if self.status == 'playing':
            row, column = get_clicked_row(mouse_pos), get_clicked_column(mouse_pos)
            if self.selected_token:
                move = self.is_valid_move(self.players[self.turn], self.selected_token, row, column)
                if move[0]:
                    self.play(self.players[self.turn], self.selected_token, row, column, move[1])
                elif row == self.selected_token[0] and column == self.selected_token[1]:
                    self.selected_token = None
                    if self.jumping:
                        self.jumping = False
                        self.next_turn()
                else:
                    print('invalid move')
            else:
                if 0 <= row < 8 and 0 <= column < 8 and self.game_board[row][column].lower() == self.players[self.turn]:
                    self.selected_token = [row, column]
        elif self.status == 'game over':
            self.__init__()

    def is_valid_move(self, player, token_location, to_row, to_col):
        from_row, from_col = token_location
        token_char = self.game_board[from_row][from_col]

        # Verifica se o destino está dentro do tabuleiro
        if not (0 <= to_row < 8 and 0 <= to_col < 8):
            return False, None

        if self.game_board[to_row][to_col] != '-':
            return False, None

        # Movimento simples
        if (((token_char.isupper() and abs(from_row - to_row) == 1) or
             (player == 'x' and to_row - from_row == 1) or
             (player == 'o' and from_row - to_row == 1)) and abs(from_col - to_col) == 1) and not self.jumping:
            return True, None

        # Movimento de salto
        if (((token_char.isupper() and abs(from_row - to_row) == 2) or
             (player == 'x' and to_row - from_row == 2) or
             (player == 'o' and from_row - to_row == 2)) and abs(from_col - to_col) == 2):
            jump_row = (to_row - from_row) // 2 + from_row
            jump_col = (to_col - from_col) // 2 + from_col

            if 0 <= jump_row < 8 and 0 <= jump_col < 8 and self.game_board[jump_row][jump_col].lower() not in [player, '-']:
                return True, [jump_row, jump_col]

        return False, None

    def play(self, player, token_location, to_row, to_col, jump):
        from_row, from_col = token_location
        token_char = self.game_board[from_row][from_col]
        self.game_board[to_row][to_col] = token_char
        self.game_board[from_row][from_col] = '-'

        if (player == 'x' and to_row == 7) or (player == 'o' and to_row == 0):
            self.game_board[to_row][to_col] = token_char.upper()

        if jump:
            self.game_board[jump[0]][jump[1]] = '-'
            self.selected_token = [to_row, to_col]
            self.jumping = True
        else:
            self.selected_token = None
            self.next_turn()

        winner = self.check_winner()
        if winner is None:
            pygame.display.set_caption("%s's turn" % self.players[self.turn])
        elif winner == 'draw':
            pygame.display.set_caption("It's a stalemate! Click to start again")
            self.status = 'game over'
        else:
            pygame.display.set_caption("%s wins! Click to start again" % winner)
            self.status = 'game over'

    def next_turn(self):
        self.turn = 1 - self.turn  # Alterna entre 0 e 1
        pygame.display.set_caption("%s's turn" % self.players[self.turn])

    def check_winner(self):
        x = sum([row.count('x') + row.count('X') for row in self.game_board])
        if x == 0:
            return 'o'
        o = sum([row.count('o') + row.count('O') for row in self.game_board])
        if o == 0:
            return 'x'
        if x == 1 and o == 1:
            return 'draw'
        return None

    def draw(self):
        for i in range(9):
            pygame.draw.line(screen, WHITE, [i * WIDTH / 8, 0], [i * WIDTH / 8, HEIGHT], 5)
            pygame.draw.line(screen, WHITE, [0, i * HEIGHT / 8], [WIDTH, i * HEIGHT / 8], 5)
        font = pygame.font.SysFont('Calibri', MARK_SIZE, False, False)
        for r in range(len(self.game_board)):
            for c in range(len(self.game_board[r])):
                mark = self.game_board[r][c]
                if self.players[self.turn] == mark.lower():
                    color = YELLOW
                else:
                    color = WHITE
                if self.selected_token:
                    if self.selected_token[0] == r and self.selected_token[1] == c:
                        color = RED
                if mark != '-':
                    mark_text = font.render(self.game_board[r][c], True, color)
                    x = WIDTH / 8 * c + WIDTH / 16
                    y = HEIGHT / 8 * r + HEIGHT / 16
                    screen.blit(mark_text, [x - mark_text.get_width() / 2, y - mark_text.get_height() / 2])

    def get_valid_moves(self, player):
        moves = []
        for r in range(8):
            for c in range(8):
                if self.game_board[r][c] == player:
                    # Checa movimentos normais e de captura
                    for dr in [-1, -2]:
                        for dc in [-1, 1]:
                            if self.is_valid_move(player, (r, c), r + dr, c + dc)[0]:
                                moves.append(((r, c), (r + dr, c + dc)))
        return moves

    def minimax(self, depth, maximizing_player):
        winner = self.check_winner()
        if winner == 'x':
            return -10 + depth
        elif winner == 'o':
            return 10 - depth
        elif winner == 'draw':
            return 0

        if maximizing_player:
            max_eval = float('-inf')
            for move in self.get_valid_moves('o'):
                from_pos, to_pos = move
                original_piece = self.game_board[from_pos[0]][from_pos[1]]
                self.play('o', from_pos, to_pos[0], to_pos[1], None)
                eval = self.minimax(depth + 1, False)
                self.game_board[from_pos[0]][from_pos[1]] = original_piece
                self.game_board[to_pos[0]][to_pos[1]] = '-'
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.get_valid_moves('x'):
                from_pos, to_pos = move
                original_piece = self.game_board[from_pos[0]][from_pos[1]]
                self.play('x', from_pos, to_pos[0], to_pos[1], None)
                eval = self.minimax(depth + 1, True)
                self.game_board[from_pos[0]][from_pos[1]] = original_piece
                self.game_board[to_pos[0]][to_pos[1]] = '-'
                min_eval = min(min_eval, eval)
            return min_eval

    def best_move(self):
        best_eval = float('-inf')
        best_move = None
        for move in self.get_valid_moves('o'):
            from_pos, to_pos = move
            original_piece = self.game_board[from_pos[0]][from_pos[1]]
            self.play('o', from_pos, to_pos[0], to_pos[1], None)
            eval = self.minimax(0, False)
            self.game_board[from_pos[0]][from_pos[1]] = original_piece
            self.game_board[to_pos[0]][to_pos[1]] = '-'
            if eval > best_eval:
                best_eval = eval
                best_move = move
        return best_move

    def ai_move(self):
        move = self.best_move()
        if move:
            from_pos, to_pos = move
            self.play('o', from_pos, to_pos[0], to_pos[1], None)

        game.turn = 0

def get_clicked_row(mouse_pos):
    x, y = mouse_pos
    return int(y // (HEIGHT / 8))

def get_clicked_column(mouse_pos):
    x, y = mouse_pos
    return int(x // (WIDTH / 8))

# Inicialização do Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
game = Game()

# Loop principal do jogo
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:

            if game.turn == 1:  # Se for a vez da IA
                game.ai_move()
            else:
                game.evaluate_click(event.pos)

    screen.fill(BLACK)
    game.draw()
    pygame.display.flip()
