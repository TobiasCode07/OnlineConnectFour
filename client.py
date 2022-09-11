import socket
from _thread import *
import pygame
from player import Player
from tkinter import *
from tkinter import messagebox

pygame.init()

server = socket.gethostname()
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.connect((server, port))
except socket.error as e:
    print(e)

global playing, waiting, p, win, gui_open, running, over, surrendered, label_font, counter, drew
waiting = False
playing = False
running = True
over = False
surrendered = False
drew = False
label_font = pygame.font.Font("freesansbold.ttf", 50)
counter = 0

ICON = "icon.png"
WIDTH = 700
HEIGHT = 700
PADDING = 100
ROWS = 6
COLS = 7
RADIUS = (WIDTH / COLS) / 2 - 2
SQUARE_SIZE = WIDTH / COLS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

def get_mouse_pos(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return (int(row), int(col))

def play(player):
    global waiting, playing, p, win, running, over, surrendered, label_font, counter, drew

    win = pygame.display.set_mode((WIDTH, HEIGHT))
    win.fill(WHITE)
    pygame.display.set_caption(f"Online Connect Four - Player {player}")
    timer = pygame.time.Clock()

    while running:
        timer.tick(60)

        if not waiting and not playing and not over:
            play_rect = pygame.draw.rect(win, GREEN, [(WIDTH / 2) - (300 / 2), (HEIGHT / 2) - (100 / 2), 300, 100])
            play_text = label_font.render("Play!", True, BLACK)
            win.blit(play_text, ((WIDTH / 2) - (play_text.get_width() / 2), (HEIGHT / 2) - (play_text.get_height() / 2)))
        elif waiting and not playing and not over:
            win.fill(WHITE)
            waiting_text = label_font.render("Waiting for other player...", True, BLACK)
            win.blit(waiting_text, ((WIDTH / 2) - (waiting_text.get_width() / 2), (HEIGHT / 2) - (waiting_text.get_height() / 2)))
        elif over:
            if drew:
                p.game_over("drew")
            elif not surrendered:
                p.game_over("lost")
            elif surrendered:
                p.game_over("won")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if playing:
                    print(playing, over, p.over)
                    if not over and not p.over:
                        root = Tk()
                        root.withdraw()
                        reply = messagebox.askokcancel(f"Online game test - Player {player}", "The game is still running\nDo you want to surrender?")
                        print(f"You replied {reply} to a question box")
                        if reply:
                            s.sendall("SURRENDER".encode())
                            p.game_over("lost")
                            running = False
                            break
                    else:
                        running = False
                        playing = False
                        break
                else:
                    running = False
                    playing = False
                    break
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not waiting:
                    if play_rect.collidepoint(event.pos):
                        print("Sending waiting command...")
                        s.sendall("READY".encode())
                        waiting = True
                if not over and playing:
                    if player == p.turn:
                        p.mouse_pos = get_mouse_pos(pygame.mouse.get_pos())
                        p.clicked()

        pygame.display.flip()

    print("Closed gui\nSending kill command...")
    s.sendall("KILL".encode())

player = None
while True:
    try:
        data = s.recv(2048).decode()
        if data:
            print(f"Received: {data}")
            if "Player:" in data:
                player = int(data.split(" ")[1])
                print(f"You're player {str(player)}")
                start_new_thread(play, (player, ))
            elif data == "QUIT":
                print("Received a quit command")
                break
            elif data == "PLAY":
                print("Received play command")
                win.fill(WHITE)
                p = Player(player, win, WIDTH, HEIGHT, BLUE, RED, YELLOW, WHITE, BLACK, COLS, ROWS, SQUARE_SIZE, RADIUS, PADDING, s, label_font)
                playing = True
            elif "Moved:" in data:
                print(f"Received opponent move: {data}")
                starting1, starting2, ending1, ending2 = data.split("Moved: ")[1].split(",")
                circle = p.get_circle(int(starting1), int(starting2))
                p.move(circle, int(ending1), int(ending2))
                print("Done opponent move")
                if p.check_if_won():
                    print("You lost!!!")
                    over = True
                    playing = False
            elif data == "SURRENDER":
                print("Opponent surrendered\nYou won the game!")
                over = True
                surrendered = True
                playing = False
            elif data == "MOVE":
                print("Received move command\nChanging turn...\nAdding one move to counter...")
                counter += 1
                print(f"Move counter is: {counter}")
                if counter == (ROWS * COLS) / 2 and player == 0:
                    print("You drew!!!\nSending draw command to other player...")
                    s.sendall("DRAW".encode())
                    p.game_over("drew")
                    drew = True
                    over = True
                    playing = False
                else:
                    p.change_turn()
                    p.starting_circle()
            elif data == "DRAW":
                p.clear(p.starting_pos[0], p.starting_pos[1])
                print("You drew!!!")
                p.game_over("drew")
                drew = True
                over = True
                playing = False
        else:
            print("Error while receiving data")
            break
    except Exception as exc:
        print(exc)
        break

print("Closing connection...")
running = False
s.close()