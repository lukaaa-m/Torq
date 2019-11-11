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

        tk.mainloop()

        


    def send(self, event=None):
        temp_msg = self.msg.get() #Gets msg from tkinter input field
        if(len(temp_msg) > 1014):
            self.msg_list.configure(state="normal")
            self.msg_list.insert(tk.END, 'Message exceeds 1014 characters!' + '\n')
            self.msg_list.configure(state="disabled")
            self.msg_list.see(tk.END)
            self.msg.set('')
        else:
            self.msg.set('') #Clears input field
            self.sock.send(temp_msg.encode())

        if temp_msg == '{quit}': #Closes socket and chat window if window is exited
            self.sock.close()
            self.chat_window.destroy()

    def receive(self):
        while True:
            try:
                new_message = self.sock.recv(self.bufsize).decode() #Receive message from server
                if new_message == 'send hostname':
                    self.sock.send(bytes(os.getlogin(), 'utf8'))
                else:
                    self.msg_list.configure(state="normal")
                    self.msg_list.insert(tk.END, new_message + '\n') #Add new msg to chat history
                    self.msg_list.configure(state="disabled")
                    self.msg_list.see(tk.END)
            except OSError: #Other client may have left the chat
                #print('No socket yet')
                continue    

    def initChatGUI(self):
        self.chat_window = tk.Tk()
        self.chat_window.title('Torq')

        #Frame for chat window
        self.chat_frame = tk.Frame(self.chat_window, bg="#36393e")
        self.msg = tk.StringVar()  #For the messages to be sent
        self.msg.set("")
        self.scrollbar = tk.Scrollbar(self.chat_frame)  #To navigate through past messages

        #Box to contain message history
        self.msg_list = tk.Text(self.chat_frame, height=25, width=60, yscrollcommand=self.scrollbar.set, wrap=tk.WORD, padx=10, font=("Verdana", 10), bg="#36393e", fg="white", spacing1=6, selectborderwidth=0, bd=0, selectbackground="gray")
        self.msg_list.configure(state="disabled")
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.msg_list.pack(side=tk.LEFT, fill=tk.BOTH)
        self.chat_frame.pack()

        #Message input field
        self.msg_field = tk.Entry(self.chat_window, textvariable=self.msg, width=64, justify='left', font=("Verdana", 10), bg='#484B52', fg='white', selectborderwidth=0, bd=0, selectbackground="gray")
        self.msg_field.bind("<Return>", self.send)
        self.msg_field.pack(side="top", fill="x")

        self.chat_window.protocol("WM_DELETE_WINDOW", self.onClosing)
        self.chat_window.resizable(False, False)
        

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

        tk.mainloop()

    def createClient(self, event=None):
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print(self.search.get())
        PORT = 42069
        HOST = socket.gethostbyname(self.search.get())
        client_sock.connect((HOST,PORT))

        self.search_window.destroy()

        self.client = Client(client_sock)

search = ServerSearch()
#client = Client()

