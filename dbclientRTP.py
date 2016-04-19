"""DB Client TCP executable."""
import argparse
import rtpsocket

# Utilize argparse to take in command line arguments.
parser = argparse.ArgumentParser()

parser.add_argument("ip", type=str, help="IP Address and Port")
parser.add_argument("key", type=int, help="GTID numbers")
parser.add_argument('fields', nargs='*', help="Data fields")
args = parser.parse_args()

# Split ip into host and port
if ':' not in args.ip:
    print('Error: Input ip as a IP:PORT pair.')
    exit(1)

parts = args.ip.split(':')
host = parts[0]
port = int(parts[1])

# Combine the key and the query and concatenate to form the query string.
query = []
query.append(str(args.key))
query.extend(args.fields)
query_str = ' '.join(query)


# Create the socket and connect to the server passed in.
socket = rtpsocket.Rtpsocket()
connection = socket.connect(host, port)
socket.listen()



# Try to send the query and receive the response.
connection.send(query_str.encode('utf-8'))
response = connection.recv()
response_str = response.decode('utf-8')
print('Server response: {}'.format(response_str))
