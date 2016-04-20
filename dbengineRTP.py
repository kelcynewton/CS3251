"""TCP implementation of the server."""
import argparse
import re
from time import sleep
import rtpsocket

import student_data

parser = argparse.ArgumentParser()
data = student_data.data
valid_fields = student_data.valid_fields

# Parse Arguments: python dbengineTCP.py PORT
parser.add_argument("port", type=int, help="Port number")
args = parser.parse_args()

# Create TCP socket and bind to the passed port.
socket = rtpsocket.Rtpsocket(1)
print("Server started")

socket.bind('', args.port)
print("Server bound to port: {}".format(args.port))


# Set the socket to listen for incoming connections.
socket.listen()

while True:
    connection = None

    while connection is None:
      connection = socket.accept()

    client_msg = connection.recv()
    client_str = client_msg.decode('utf-8')
    client_str = re.sub("[^a-zA-Z\d_ ]", "", client_str)

    # Split the query string into the key and fields
    query = client_str.split(' ')
    message = ''
    key = ''
    fields = ''
    error = False

    # Check that the first part of the query is a key matching an id number.
    if (re.match(r'\d{9}', query[0])):
        key = query[0]
        fields = query[1:]
    else:
        error = True
        message = 'Malformed key'

    # Check if each of the remaining fields is a valid field to search for.
    if (not error):
        for field in fields:
            if (field not in valid_fields):
                error = True
                message = '{} is not a valid field'.format(field)
                break

    # Finally, use they key to look up the record and build a response.
    if (not error):
        if (key in data):
            results = []
            for field in fields:
                results.append('{}: {}'.format(field, data[key][field]))
            message = ', '.join(results)
        else:
            error = True
            message = '{} was not found'.format(key)

    # Send the response back to the client.
    print('Response: {}'.format(message))
    connection.send(message.encode('utf-8'))

    # Close the socket that is bound to the connected client.
    connection.close()

server.close()
