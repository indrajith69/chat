import threading
import socket

host = '127.0.0.1'
port = 5051

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((host,port))
server.listen()

clients = []
usernames = []


def broadcast(message):
	for client in clients:
		client.send(message)

def handle(client):
	while True:
		try:
			message = client.recv(1024)
			broadcast(message)
		except:
			index = clients.index(client)
			username = usernames[index]
			clients.remove(client)
			usernames.remove(username)
			client.close()

			broadcast(f'{username} has left the chat'.encode('ascii'))
			break

def receive():
	while True:
		client , address = server.accept()
		print(f'connected to [{str(address)}]')
		username = client.recv(1024).decode('ascii')

		usernames.append(username)
		clients.append(client)

		print(f'username is {username}')
		client.send('connected to the server\n'.encode('ascii'))
		broadcast(f'{username} joined the chat'.encode('ascii'))

		thread = threading.Thread(target=handle,args=(client,))
		thread.start()

receive()