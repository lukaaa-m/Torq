import socket
from threading import Thread
import tkinter as tk
import os

#make a server search class as well
#only allow program to progress 'after' a host has been ascertained from the server search

class Client:
    def __init__(self, sock=None):
        #Creates a socket instance if there isn't one already
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

        self.bufsize = 1024 #largest message size accepted by the client socket

        self.initChatGUI()

        receive_thread = Thread(target=self.receive)
        receive_thread.start()

    def send(self, event=None):
        temp_msg = self.msg.get() #Gets msg from tk input field
        self.msg.set('') #Clears input field
        self.sock.send(temp_msg.encode())

        if temp_msg == '{quit}': #Closes socket and chat window if window is exited
            self.sock.close()
            self.chat_window.quit()

    def receive(self):
        while True:
            try:
                new_message = self.sock.recv(self.bufsize).decode() #Receive message from server
                print(new_message)
                if new_message == 'send hostname':
                    self.sock.send(bytes(os.getlogin(), 'utf8'))
                else:
                    self.msg_list.insert('end', new_message) #Add new msg to chat history 
            
            except OSError: #Other client may have left the chat
                #print('No socket yet')
                continue    

    def initChatGUI(self):
        self.chat_window = tk.Tk()
        self.chat_window.title('Torq')

        #Frame for chat window
        self.chat_frame = tk.Frame(self.chat_window)
        self.msg = tk.StringVar()  #For the messages to be sent
        self.msg.set("")
        self.scrollbar = tk.Scrollbar(self.chat_frame)  #To navigate through past messages

        #Box to contain message history
        self.msg_list = tk.Listbox(self.chat_frame, height=15, width=50, yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.msg_list.pack(side=tk.LEFT, fill=tk.BOTH)
        self.msg_list.pack()
        self.chat_frame.pack()

        #Message input field
        self.msg_field = tk.Entry(self.chat_window, textvariable=self.msg)
        self.msg_field.bind("<Return>", self.send)
        self.msg_field.pack()
        self.send_button = tk.Button(self.chat_window, text="Send", command=self.send)
        self.send_button.pack()

        self.chat_window.protocol("WM_DELETE_WINDOW", self.onClosing)

    def onClosing(self, event=None):
        self.msg.set('{quit}')
        self.send()

class ServerSearch:
    def __init__(self):
        self.search_window = tk.Tk() #Creates window for server search
        self.search_window.title('Torq')

        self.search = tk.StringVar()
        self.search.set('')
        search_field = tk.Entry(self.search_window, textvariable=self.search)
        search_field.bind("<Return>", self.createClient)
        search_field.pack()

        self.send_button = tk.Button(self.search_window, text="Send", command=self.createClient)
        self.send_button.pack()

        self.search_window.protocol("WM_DELETE_WINDOW", self.search_window.quit())

    def createClient(self, event=None):
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print(self.search.get())
        PORT = 42069
        HOST = socket.gethostbyname(self.search.get())
        client_sock.connect((HOST,PORT))

        self.search_window.quit()

        self.client = Client(client_sock)

search = ServerSearch()

tk.mainloop()
