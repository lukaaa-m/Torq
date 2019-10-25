import socket

hostName = socket.gethostname()

HOST = socket.gethostbyname(hostName)
PORT = 42069

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def listenForMessage():
    sock.bind((HOST,PORT))
    sock.listen()
    conn, addr = sock.accept()
    with conn:
        while True:
            message = conn.recv(1024)

            if not message:
                break