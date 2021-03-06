import socket
from threading import Thread
from datetime import datetime
from badwords import bad_words
import re


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
        self.muted_clients = {}

        self.HOST = ''
        self.PORT = 42069 #choosePort()
        self.buf_size = 1024

        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.bind((self.HOST,self.PORT))
        self.server_sock.listen(5)

        print('Server initialised on', getTimeStamp('%d-%b-%Y'), 'at', getTimeStamp('%H:%M:%S'))
        print('Port:', self.PORT)
        print("Waiting for connection...")

        #Starts coroutine to wait for server commands
        command_thread = Thread(target=self.handleCommands)
        command_thread.start()

        #Starts coroutine to constantly listen for new connections
        accept_thread = Thread(target=self.acceptIncomingConns)
        accept_thread.start()
        accept_thread.join()
        self.server_sock.close()

        
    def acceptIncomingConns(self):
        while True:
            
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
                new_msg = client.recv(self.buf_size) #Receives messages from client
                if new_msg != bytes('{quit}', 'utf8'):
                    if client not in self.muted_clients:
                        self.broadcast(self.censorBadWords(new_msg), name+': ') #Send message to chat room
                    else:
                        client.send(bytes('You have been muted','utf8'))
                else:
                    #client.send(bytes('{quit}', 'utf8'))
                    client.close()
                    del self.clients[client]
                    self.broadcast(bytes('%s has left the chat.' % name, 'utf8'))
                    print(getTimeStamp("[%H:%M:%S]"), '%s: %s has disconnected.' % self.addresses[client])
                    break
            except OSError:
                try:
                    client.close()
                    del self.clients[client]

                    self.broadcast(bytes('%s has left the chat.' % name, 'utf8'))
                    print(getTimeStamp("[%H:%M:%S]"), '%s: %s has disconnected.' % self.addresses[client])
                    break
                except KeyError:
                    break

    def broadcast(self, msg, prefix=''):
        print(getTimeStamp("[%H:%M:%S]"), prefix + msg.decode())
        for client in self.clients:
            client.send(bytes(prefix, 'utf8') + msg)

    def censorBadWords(self, msg):
        msg = msg.decode()
        
        for word in bad_words:
            #word to replace, replace with word, original msg
            msg = re.sub(word, '*'*len(word), msg, flags=re.IGNORECASE)

        return bytes(msg, 'utf8')
        
    '''*SERVER COMMANDS*'''

    def mute(self, target):
        self.muted_clients[target] = self.clients[target]

    def unmute(self,target):
        target.send(bytes('You have been unmuted','utf8'))
        del self.muted_clients[target]
                
    def kick(self, target):
        target.send(bytes('You were kicked','utf8'))

        self.broadcast(bytes('%s was kicked' % self.clients[target], 'utf8'))

        target.close()
        del self.clients[target]

    def badWordDump(self, target):
        for word in bad_words:
            target.send(bytes(word+'\n','utf8'))

    def handleCommands(self):
        self.commands = {
            'mute' : self.mute,
            'kick' : self.kick,
            'unmute' : self.unmute,
            'badworddump' : self.badWordDump
        }
        while True:
            try:
                command = input()
                action, target = command.split()[0], command.split()[1]
                target_exists = False

                if action not in self.commands:
                    print('That command is not valid')
                    continue
                
                for client in self.clients:
                    if self.clients[client] == target:
                        target = client
                        target_exists = True

                if not target_exists:
                    print('That client does not exist')
                    continue

                self.commands[action](target) #Runs the action's corresponding function (from self.commands dict) with target parameter
            except (IndexError, KeyError):
                print('Error: format >> [action] [target]')
         


server = Server()
