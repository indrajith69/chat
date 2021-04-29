import socket
import pickle
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
		self.current_chat = self.glb

		self.root = Tk()
		self.root.config(bg=self.bg)
		self.style = ttk.Style()
		self.style.theme_use("default")
		self.style.configure("Treeview", background=self.bg,fieldbackground=self.bg, foreground="white")
		self.style.map("Treeview")
		self.root.protocol("WM_DELETE_WINDOW",self.close_connection)

		self.connection_info()
		self.root.mainloop()

	def close_connection(self):
		if self.client_running:
			self.client_running = False
			self.client.send(pickle.dumps(('<<exit>>','')))
			#self.client.close()
		self.root.destroy()

	def clear(self,frame):
		for widget in frame.winfo_children():
			widget.destroy()

	def add_user(self,user):
		ID,VALUE = user
		self.users_list.insert(parent='',index=ID,iid=ID,values=VALUE)


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
		self.btn_set = Button(self.root,bg=self.bg,fg=self.fg,text='okay',command=self.start_connection)

		self.label_ip.pack(fill=BOTH,side=TOP)
		self.label_username.pack(fill=BOTH,side=TOP)
		self.entry_ip.pack(fill=X)
		self.entry_username.pack(fill=X)
		self.btn_set.pack(fill=X,side=BOTTOM)
		self.frame_widgets.pack(fill=BOTH,side=BOTTOM,expand=True)
		self.frame_ip.pack(fill=BOTH,side=LEFT,expand=True)
		self.frame_port.pack(fill=BOTH,side=RIGHT,expand=True)

	def start_connection(self):
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
			self.client.send('okay'.encode('ascii'))
		else:
			messagebox.showwarning('connection error',f'username unavailable\n{status}')
			self.close_connection()
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

	def update_users(self,users):
		users.remove(self.username)
		self.users_list.delete(*self.users_list.get_children())
		self.add_user((0,'global'))
		for user in users:
			self.add_user((users.index(user)+1,user))
		self.users = users

	def message(self,data):
		sender,receiver,message = data
		if receiver==self.current_chat and receiver==self.glb:
			self.display.delete('1.0',END)
			self.display.insert(END,message)
		elif (sender==self.username and receiver==self.current_chat) or (sender==self.current_chat and receiver==self.username):
			self.display.delete('1.0',END)
			self.display.insert(END,message)
	def onselect(self, event):
		try:
			user = self.users_list.selection()[0]
			self.current_chat = self.users_list.item(user,'values')[0]
			data = pickle.dumps(('<<view>>',[self.username,self.current_chat]))
			self.client.send(data)
		except:
			data = pickle.dumps(('<<view>>',[self.username,self.glb]))
			self.client.send(data)


	def recv(self):
		while True and self.client_running:
			message,data = pickle.loads(self.client.recv(1024))
			if message=="<<update>>":
				self.update_users(data)
			elif message=="<<message>>":
				self.message(data)
			elif message=="<<exit>>":
				self.client.close()
				break	

	def write(self):
		#try:
			#self.client.send('<<message>>'.encode('ascii'))
		selected = self.users_list.focus()
		user = self.users_list.item(selected,'values')
		if not len(user):
			receiver=self.glb
		else:
			receiver=user[0]
		sender = self.username
		message = self.chat_box.get()
		data = pickle.dumps(('<<message>>',[sender,receiver,message]))
		self.chat_box.delete(0,END)
		self.client.send(data)
		#except Exception as err:
			#print(err)



chat = chat_app()