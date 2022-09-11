import socket
from _thread import *

server = socket.gethostname()
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(e)

print("[SERVER STARTED]\nWaiting for connection...")
s.listen()

def _send(message):
    for client in clients:
        client.sendall(message.encode())

def _send_to_other(message, client_sending):
    clients[0 if client_sending == 1 else 1].sendall(message)

def threaded_client(conn, player):
    start_data = f"Player: {player}"
    print(f"Sending: {start_data}")
    conn.sendall(start_data.encode())
    while True:
        try:
            data = conn.recv(2048).decode()
            if data:
                if data == "READY":
                    print(f"Player {player} is ready to play")
                    players[player][1] = True

                    if players[0][1] and players[1][1]:
                        print("All players are ready to play\nSending play command...")
                        _send("PLAY")
                elif data == "KILL":
                    print(f"Received kill command from player {player}\nEnding communication...")
                    break
                elif "Moved:" in data:
                    _send_to_other(data.encode(), player)
                elif data == "SURRENDER":
                    print(f"Received surrender command from player {player}\nSending it to other player...")
                    _send_to_other(data.encode(), player)
                elif data == "MOVE":
                    print(f"Received move command from player {player}\nSending it to other player...")
                    _send_to_other(data.encode(), player)
                elif data == "DRAW":
                    print(f"Received draw command from player {player}\nSending it to other player...")
                    _send_to_other(data.encode(), player)
            else:
                print(f"Error while receiving data from player {player}\nDisconnecting...")
                break
        except:
            break

    print(f"Error while communicating with the player {player}\nClosing connection...")
    print(f"Removing player {player} from players list...")
    players[player][0] = False
    players[player][1] = False
    clients.remove(conn)
    conn.close()

players = [[False, False], [False, False]]
clients = []
while True:
    conn, addr = s.accept()

    print(f"{addr} connected to the server")

    if players[0][0] and players[1][0]:
        print("Too many players\nSending a quit command")
        conn.sendall("QUIT".encode())
    else:
        for i in range(len(players)):
            if not players[i][0]:
                start_new_thread(threaded_client, (conn, i))
                players[i][0] = True
                clients.append(conn)
                break