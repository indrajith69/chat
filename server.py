import socket
import threading
from tkinter import *
from tkinter import messagebox
from tkinter import ttk

class server:
	def __init__(self):
		self.bg = '#081828'
		self.fg = '#00FF00'
		self.font = 18
		self.server_running = False
		self.clients = []
		self.usernames = []
		self.window()

	def clear(self,frame):
		for widget in frame.winfo_children():
			widget.destroy()

	def connection_info(self):
		self.clear(self.root)
		self.frame_widgets = Frame(self.root,bg=self.bg)
		self.root.geometry('350x300')
		self.frame_ip   = Frame(self.frame_widgets,bg=self.bg)
		self.frame_port = Frame(self.frame_widgets,bg=self.bg)
		self.entry_ip = Entry(self.frame_ip,bg=self.bg,fg=self.fg,font=16)
		self.entry_port = Entry(self.frame_port,bg=self.bg,fg=self.fg,font=16)
		self.label_ip = Label(self.frame_ip,bg=self.bg,fg=self.fg,text='ip',font=20)
		self.label_port = Label(self.frame_port,bg=self.bg,fg=self.fg,text='port',font=20)
		self.btn_set = Button(self.root,bg=self.bg,fg=self.fg,text='okay',command=self.start_server)

		self.label_ip.pack(fill=BOTH,side=TOP)
		self.label_port.pack(fill=BOTH,side=TOP)
		self.entry_ip.pack(fill=X)
		self.entry_port.pack(fill=X)
		self.btn_set.pack(fill=X,side=BOTTOM)
		self.frame_widgets.pack(fill=BOTH,side=BOTTOM,expand=True)
		self.frame_ip.pack(fill=BOTH,side=LEFT,expand=True)
		self.frame_port.pack(fill=BOTH,side=RIGHT,expand=True)

	def window(self):
		self.root = Tk()
		self.root.config(bg=self.bg)
		self.root.geometry('350x300')
		self.root.title('server')
		self.root.protocol("WM_DELETE_WINDOW",self.on_closing)

		self.connection_info()
		self.root.mainloop()

	def start_server(self):
		self.server_running = True
		self.host,self.port = self.entry_ip.get(),int(self.entry_port.get())
		self.clear(self.root)
		self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.server.settimeout(60)
		self.server.bind((self.host,self.port))
		self.server.listen()

		Label(self.root,text=f'server started at\n\n{self.host}:{self.port}',
			bg=self.bg,fg=self.fg,font=self.font).pack(fill=BOTH,expand=True)
		self.server_thread = threading.Thread(target=self.receive)
		self.server_thread.start()

	def on_closing(self): 
		if self.server_running:
			self.server_running = False
			for client in self.clients:
				client.close()
		self.root.destroy()

	def broadcast(self,message):
		if not len(message.decode('ascii').split(':')[1].strip()):
			return
		for client in self.clients:
			client.send(message)

	def disconnect(self,client):
		index = self.clients.index(client)
		username = self.usernames[index]
		self.clients.remove(client)
		self.usernames.remove(username)
		client.close()
		self.broadcast(f'global;server:{username} has left the chat'.encode('ascii'))
		message = 'update:'+';'.join(self.usernames)
		self.broadcast(message.encode('ascii'))
					


	def handle(self,client):
		while self.server_running:
			try:
				message = client.recv(1024)

				if not len(message):
					continue

				if message.decode('ascii')=='<<exit>>':
					self.disconnect(client)
					break

				receiver = message.decode('ascii').split(';')[0]
				sender = message.decode('ascii').split(';')[1].split(':')[0]

				if receiver=='global':
					self.broadcast(message)
				else:
					rclient = self.clients[self.usernames.index(receiver)]
					sclient = self.clients[self.usernames.index(sender)]
					rclient.send(message)
					sclient.send(message)
			except Exception as err:
				self.disconnect(client)
				break

	def receive(self):
		while self.server_running:
			try:
				client , address = self.server.accept()
				username = client.recv(1024).decode('ascii')
				if username in self.usernames:
					client.send('username unavailable'.encode('ascii'))
					continue
				else:
					client.send('okay'.encode('ascii'))

				self.usernames.append(username)
				self.clients.append(client)

				message = 'update:'+';'.join(self.usernames)
				self.broadcast(message.encode('ascii'))
				thread = threading.Thread(target=self.handle,args=(client,))
				thread.start()
			except Exception as err:
				pass


serv = server()
