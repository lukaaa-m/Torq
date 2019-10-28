import socket
from threading import Thread
import tkinter
import os
from functools import partial



#HOST = socket.gethostbyname(hostName)
#PORT = 42069  



class Client:
    def __init__(self, sock=None):
        #Creates a socket instance if there isn't one already
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

        self.window = tkinter.Tk() #Creates window for chat instance
        self.window.title('Torq')

        self.bufsize = 1024 #largest message size accepted by the client socket
        #self.sock.connect((HOST,PORT))

        self.initServerListGUI()        

    def send(self, event=None):
        temp_msg = self.msg.get() #Gets msg from tkinter input field
        self.msg.set('') #Clears input field
        self.sock.send(temp_msg.encode())

        if temp_msg == '{quit}': #Closes socket and chat window if window is exited
            self.sock.close()
            self.window.quit()

    def receive(self):
        while True:
            try:
                new_message = self.sock.recv(self.bufsize).decode() #Receive message from server
                print(new_message)
                if new_message == 'send hostname':
                    self.sock.send(bytes(os.getlogin(), 'utf8'))
                else:
                    self.msg_list.insert(tkinter.END, new_message) #Add new msg to chat history
                    
            except OSError: #Other client may have left the chat
                break

    def findServers(self):
        servers = [] #Stores all discovered servers
        for port in range(42069,42079):
            print ('started looking for ports')
            sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #UDP connection
            sock.bind(('', port))
            print('bound to port')
            servername, addr = sock.recvfrom(self.bufsize) #Receives UDP broadcast from server (contains a message + server address)
            if servername is not None:
                print('received from port')
                servers.add(servername, addr)
            
            #self.connect(addr)
        print('finished looking for ports')
        return servers

    def connect(self,addr):
        self.sock.connect((addr))
        self.initGUI()

        receive_thread = Thread(target=client.receive)
        receive_thread.start()


    def initServerListGUI(self):
        print('started server list gui')
        server_frame = tkinter.Frame(self.window)
        server_list = tkinter.Listbox(server_frame, height=10, width=50)
        servers = self.findServers()
        

        for server in servers:
            server_list.insert(tkinter.END, server[0]) #Inserts first part of server tuple (the hostname) into the listbox
        
    
        choose_server = tkinter.Button(self.window, text='Join') #Runs connect with the second part (the address) of the server connected to the selected index in the listbox
        if server_list.curselection():
            selected_server = servers[server_list.curselection()[0]]
            choose_server.command(partial(self.connect(selected_server[1])))
        
        server_list.pack()
        choose_server.pack()

        self.window.protocol("WM_DELETE_WINDOW", self.window.quit())


    def initGUI(self):
        for widget in self.window.winfo_children():
            widget.destroy() #Clears all widgets from the serverlist screen

        #Frame for chat window
        self.chat_frame = tkinter.Frame(self.window)
        self.msg = tkinter.StringVar()  #For the messages to be sent
        self.msg.set("")
        self.scrollbar = tkinter.Scrollbar(self.chat_frame)  #To navigate through past messages

        #Box to contain message history
        self.msg_list = tkinter.Listbox(self.chat_frame, height=15, width=50, yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
        self.msg_list.pack()
        self.chat_frame.pack()

        #Message input field
        self.msg_field = tkinter.Entry(self.window, textvariable=self.msg)
        self.msg_field.bind("<Return>", self.send)
        self.msg_field.pack()
        self.send_button = tkinter.Button(self.window, text="Send", command=self.send)
        self.send_button.pack()

        self.window.protocol("WM_DELETE_WINDOW", self.onClosing)

    def onClosing(self, event=None):
        self.msg.set('{quit}')
        self.send()

client = Client()

tkinter.mainloop()