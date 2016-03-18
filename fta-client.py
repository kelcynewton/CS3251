"""Client for the file transfer application."""
import argparse
import rtpsocket
import threading
import time


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

parser.add_argument("ip", type=str, help="IP Address and Port")
parser.add_argument("window", type=int, help="Window size of the server.")

args = parser.parse_args()

host, port = args.ip.split(':')

s = rtpsocket.Rtpsocket()
c = s.connect(host, int(port))

command = ''

while (command != 'disconnect'):
    command = raw_input('Command: ')

    cmd_list = command.split(' ')

    if (len(cmd_list) == 1 and cmd_list[0] == 'disconnect'):
        continue
    elif (len(cmd_list) == 2 and cmd_list[0] == 'get'):
        recv_name = cmd_list[1]
        c.send(' '.join(cmd_list[0:2]))

        threading.Thread(target=recv_file, args=(recv_name, c))
    elif (len(cmd_list) == 3 and cmd_list[0] == 'get-post'):
        recv_name = cmd_list[1]
        send_name = cmd_list[2]

        c.send(' '.join(cmd_list[0:3]))

        with open(send_name, 'wb') as f:
            data = f.read()
            c.send(data)

        threading.Thread(target=recv_file, args=(recv_name, c))
    else:
        print(
            'Please input a command in one of the following formats:\n' +
            '\tdisconnect\n' +
            '\tget F\n' +
            '\tget-post F G'
        )


print('Disconnecting')
s.close()
