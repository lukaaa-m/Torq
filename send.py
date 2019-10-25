hostName = socket.gethostname()

HOST = socket.gethostbyname(hostName)
PORT = 42069

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect((HOST,PORT))

def sendMessage(message):
    sock.send(message)