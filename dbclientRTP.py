import rtpsocket
import sys

s = rtpsocket.Rtpsocket()

host, port = str(sys.argv[1]).split(':') #seperate host IP from the socket
port = int(port)

if len(sys.argv) > 2:					#make sure query is actually entered
	query = sys.argv[2:]
	query = str(query).replace("[", "")		#strip brackets and blank space from query
	query = query.replace("]", "")
	query = query.replace(" ", "")
	qlength = len(sys.argv[2:])
	query = str(qlength) + "+" + query	#attach length of query to front of query
else:
	print "Please enter a valid query"

s.connect(host, port)
s.send_s(s.connections[(host, port)], str(query))

gotresponse = False

while(not gotresponse):
	response = s.recv()
	if response is not None:
		gotresponse = True
		print response

sys.exit(1)