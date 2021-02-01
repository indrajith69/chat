import socket
import threading

host = '127.0.0.1'
port = 5051

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect((host,port))

username = input('enter your username :')
client.send(username.encode('ascii'))

def receive():
	while True:
		try:
			message = client.recv(1024).decode('ascii')
			print(message)
		except Exception as e:
			print(e)
			client.close()
			break

def write():
	while True:
		message = f'{username}: {input("")}'
		client.send(message.encode('ascii'))


write_thread   = threading.Thread(target=write)
receive_thread = threading.Thread(target=receive)

write_thread.start()
receive_thread.start()