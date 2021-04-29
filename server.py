import socket
import sqlite3
import pickle
import threading
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

class server:
	def __init__(self):
		self.bg = '#081828'
		self.fg = '#00FF00'
		self.font = 18
		self.server_running = False
		self.clients = []
		self.usernames = []

		self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.server.settimeout(60)
		self.db = sqlite3.connect('messages.db',check_same_thread=False)
		self.cur = self.db.cursor()
		
		self.root = Tk()
		self.root.config(bg=self.bg)
		self.root.geometry('350x300')
		self.root.title('server')
		self.root.protocol("WM_DELETE_WINDOW",self.stop_server)

		self.connection_info()
		self.root.mainloop()

	def clear(self,frame):
		for widget in frame.winfo_children():
			widget.destroy()

	def connection_info(self):
		self.frame_widgets = Frame(self.root,bg=self.bg)
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

	def start_server(self):
		self.server_running = True
		self.host,self.port = self.entry_ip.get(),int(self.entry_port.get())
		self.server.bind((self.host,self.port))
		self.server.listen()
		self.clear(self.root)
		Label(self.root,text=f'server started at\n\n{self.host}:{self.port}',
			bg=self.bg,fg=self.fg,font=self.font).pack(fill=BOTH,expand=True)
		self.server_thread = threading.Thread(target=self.receive)
		self.server_thread.start()

	def stop_server(self):
		if self.server_running:
			self.server_running = False
			for client in self.clients:
				client.close()
		self.db.close()
		self.root.destroy()

	def disconnect(self,client):
		index = self.clients.index(client)
		username = self.usernames[index]
		self.clients.remove(client)
		self.usernames.remove(username)
		client.send(pickle.dumps(('<<exit>>','')))
		client.close()
		message = pickle.dumps(('<<update>>',self.usernames))
		self.broadcast(message)

	def store(self,data):
		sender = data['sender']
		receiver = data['receiver']
		message = data['message']
		time = datetime.now()
		if not len(message.strip()):
			return
		self.cur.execute("INSERT INTO messages VALUES(:sender,:receiver,:message,:time)",
			{'sender':sender,'receiver':receiver,'message':message,'time':time})
		self.db.commit()

	def view_message(self,data):
		sender = data['sender']
		receiver = data['receiver']

		if receiver=='global':
			self.cur.execute("SELECT sender,message FROM messages WHERE receiver=:receiver ORDER BY time ASC",
				{'receiver':receiver})
			messages = self.cur.fetchall()
			conversation = ''
			for message in messages:
				conversation+=':'.join(message)+'\n'

			data = pickle.dumps(('<<message>>',[sender,receiver,conversation]))
			self.broadcast(data)
		else:
			self.cur.execute("SELECT sender,message FROM messages WHERE (sender=:sender and receiver=:receiver) or (sender=:receiver and receiver=:sender) ORDER BY time ASC",
				{'sender':sender,'receiver':receiver})
			messages = self.cur.fetchall()
			conversation = ''
			for message in messages:
				conversation+=':'.join(message)+'\n'
			data = pickle.dumps(('<<message>>',[sender,receiver,conversation]))

			user1 = self.clients[self.usernames.index(sender)]
			user2 = self.clients[self.usernames.index(receiver)]

			user1.send(data)
			user2.send(data)

	def broadcast(self,data):
		if not len(data):
			return
		for client in self.clients:
			client.send(data)

	def handle(self,client):
		while self.server_running:
			message,data = pickle.loads(client.recv(1024))
			if message=='<<message>>':
				sender,receiver,msg = data
				data = {'sender':sender,'receiver':receiver,'message':msg}
				self.store(data)
				self.view_message({'sender':sender,'receiver':receiver})
			elif message=='<<view>>':
				sender,receiver=data
				self.view_message({'sender':sender,'receiver':receiver})
			elif message=='<<exit>>':
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
					client.recv(1024)

				self.usernames.append(username)
				self.clients.append(client)

				self.broadcast(pickle.dumps(('<<update>>',self.usernames)))
				thread = threading.Thread(target=self.handle,args=(client,))
				thread.start()
			except Exception as err:
				print(err)



#192.168.29.98:5050


serv = server()



















