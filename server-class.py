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

        self.server_sock = socket(AF_INET, SOCK_STREAM)
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
            client.send(bytes('Welcome to the chat!' + 'Now type your display name and press enter!'))
            self.addresses[client] = client_address
            Thread(target=handleClient, args=(client,)).start()

    def handleClient(self, client):
        name = client.recv(self.buf_size).decode()
        welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % name
        self.clients[client] = name #Adds new client to server list
        client.send(bytes(welcome))

        msg = '%s has joined the chat!' % name 
        broadcast(bytes(msg)) #Tells chat room about new client

        
        while True:
            msg = client.recv(self.buf_size) #Receives messages from client
            if msg != bytes('{quit}'):
                broadcast(msg, name+': ') #Send message to chat room
            else:
                client.send(bytes('{quit}'))
                client.close()
                del clients[client]
                broadcast(bytes('%s has left the chat.' % name))
                break

    def broadcast(self, msg, prefix=''):
        for client in self.clients:
            client.send(bytes(prefix) + msg)

server = Server()