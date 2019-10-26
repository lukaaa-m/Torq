import socket
from threading import Thread
import tkinter

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
        self.window.title = 'Torq'
        initGUI()

    def connect(self,host,port):
        self.sock.connect((host,port))

    def send(event=None):
        temp_msg = self.msg.get() #Gets msg from tkinter input field
        self.msg.set('') #Clears input field
        self.sock.send(temp_msg.encode())

        if temp_msg = '{quit}': #Closes socket and chat window if window is exited
            self.sock.close()
            self.window.quit()

    def receive():
        while True:
            try:
                new_message = self.sock.recv(buf_size).decode() #Receive message from server
                self.msg_list.insert(tkinter.END, new_message) #Add new msg to chat history
            except OSError: #Other client may have left the chat
                break

    def onClosing(event=None):
        self.msg.set('{quit}')
        self.send()

    def initGUI(self):
        #Frame for chat window
        self.chat_frame = tkinter.Frame(self.window)
        self.msg = tkinter.StringVar()  #For the messages to be sent
        self.msg.set("Type your messages here.")
        self.scrollbar = tkinter.Scrollbar(chat_frame)  #To navigate through past messages

        #Box to contain message history
        self.msg_list = tkinter.Listbox(chat_frame, height=15, width=50, yscrollcommand=scrollbar.set)
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
        self.msg_list.pack()
        self.messages_frame.pack()

        #Message input field
        self.msg_field = tkinter.Entry(self.window, textvariable=msg)
        self.msg_field.bind("<Return>", self.send())
        self.msg_field.pack()
        self.send_button = tkinter.Button(self.window, text="Send", command=self.send())
        self.send_button.pack()

        self.window.protocol("WM_DELETE_WINDOW", self.onClosing)


client = Client()

client.connect(HOST, PORT)

receive_thread = Thread(target=receive)
receive_thread.start()