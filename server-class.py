import socket
from threading import Thread

room_size = 5

class Server:
    def __init__(self):
        self.clients = {} #Stores client names
        self.addresses = {} #Stores client addresses

        self.HOST = ''
        self.PORT = 42069
        self.buf_size = 1024

        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.bind((self.HOST,self.PORT))

        self.server_sock.listen(room_size)
        print("Waiting for connection...")
        accept_thread = Thread(target=self.AcceptIncomingConns)
        accept_thread.start()
        accept_thread.join()
        self.server_sock.close()

    def AcceptIncomingConns(self):
        while True:
            client, client_address = self.server_sock.accept()
            print('%s: %s has connected.' % client_address)
            client.send(bytes('Welcome to the chat!' + 'Now type your display name and press enter!', 'utf8'))
            self.addresses[client] = client_address
            Thread(target=self.handleClient, args=(client,)).start()

    def handleClient(self, client):
        client.send(bytes('send hostname', 'utf8'))
        name = client.recv(self.buf_size).decode()
        welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % name
        self.clients[client] = name #Adds new client to server list
        client.send(bytes(welcome, 'utf8'))

        msg = '%s has joined the chat!' % name 
        self.broadcast(bytes(msg, 'utf8')) #Tells chat room about new client

        
        while True:
            msg = client.recv(self.buf_size) #Receives messages from client
            if msg != bytes('{quit}', 'utf8'):
                self.broadcast(msg, name+': ') #Send message to chat room
            else:
                client.send(bytes('{quit}', 'utf8'))
                client.close()
                del self.clients[client]
                self.broadcast(bytes('%s has left the chat.' % name, 'utf8'))
                print('%s: %s has disconnected.' % self.addresses[client])
                break

    def broadcast(self, msg, prefix=''):
        for client in self.clients:
            client.send(bytes(prefix, 'utf8') + msg)

server = Server()