from tkinter import *
from tkinter import messagebox
from tkinter import ttk

class chat_app:
	"""docstring for chat_app"""
	def __init__(self):
		self.bg = '#081828'
		self.fg = '#00FF00'
		self.border='#000000'

		self.root = Tk()
		self.root.geometry('800x600')
		self.root.config(bg=self.bg)
		
		self.style = ttk.Style()
		self.style.theme_use("default")
		self.style.configure("Treeview", background=self.bg,fieldbackground=self.bg, foreground="white")
		self.style.map("Treeview")

		self.window()
		self.widgets()
		self.root.mainloop()

	def window(self):
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
		self.display = Text(self.display_area,bg=self.bg,fg=self.fg)
		self.scrollbar = Scrollbar(self.display_area,bg=self.bg)
		self.display.config(yscrollcommand=self.scrollbar.set)
		self.scrollbar.config(command=self.display.yview)
		self.scrollbar.pack(fill=Y,side=RIGHT)
		self.display.pack(fill=BOTH,expand=True)
		#CHAT AREA WIDGETS
		self.chat_box = Entry(self.chat_area,bg=self.bg,fg=self.fg,font=14)
		self.send_btn = Button(self.chat_area,bg=self.bg,fg=self.fg,text='send')
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

		self.users_list.bind("<Double-1>", self.OnDoubleClick)


	def add_user(self,user):
		ID,VALUE = user
		self.users_list.insert(parent='',index=ID,iid=ID,values=VALUE)

	def OnDoubleClick(self, event):
		item = self.users_list.selection()[0]
		print(item)
		#print("you clicked on", self.users_list.item(item,'values'))







myapp = chat_app()









































































































































































		