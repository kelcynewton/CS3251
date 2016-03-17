"""Server for the file transfer application."""
import argparse
import rtpsocket

parser = argparse.ArgumentParser(description='File transfer client.')

parser.add_argument("port", type=int, help="Port number to bind to.")
parser.add_argument("window", type=int, help="Window size of the server.")

args = parser.parse_args()

s = rtpsocket.Rtpsocket()
s.bind(args.port)
s.listen()

while(True):
    s.accept()
    cmd = 'get 3251.jpg'
    cmd_list = cmd.split(' ')

    if (len(cmd_list) == 2 and cmd_list[0] == 'get'):
        req_file = cmd_list[1]
    elif (len(cmd_list) == 3 and cmd_list[0] == 'get-post'):
        req_file = cmd_list[1]
        sent_file = cmd_list[2]
    else:
        s.send('Invalid command.')
        continue

    f = open(cmd_list[1], 'rb')
    s.send(f)
    f.close()

s.close()
