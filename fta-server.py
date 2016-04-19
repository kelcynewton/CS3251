"""Server for the file transfer application."""
import argparse
import rtpsocket
import time
import threading
import os


def recv_file(name, connection):
    TIMEOUT = 5
    t_start = time.time()
    print ("Entering post file")
    name = "post_" + name
    if os.path.exists(name):
        os.remove(name)
    while (time.time() - t_start < TIMEOUT):
        print ("Receive loop entered")
        data = connection.recv()
        if (data is not None and data is not True):
            with open(name, 'ba') as f:
                f.write(data)
            t_start = time.time()
        elif (data is True):
            print ("Leaving loop")
            return

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
        cmd = b''

        while (True):
            temp = c.recv()
            if (temp == True):
                break
            else:
                cmd += temp

        cmd = cmd.decode()

        print('SERVER: ', cmd)

        cmd_list = cmd.split(' ')

        print('SERVER: ', cmd_list)

        if (len(cmd_list) == 2 and cmd_list[0] == 'get'):
            req_file = cmd_list[1]
            with open(req_file, 'rb') as f: #open file with wb
                data = f.read()
                print('SERVER: Sending')
                c.send(data)
                print('SERVER: Sent')
        elif (len(cmd_list) == 3 and cmd_list[0] == 'get-post'):
            req_file = cmd_list[1]
            sent_file = cmd_list[2]
            threading.Thread(target=recv_file, args=(sent_file, c)).start()
            with open(req_file, 'rb') as f:
                data = f.read()
                print('SERVER: Sending ')
                c.send(data)
                print('SERVER: Sent')
        else:
            print('SERVER: Invalid command.')
            c.send('Invalid command.')

        cmd = None

s.close()
