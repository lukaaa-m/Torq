import socket
from threading import Thread
import tkinter
import os

hostName = socket.gethostname()

HOST = socket.gethostbyname(hostName)
#HOST = '10.223.130.72'
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
        if(len(temp_msg) > 1014):
            self.msg_list.configure(state="normal")
            self.msg_list.insert(tkinter.END, 'Message exceeds 1014 characters!' + '\n')
            self.msg_list.configure(state="disabled")
            self.msg_list.see(tkinter.END)
        else:
            self.msg.set('') #Clears input field
            self.sock.send(temp_msg.encode())

        if temp_msg == '{quit}': #Closes socket and chat window if window is exited
            self.sock.close()
            self.window.quit()

    def receive(self):
        while True:
            try:
                new_message = self.sock.recv(buf_size).decode() #Receive message from server
                if new_message == 'send hostname':
                    self.sock.send(bytes(os.getlogin(), 'utf8'))
                else:
                    self.msg_list.configure(state="normal")
                    self.msg_list.insert(tkinter.END, new_message + '\n') #Add new msg to chat history
                    self.msg_list.configure(state="disabled")
                    self.msg_list.see(tkinter.END)
            except OSError: #Other client may have left the chat
                break

    def onClosing(self, event=None):
        self.msg.set('{quit}')
        self.send()

    def initGUI(self):
        #Frame for chat window
        self.chat_frame = tkinter.Frame(self.window, bg="#36393e")
        self.msg = tkinter.StringVar()  #For the messages to be sent
        self.msg.set("")
        self.scrollbar = tkinter.Scrollbar(self.chat_frame)  #To navigate through past messages

        #Box to contain message history
        self.msg_list = tkinter.Text(self.chat_frame, height=25, width=60, yscrollcommand=self.scrollbar.set, wrap=tkinter.WORD, padx=10, font=("Verdana", 10), bg="#36393e", fg="white", spacing1=6, selectborderwidth=0, bd=0, selectbackground="gray")
        self.msg_list.configure(state="disabled")
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
        self.chat_frame.pack()

        #Message input field
        self.msg_field = tkinter.Entry(self.window, textvariable=self.msg, width=64, justify='left', font=("Verdana", 10), bg='#484B52', fg='white', selectborderwidth=0, bd=0, selectbackground="gray")
        self.msg_field.bind("<Return>", self.send)
        self.msg_field.pack(side="top", fill="x")

        self.window.protocol("WM_DELETE_WINDOW", self.onClosing)
        self.window.resizable(False, False)


client = Client()

receive_thread = Thread(target=client.receive)
receive_thread.start()

tkinter.mainloop()