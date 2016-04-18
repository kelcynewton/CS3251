"""Server for the file transfer application."""
import argparse
import rtpsocket
import time
import threading


def recv_file(name, connection):
    TIMEOUT = 3
    t_start = time.time()

    while (time.time() - t_start < TIMEOUT):
        data = connection.recv()
        if (data):
            with open(name, 'wba') as f:
                f.write(data)
            t_start = time.time()

parser = argparse.ArgumentParser(description='File transfer client.')

parser.add_argument("port", type=int, help="Port number to bind to.")
parser.add_argument("window", type=int, help="Window size of the server.")

args = parser.parse_args()

s = rtpsocket.Rtpsocket()
s.bind('', args.port)
s.listen()

while(True):

    c = None
    while (c is None):
        c = s.accept()

    print("SERVER: Connection established.")

    cmd = None

    while (c.connected):
        cmd = c.recv()
        if (cmd is True):
            cmd = None
            continue
        cmd = cmd.decode()

        print('SERVER: ', cmd)

        cmd_list = cmd.split(' ')

        print('SERVER: ', cmd_list)

        if (len(cmd_list) == 2 and cmd_list[0] == 'get'):
            req_file = cmd_list[1]
            with open(req_file, 'rb') as f: #open file with wb
                data = f.read()
                print('SERVER: Sending ', str(data))
                c.send(data)
                print('SERVER: Send')
        elif (len(cmd_list) == 3 and cmd_list[0] == 'get-post'):
            req_file = cmd_list[1]
            sent_file = cmd_list[2]
            with open(req_file, 'rb') as f:
                data = f.read()
                print('SERVER: Sending ', str(data))
                c.send(data)
                print('SERVER: Send')
            threading.Thread(target=recv_file, args=(sent_file, c))
        else:
            print('SERVER: Invalid command.')
            c.send('Invalid command.')

        cmd = None

s.close()
