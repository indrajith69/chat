import socket
import threading
from tkinter import *
from tkinter import messagebox
from tkinter import ttk



class chat_app:
	"""docstring for chat_app"""
	def __init__(self):
		self.bg = '#081828'
		self.fg = '#00FF00'
		self.border='#000000'
		self.font = 16
		self.glb = 'global'
		self.me  = 'me'
		self.client_running = False

		self.users = []
		self.messages = {self.glb:''}
		self.current_chat = self.glb

		self.root = Tk()
		self.root.config(bg=self.bg)
		self.style = ttk.Style()
		self.style.theme_use("default")
		self.style.configure("Treeview", background=self.bg,fieldbackground=self.bg, foreground="white")
		self.style.map("Treeview")
		self.root.protocol("WM_DELETE_WINDOW",self.on_closing)

		self.connection_info()
		self.root.mainloop()

	def on_closing(self):
		if self.client_running:
			self.client_running = False
			self.client.send('<<exit>>'.encode('ascii'))
			self.client.close()
		self.root.destroy()

	def window(self):
		self.clear(self.root)
		self.main = PanedWindow(self.root,bg=self.border)
		self.win_users = Frame(self.main,bg=self.border)
		self.win_chat  = Frame(self.main,bg=self.border)
		self.display_area   = LabelFrame(self.win_chat,bg=self.bg)
		self.chat_area = LabelFrame(self.win_chat,bg=self.bg)
		self.search_users  = LabelFrame(self.win_users,bg=self.bg)
		self.display_users = LabelFrame(self.win_users,bg=self.bg)

		self.main.add(self.win_users)
		self.main.add(self.win_chat)
		self.display_area.pack(expand=True,fill=BOTH)
		self.chat_area.pack(fill=BOTH)
		self.search_users.pack(fill=BOTH)
		self.display_users.pack(expand=True,fill=BOTH)

		self.main.pack(fill=BOTH,expand=True)

	def widgets(self):
		#DISPLAY AREA WIDGETS
		self.display = Text(self.display_area,bg=self.bg,fg=self.fg,font=14)
		self.scrollbar = Scrollbar(self.display_area,bg=self.bg)
		self.display.config(yscrollcommand=self.scrollbar.set)
		self.scrollbar.config(command=self.display.yview)
		self.scrollbar.pack(fill=Y,side=RIGHT)
		self.display.pack(fill=BOTH,expand=True)
		#CHAT AREA WIDGETS
		self.chat_box = Entry(self.chat_area,bg=self.bg,fg=self.fg,font=14)
		self.send_btn = Button(self.chat_area,bg=self.bg,fg=self.fg,text='send',command=self.write)
		self.chat_box.pack(fill=BOTH,side=LEFT,expand=True)
		self.send_btn.pack(fill=BOTH,expand=True)
		#USERS AREA WIDGETS
		self.users_list = ttk.Treeview(self.display_users, columns=1, show='', height=8)
		self.sb = Scrollbar(self.display_users,bg=self.bg)
		self.users_list.config(yscrollcommand=self.sb.set)
		self.sb.config(command=self.users_list.yview)
		self.sb.pack(fill=Y,side=RIGHT)
		self.users_list.pack(fill=BOTH,expand=True)
		#USERINFO AREA WIDGETS
		self.label = Label(self.search_users,bg=self.bg,fg=self.fg,text='connected users',font=16)
		self.label.pack(expand=True)

		self.users_list.bind("<<TreeviewSelect>>",self.onselect)

	def connection_info(self):
		self.clear(self.root)
		self.frame_widgets = Frame(self.root,bg=self.bg)
		self.root.geometry('350x300')
		self.frame_ip   = Frame(self.frame_widgets,bg=self.bg)
		self.frame_port = Frame(self.frame_widgets,bg=self.bg)
		self.entry_ip = Entry(self.frame_ip,bg=self.bg,fg=self.fg,font=16)
		self.entry_username = Entry(self.frame_port,bg=self.bg,fg=self.fg,font=16)
		self.label_ip = Label(self.frame_ip,bg=self.bg,fg=self.fg,text='ip:port',font=20)
		self.label_username = Label(self.frame_port,bg=self.bg,fg=self.fg,text='username',font=20)
		self.btn_set = Button(self.root,bg=self.bg,fg=self.fg,text='okay',command=self.chat)

		self.label_ip.pack(fill=BOTH,side=TOP)
		self.label_username.pack(fill=BOTH,side=TOP)
		self.entry_ip.pack(fill=X)
		self.entry_username.pack(fill=X)
		self.btn_set.pack(fill=X,side=BOTTOM)
		self.frame_widgets.pack(fill=BOTH,side=BOTTOM,expand=True)
		self.frame_ip.pack(fill=BOTH,side=LEFT,expand=True)
		self.frame_port.pack(fill=BOTH,side=RIGHT,expand=True)

	def chat(self):
		ip,username=self.entry_ip.get(),self.entry_username.get()
		host = ip.split(':')[0]
		port = int(ip.split(':')[1])
		
		self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.client.connect((host,port))

		self.username = username
		self.client.send(self.username.encode('ascii'))

		status = self.client.recv(1024).decode('ascii')
		if status=='okay':
			self.client_running = True
		else:
			messagebox.showwarning('connection error','username unavailable')
			self.on_closing()
			return

		self.clear(self.root)
		self.root.geometry('800x600')
		self.root.title(self.username)
		self.window()
		self.widgets()
		self.add_user((0,self.glb))

		write_thread   = threading.Thread(target=self.write)
		receive_thread = threading.Thread(target=self.recv)
		write_thread.start()
		receive_thread.start()


	def clear(self,frame):
		for widget in frame.winfo_children():
			widget.destroy()

	def add_user(self,user):
		ID,VALUE = user
		self.users_list.insert(parent='',index=ID,iid=ID,values=VALUE)

	def onselect(self, event):
		try:
			user = self.users_list.selection()[0]
			self.messages[self.current_chat] = self.display.get('1.0',END)
			self.display.delete('1.0',END)
			self.current_chat = self.users_list.item(user,'values')[0]
			if self.current_chat in self.messages:
				self.display.insert(END,self.messages[self.current_chat])
		except:
			pass

	def recv(self):
		while True and self.client_running:
			try:
				message = self.client.recv(1024).decode('ascii')
				if message[:7]=='update:':
					users = message.split(':')[1].split(';')
					users.remove(self.username)
					self.users_list.delete(*self.users_list.get_children())
					self.add_user((0,'global'))
					for user in users:
						self.add_user((users.index(user)+1,user))
						if user not in self.users:
							self.messages[self.glb]+='\n'+f'{user} has joined the chat'
							self.display.delete('1.0',END)
							self.display.insert(END,self.messages[self.current_chat])
					self.users = users

				else:
					temp = message.split(';')
					receiver = temp[0]
					sender = temp[1].split(':')[0]
					message = temp[1]

					if self.current_chat not in self.messages:
						self.messages[self.current_chat]=''
					if receiver==self.glb:
						if sender==self.username:
							self.messages[receiver]+='\n'+message.replace(sender,self.me)
						else:
							self.messages[receiver]+='\n'+message
					else:
						if sender==self.username:
							self.messages[self.current_chat]+='\n'+message.replace(sender,self.me)
						elif sender not in self.messages:
							self.messages[sender]=message
						else:
							self.messages[sender]+='\n'+message

					self.display.delete('1.0',END)
					if 'has left the chat' in message:
						self.display.insert(END,self.messages[self.glb])
					else:
						self.display.insert(END,self.messages[self.current_chat])
			except:
				self.client.close()
				break

	def write(self):
		try:
			selected = self.users_list.focus()
			data = self.users_list.item(selected,'values')
			if len(data)<1:
				receiver=self.glb
			else:
				receiver=data[0]
			message = f'{receiver};{self.username}: {self.chat_box.get()}'
			self.client.send(message.encode('ascii'))
			self.chat_box.delete(0,END)
		except:
			pass


chat = chat_app()