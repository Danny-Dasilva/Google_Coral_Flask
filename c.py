import socket
for i in range(10):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostname(), 1234))

    while True:
        msg = s.recv(8)
        print(msg.decode("utf-8"))