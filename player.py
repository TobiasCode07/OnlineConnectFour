import pygame

class Player:
    def __init__(self, p, win, width, height, blue, red, yellow, white, black, cols, rows, square_size, radius, padding, s, label_font):
        self.p = p
        self.win = win
        self.width = width
        self.height = height
        self.blue = blue
        self.red = red
        self.yellow = yellow
        self.white = white
        self.black = black
        self.cols = cols
        self.rows = rows
        self.square_size = square_size
        self.radius = radius
        self.padding = padding
        self.s = s
        self.label_font = label_font
        self.turn = 0
        self.colors = [self.red, self.yellow]
        self.color = self.colors[self.p]
        self.starting_pos = (0, 6)
        self.mouse_pos = None
        self.over = False
        self.create_board()
        self.draw_start_screen()
        self.starting_circle()

    def change_turn(self):
        self.turn = 0 if self.turn == 1 else 1

    def starting_circle(self):
        circle = Circle(self.win, self.colors[self.turn], self.starting_pos[0], self.starting_pos[1], self.square_size, self.radius)
        self.board[self.starting_pos[0]][self.starting_pos[1]] = circle
        circle.draw()

    def get_circle(self, row, col):
        return self.board[row][col]

    def clear(self, row, col):
        pygame.draw.circle(self.win, self.white, (col * self.square_size + self.radius, row * self.square_size + self.radius), self.radius)

    def move(self, circle, row, col):
        r, c = circle.row, circle.col
        self.clear(circle.row, circle.col)
        self.board[circle.row][circle.col], self.board[row][col] = self.board[row][col], self.board[circle.row][circle.col]
        circle.move(row, col)

        return [r, c]

    def get_valid_row(self, col):
        for row in range(self.rows):
            circle = self.get_circle(self.rows - row, col)
            if not circle:
                return self.rows - row

    def check_if_won(self):
        # Check vertical
        for c in range(self.cols):
            for r in range(self.rows - 3):
                if self.board[r + 1][c] and self.board[r + 2][c] and self.board[r + 3][c] and self.board[r + 4][c]:
                    if self.board[r + 1][c].color == self.board[r + 2][c].color == self.board[r + 3][c].color == self.board[r + 4][c].color:
                        return True

        # Check horizontal
        for r in range(self.rows):
            for c in range(self.cols - 3):
                if self.board[r + 1][c] and self.board[r + 1][c + 1] and self.board[r + 1][c + 2] and self.board[r + 1][c + 3]:
                    if self.board[r + 1][c].color == self.board[r + 1][c + 1].color == self.board[r + 1][c + 2].color == self.board[r + 1][c + 3].color:
                        return True

        # Check positively sloped diagonales
        for c in range(self.cols - 3):
            for r in range(self.rows - 3):
                if self.board[r + 1][c] and self.board[r + 2][c + 1] and self.board[r + 3][c + 2] and self.board[r + 4][c + 3]:
                    if self.board[r + 1][c].color == self.board[r + 2][c + 1].color == self.board[r + 3][c + 2].color == self.board[r + 4][c + 3].color:
                        return True

        # Check negatively sloped diagonales
        for c in range(self.cols - 3):
            for r in range(3, self.rows):
                if self.board[r + 1][c] and self.board[r][c + 1] and self.board[r - 1][c + 2] and self.board[r - 2][c + 3]:
                    if self.board[r + 1][c].color == self.board[r][c + 1].color == self.board[r - 1][c + 2].color == self.board[r - 2][c + 3].color:
                        return True

    def draw_frame(self, circle):
        pygame.draw.circle(self.win, self.black,(circle.col * self.square_size + self.radius, circle.row * self.square_size + self.radius),self.radius, 2)

    def remove_frame(self, circle):
        self.clear(circle.row, circle.col)
        circle.draw()

    def clicked(self):
        for col in range(self.cols):
            if self.get_circle(self.starting_pos[0], col):
                circle = self.get_circle(self.starting_pos[0], col)

        if self.mouse_pos[0] == 0:
            if self.mouse_pos == circle.pos and not circle.selected:
                circle.selected = True
                self.draw_frame(circle)
            elif self.mouse_pos == circle.pos and circle.selected:
                row = self.get_valid_row(circle.col)
                if row:
                    starting1 = self.move(circle, row, circle.col)
                    print(f"You made a circle to move to {row},{circle.col}\nSending coordinates to another player...")
                    self.s.sendall(f"Moved: {starting1[0]},{starting1[1]},{row},{circle.col}".encode())
                    if not self.check_if_won():
                        print("Sending move command...")
                        self.s.sendall("MOVE".encode())
                        self.change_turn()
                        self.starting_circle()
                    else:
                        self.over = True
                        self.game_over("won")
            elif self.mouse_pos != circle.pos and circle.selected:
                starting2 = self.move(circle, self.mouse_pos[0], self.mouse_pos[1])
                print(f"You moved a circle to {starting2[0]},{starting2[1]},{self.mouse_pos[0]},{self.mouse_pos[1]}\nSending coordinates to another player...")
                self.s.sendall(f"Moved: {starting2[0]},{starting2[1]},{self.mouse_pos[0]},{self.mouse_pos[1]}".encode())
                self.draw_frame(circle)
            else:
                circle.selected = False
                self.remove_frame(circle)
        else:
            circle.selected = False
            self.remove_frame(circle)

    def game_over(self, result):
        over_text = self.label_font.render(f"You {result}!!!", True, self.black)
        self.win.blit(over_text, ((self.width / 2) - (over_text.get_width() / 2), (self.padding / 2) - (over_text.get_height() / 2)))

    def create_board(self):
        self.board = []
        for row in range(self.rows + 1):
            self.board.append([])
            for col in range(self.cols):
                self.board[row].append(0)

    def draw_start_screen(self):
        self.win.fill(self.white)

        pygame.draw.rect(self.win, self.blue, pygame.Rect(0, self.padding, self.width, self.height - self.padding))

        for row in range(self.rows):
            for col in range(self.cols):
                pygame.draw.circle(self.win, self.white, (col * self.square_size + self.radius, row * self.square_size + self.radius + self.padding), self.radius)

class Circle:
    def __init__(self, win, color, row, col, square_size, radius):
        self.win = win
        self.color = color
        self.row = row
        self.col = col
        self.square_size = square_size
        self.radius = radius
        self.pos = (self.row, self.col)
        self.selected = False
        self.draw()

    def draw(self):
        pygame.draw.circle(self.win, self.color, (self.col * self.square_size + self.radius, self.row * self.square_size + self.radius), self.radius)

    def move(self, row, col):
        self.row = row
        self.col = col
        self.pos = (self.row, self.col)
        self.draw()