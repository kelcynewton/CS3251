import rtpsocket
import sys
import connection
import socket
import time

s = rtpsocket.Rtpsocket()
host = '127.0.0.1'
students = {'903076259':['Anthony', 'Peterson', 231, 63, float(231/63.0)],
		'903084074':['Richard', 'Harris', 236, 66, float(236/66.0)],
		'903077650':['Joe', 'Miller', 224, 65, float(224/65.0)],
		'903083691':['Todd', 'Collins', 218, 56, float(218/56.0)],
		'903082265':['Laura', 'Stewart', 207, 64, float(207/64.0)],
		'903075951':['Marie', 'Cox', 246, 63, float(246/63.0)],
		'903084336':['Stephen', 'Baker', 234, 66, float(234/66.0)]
												}   #create database (dictionary)
if (len(sys.argv) == 2): #check to make sure only 1 argument after executable
    port = int(sys.argv[1])
else:
    print "Please enter only the port number you wish to use after the program executable"


 
s.bind(host, port) #bind the host ip with the port if it's valid
s.listen()

findConnection = False

while(not findConnection):
	c = s.accept()
	if isinstance(c, connection.Connection):
		findConnection = True
		query = c.recv()
		print query

		qlength, query = query.split("+") #get length of query and query

		response = "Server response: "
	    	validq = 0  #help check if only has valid headers

	    	if str(query[1:10]) in students.keys(): #make sure student id is valid before continuing query
			if ('first_name' in query):
				response = response + "first_name: " + students[query[1:10]][0] + ", "
				validq += 1 #increment valid query count
			if ('last_name' in query):
				response = response + "last_name: " + students[query[1:10]][1] + ", "
				validq += 1
			if ('quality_points' in query):
				response = response + "quality_points: " + str(students[query[1:10]][2]) + ", "
				validq += 1
			if ('gpa_hours' in query):
				response = response + "gpa_hours: " + str(students[query[1:10]][3]) + ", "
				validq += 1
			if ('gpa' in query):
				response = response + "gpa: " + str(students[query[1:10]][4])
				validq += 1
			if validq != 0 and validq == (int(qlength) - 1): #check if attempted query is valid, any typo will fail this condition
				print response
				c.send_s(response)
	time.sleep(1)

print "done"
sys.exit(1)