import socket
from threading import Thread
from datetime import datetime
def getTimeStamp(format):
    dt_obj = datetime.now()
    return dt_obj.strftime(format)

def choosePort():
    for port in range(42069, 42079):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            res = sock.connect_ex(('', port))
            if res == 0:
                return port

class Server:
    def __init__(self):
        self.clients = {} #Stores client names
        self.addresses = {} #Stores client addresses

        self.HOST = 'localhost'
        self.PORT = 42069 #choosePort()
        self.buf_size = 1024

        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.bind((self.HOST,self.PORT))
        self.server_sock.listen(5)

        print('Server initialised on', getTimeStamp('%d-%b-%Y'), 'at', getTimeStamp('%H:%M:%S'))
        print('Port:', self.PORT)
        print("Waiting for connection...")

        #Starts coroutine to constantly listen for new connections
        accept_thread = Thread(target=self.AcceptIncomingConns)
        accept_thread.start()
        accept_thread.join()
        self.server_sock.close()

    def AcceptIncomingConns(self):
        while True:
            #send UDP broadcast
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
            sock.sendto(bytes(socket.gethostname(),'utf8'), (self.HOST, self.PORT))

            client, client_address = self.server_sock.accept() #Accept client connection
            print(getTimeStamp("[%H:%M:%S]"), '%s: %s has connected.' % client_address)

            client.send(bytes('send hostname', 'utf8')) #Requests login name
            self.addresses[client] = client_address

            #Coroutine to handle new client
            Thread(target=self.handleClient, args=(client,)).start()

    def handleClient(self, client):
        name = client.recv(self.buf_size).decode() #First message is expected to be the login name
        welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % name
        self.clients[client] = name #Adds new client to server list
        client.send(bytes(welcome, 'utf8'))

        msg = '%s has joined the chat!' % name 
        self.broadcast(bytes(msg, 'utf8')) #Tells chat room about new client

        
        while True:
            try:
                msg = client.recv(self.buf_size) #Receives messages from client
                if msg != bytes('{quit}', 'utf8'):
                    self.broadcast(msg, name+': ') #Send message to chat room
                else:
                    #client.send(bytes('{quit}', 'utf8'))
                    client.close()
                    del self.clients[client]
                    self.broadcast(bytes('%s has left the chat.' % name, 'utf8'))
                    print(getTimeStamp("[%H:%M:%S]"), '%s: %s has disconnected.' % self.addresses[client])
                    break
            except OSError:
                client.close()
                del self.clients[client]
                self.broadcast(bytes('%s has left the chat.' % name, 'utf8'))
                print(getTimeStamp("[%H:%M:%S]"), '%s: %s has disconnected.' % self.addresses[client])
                break

    def broadcast(self, msg, prefix=''):
        print(getTimeStamp("[%H:%M:%S]"), prefix + msg.decode())
        for client in self.clients:
            client.send(bytes(prefix, 'utf8') + msg)
            

server = Server()