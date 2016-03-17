"""Client for the file transfer application."""
import argparse
import rtpsocket

parser = argparse.ArgumentParser(description='File transfer client.')

parser.add_argument("ip", type=str, help="IP Address and Port")
parser.add_argument("window", type=int, help="Window size of the server.")

args = parser.parse_args()

host, port = args.ip.split(':')

s = rtpsocket.Rtpsocket()
s.connect(host, int(port))

command = ''

while (command != 'disconnect'):
    command = raw_input('Command: ')

    cmd_list = command.split(' ')

    if (len(cmd_list) == 1 and cmd_list[0] == 'disconnect'):
        continue
    elif (len(cmd_list) == 2 and cmd_list[0] == 'get'):
        recv_file = cmd_list[1]
    elif (len(cmd_list) == 3 and cmd_list[0] == 'get-post'):
        recv_file = cmd_list[1]
        send_file = cmd_list[2]
    else:
        print(
            'Please input a command in one of the following formats:\n' +
            '\tdisconnect\n' +
            '\tget F\n' +
            '\tget-post F G'
        )


print('Disconnecting')
s.close()
