import socket
import random
import os

host = "0.0.0.0"
port = 7777
banner = """
== Guessing Game v1.0 == """

difficulty_levels = {
    'a': (1, 50),   
    'b': (1, 100),  
    'c': (1, 500)   
}

user_data_file = "user_data.txt"

def generate_random_int(low, high):
    return random.randint(low, high)

def update_user_score(username, score, difficulty):
    user_data = {}
    if os.path.exists(user_data_file):
        with open(user_data_file, "r") as file:
            for line in file:
                name, prev_score, prev_difficulty = line.strip().split(",")
                user_data[name] = (int(prev_score), prev_difficulty)

    user_data[username] = (score, difficulty)

    with open(user_data_file, "w") as file:
        for name, (prev_score, prev_difficulty) in user_data.items():
            file.write(f"{name},{prev_score},{prev_difficulty}\n")

def handle_client_connection(conn, addr):
    try:
        conn.sendall(banner.encode())

        while True: 
            username = conn.recv(1024).decode().strip()
            difficulty_choice = conn.recv(1024).decode().strip().lower()
            
            conn.sendall(b"Do you want to play again? (yes/no): ")
            play_again_choice = conn.recv(1024).decode().strip().lower()
            if play_again_choice != "yes":
                break  
    except ConnectionResetError:
        print("Connection reset by the client.")
    except ConnectionAbortedError:
        print("Connection aborted by the client.")

    conn.close()
    print(f"Connection with {addr} closed")

def send_leaderboard(conn):
    if os.path.exists(user_data_file):
        with open(user_data_file, "r") as file:
            leaderboard_data = file.read()
            conn.sendall(leaderboard_data.encode())
    else:
        conn.sendall(b"Leaderboard is empty.")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(5)

print(f"server is listening on port {port}")

while True:
    conn, addr = s.accept()
    print(f"Connection from {addr}")

    conn.sendall(banner.encode())

    difficulty_options = b""
    for key, value in difficulty_levels.items():
        difficulty_options += f"{key} - {value[0]} to {value[1]}\n".encode()
    conn.sendall(difficulty_options)

    username = conn.recv(1024).decode().strip()
    difficulty_choice = conn.recv(1024).decode().strip().lower()

    while difficulty_choice not in difficulty_levels:
        conn.sendall(b"Invalid difficulty level! Choose again: ")
        difficulty_choice = conn.recv(1024).decode().strip().lower()

    low, high = difficulty_levels[difficulty_choice]
    guessme = generate_random_int(low, high)
    tries = 0

    conn.sendall(b"Let's start guessing!")
    while True:
        client_input = conn.recv(1024)
        if not client_input:
            break
        guess = int(client_input.decode().strip())
        print(f"{username} guessed: {guess}")
        tries += 1

        if guess == guessme:
            conn.sendall(f"Correct Answer, {username}! You won in {tries} tries!\n".encode())
            update_user_score(username, tries, difficulty_choice)
            break
        elif guess > guessme:
            conn.sendall(b"Guess Lower!")
        elif guess < guessme:
            conn.sendall(b"Guess Higher!")

    send_leaderboard(conn)
    conn.close()
    print(f"Connection with {addr} closed")

