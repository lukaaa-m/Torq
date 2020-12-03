'''Server'''
#send UDP broadcast
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.sendto(bytes(socket.gethostname(),'utf8'), (self.HOST, self.PORT))



'''Client'''

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
