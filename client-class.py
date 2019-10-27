import socket
from threading import Thread
import tkinter
import os

hostName = socket.gethostname()

HOST = socket.gethostbyname(hostName)
PORT = 42069  

buf_size = 1024 #largest message size accepted by the client socket

class Client:
    def __init__(self, sock=None):
        #Creates a socket instance if there isn't one already
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

        self.window = tkinter.Tk() #Creates window for chat instance
        self.window.title('Torq')

        self.sock.connect((HOST,PORT))

        self.initGUI()        

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
                new_message = self.sock.recv(buf_size).decode() #Receive message from server
                print(new_message)
                if new_message == 'send hostname':
                    self.sock.send(bytes(os.getlogin(), 'utf8'))
                else:
                    self.msg_list.insert(tkinter.END, new_message) #Add new msg to chat history
            except OSError: #Other client may have left the chat
                break

    def onClosing(self, event=None):
        self.msg.set('{quit}')
        self.send()

    def initGUI(self):
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


client = Client()

receive_thread = Thread(target=client.receive)
receive_thread.start()

tkinter.mainloop()