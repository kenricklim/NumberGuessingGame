import socket

host = "localhost"
port = 7777

def play_game():
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((host, port))
        except ConnectionRefusedError:
            print("Connection refused by the server.")
            return

        data = s.recv(1024)
        print(data.decode().strip())

        username = input("Enter your username: ")
        s.sendall(username.encode())

        
        difficulty_choice = input("Choose difficulty (a- Easy, b- Medium, c- Hard): ").lower()
        while difficulty_choice not in ['a', 'b', 'c']:
            print("Invalid choice. Please choose again.")
            difficulty_choice = input("Choose difficulty (a- Easy, b- Medium, c- Hard): ").lower()
        s.sendall(difficulty_choice.encode())

        while True:
            try:
                reply = s.recv(1024).decode().strip()
            except ConnectionResetError:
                print("Connection reset by the server.")
                break
            except ConnectionAbortedError:
                print("Connection aborted by the server.")
                break

            if "Correct" in reply:
                print(reply)
                break
            elif reply.startswith("a -") or reply.startswith("b -") or reply.startswith("c -"):
                print(reply)
            else:
                print(reply)
                print("Enter your guess: ", end="", flush=True)
                guess = input().strip()
                s.sendall(guess.encode())

        leaderboard_data = s.recv(4096).decode().strip()
        print("\n=== Leaderboard ===")
        print(leaderboard_data)

        play_again = input("Do you want to play again? (yes/no): ").strip().lower()
        if play_again != "yes":
            break

    s.close()

play_game()
