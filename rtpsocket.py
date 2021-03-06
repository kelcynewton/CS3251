import socket
import sys
from collections import deque
import packet
import connection
import threading
import random
import time

# "get shakespeare.txt"

# Packet types:
# SYN = 1
# ACK = 2
# SYNACK = 3
# DATA = 4
# FIN = 8
# FINACK = 10

MAX_TIMEOUT = 3

class Rtpsocket():
	def __init__(self, window):
		self.incomingConnections = deque() # queue of connections waiting to be accepted, SERVER ONLY
		self.closingConnections = deque() # queue of connections waiting to be closed, SERVER ONLY
		self.connections = {} # maps (IP addresses, port) tuple to connection objects
		self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #create udp socket to use
		self.timeout = self.udpSocket.settimeout(10)	# SET TIMEOUT
		self.host = '127.0.0.1' #local host
		self.port = random.randint(1000, 9000) #random port number between 1000 - 9000
		self.window = window
		self.send_threads = []

	def listen(self):
		listening = threading.Thread(target=self.listenThread)
		listening.setDaemon(True)  # Lets aplication still close on ctrl+c
		listening.start()

	def listenThread(self):
		while (True):
			try:
				data, address = self.udpSocket.recvfrom(1024)
			except socket.timeout:
				continue
			dest_IP = address[0]
			dest_port = address[1]

			if data is not None and address is not None:
				# print("data received from : " + str(address))
				arrived = packet.bytes_to_packet(data)
				pkt_src, pkt_dest, pkt_seqNum, pkt_ackNum, pkt_type, pkt_window, lastpacket, pkt_checksum, pkt_data = packet.split_packet(arrived)
				# print("received data : " + str(pkt_data))
				print("received seqNum : " + str(pkt_seqNum))
				print("received ackNum : " + str(pkt_ackNum))
				if ((dest_IP, dest_port) in self.connections.keys()):
					print("expectedSeq :", self.connections[(dest_IP, dest_port)].expectedSeq)
					print("expectedAck :", self.connections[(dest_IP, dest_port)].expectedAck)
				print("received type : " + str(pkt_type))

				if (pkt_type == 1):
					print('SYN')
				elif (pkt_type == 2):
					print('ACK')
				elif (pkt_type == 3):
					print('SYNACK')
				elif (pkt_type == 4):
					print('DATA')
				elif (pkt_type == 8):
					print('FIN')
				elif (pkt_type == 10):
					print('FINACK')

				# Drop out-of-order and corrupted packets
				# or pkt_checksum != packet.calculate_checksum(arrived.head + arrived.contents))
				if (pkt_type != 1 and pkt_type != 2 and pkt_seqNum != self.connections[address].expectedSeq):
					print("Out of Order")
					if (pkt_type == 4 and pkt_seqNum < self.connections[address].seqNum):
						print("LESS THAN")
						ack_packet = packet.create_packet(self.port, dest_port, self.connections[(dest_IP, dest_port)].seqNum - 1, pkt_seqNum, 2, self.connections[(dest_IP, dest_port)].window_size, b'0')
						self.udpSocket.sendto(packet.packet_to_bytes(ack_packet), (dest_IP, dest_port))
					continue

				if (pkt_type == 2 and pkt_ackNum != self.connections[address].expectedAck):
					print("ACK OOO")
					continue

				# IP address & port that hasn't been seen is trying to SYN, need to send synack & create new connection object
				if pkt_type == 1 and address not in self.connections.keys():
					print("SYN received!")
					newConnection = connection.Connection(self.port, dest_port, dest_IP, 0, pkt_seqNum, "nothing", self) #new connection with client that sent SYN
					print(newConnection)

					if isinstance(newConnection, connection.Connection):
						# print("Adding new connection to the table")
						self.connections[(newConnection.destIP, newConnection.destPort)] = newConnection

					if (self.window > pkt_window):
						print ("Changing window size from", self.window, "to", pkt_window)
						self.window = pkt_window
						self.connections[(newConnection.destIP, newConnection.destPort)].window_size = pkt_window

					synack = self.create_synack(dest_IP, dest_port)
					print("Sending SYNACK....")
					newConnection.expectedSeq += 1
					# print("Seqnum: " + str(self.connections[(dest_IP, dest_port)].seqNum))
					# self.udpSocket.sendto(packet.packet_to_bytes(synack), (dest_IP, dest_port))
					self.threaded_send(synack, (dest_IP, dest_port))

				# ACK for regular data packets needs to be added for server side, let's you know to move on to next packet in window
				if pkt_type == 2 and self.connections[address].connected == True:
					self.connections[address].expectedSeq += 1
					self.connections[address].ackReceived = True
					# print("data ack received")

				# ACK from packet that is trying to complete handshake
				if pkt_type == 2 and address in self.connections.keys() and self.connections[address].finReceived == False and self.connections[address].connected == False:
					# print(len(self.incomingConnections))
					self.incomingConnections.appendleft(self.connections[address]) #place connection object in queue for potential connections to be ACCEPTED
					self.connections[address].ackNum = pkt_seqNum
					self.connections[address].expectedSeq += 1
					self.connections[address].ackReceived = True
					# print(len(self.incomingConnections))
					print("Waiting to accept connection with: " + str(address))

				# ACK from connection that is closing, add it to the closing connection queue
				if pkt_type == 2 and self.connections[address].finReceived == True and self.connections[address] not in self.closingConnections:
					# print("final ack received, connection is ready to close")
					self.connections[address].ackReceived = True
					self.closingConnections.appendleft(self.connections[address]) #add connection that wants to fin to queue of closing connections

				# listening for data packets to automatically place them in the correct receive buffer, ALSO RESPOND WITH AN ACK
				if pkt_type == 4 and address in self.connections.keys():
					#not putting entire packet in receive, only the data
					self.connections[address].rcvBuff.appendleft(pkt_data)
					self.connections[address].expectedSeq += 1

					# when file transfer is complete, put a True in the receive buff to indicate
					if (lastpacket == 1):
						print("Last packet received!", lastpacket)
						self.connections[address].rcvBuff.appendleft(True)

					self.connections[address].ackNum = pkt_seqNum
					# self.connections[address].seqNum += 1
					# print("Data packet placed in appropriate receive buffer" + ", address: " + str(address))
					data_ack_packet = self.create_ack(dest_IP, dest_port)
					# print("Sending Data ack")
					# print("Seqnum: " + str(self.connections[(dest_IP, dest_port)].seqNum))
					# self.udpSocket.sendto(packet.packet_to_bytes(data_ack_packet), (dest_IP, dest_port))
					# self.threaded_send(data_ack_packet, (dest_IP, dest_port))
					self.send_no_timeout(data_ack_packet, (dest_IP, dest_port))

				# connection wants to close, send a finack in response, wait for the final ack
				if pkt_type == 8 and address in self.connections.keys():
					# print("FIN Received From: " + str(address))
					# print("Seqnum: " + str(self.connections[address].seqNum))
					self.connections[address].finReceived = True #set the fin received in connection to true
					self.connections[address].ackNum = pkt_seqNum
					# self.connections[address].seqNum += 1
					self.connections[address].expectedSeq += 1
					self.connections[address].expectedAck = self.connections[address].seqNum

					finack = self.create_finack_packet(dest_IP, dest_port)
					# self.udpSocket.sendto(packet.packet_to_bytes(finack), address) #send finack to the connection
					# self.threaded_send(finack, (dest_IP, dest_port))
					# print("Sending finack")
					# print("Seqnum: " + str(self.connections[(dest_IP, dest_port)].seqNum))

				# handle client side closing connection (receive finack, add to closing connections)
				if pkt_type == 10:
					self.connections[address].finReceived = True
					self.connections[address].ackReceived = True
					self.connections[address].ackNum = pkt_seqNum
					# self.connections[address].seqNum += 1
					ack_packet = self.create_ack(dest_IP, dest_port) #ack the finack so we can close
					# self.udpSocket.sendto(packet.packet_to_bytes(ack_packet), (dest_IP, dest_port))
					# self.threaded_send(ack_packet, (dest_IP, dest_port))
					self.send_no_timeout(ack_packet, (dest_IP, dest_port))
					# print("sending final ACK, going to close connection")
					# print("Seqnum: " + str(self.connections[address].seqNum))


	def bind(self, host, port):
		self.host = host
		self.port = port
		self.udpSocket.bind((host, port))
		# print("Socket bound to " + host + ":" + str(port))

	def accept(self):
		if len(self.incomingConnections) > 0:
			newConnect = self.incomingConnections.pop()
			dest_IP = newConnect.destIP
			dest_port = newConnect.destPort
			address = (dest_IP, dest_port)
			# self.connections[address].ackNum += 1
			# self.connections[address].seqNum += 1
			self.connections[address].connected = True
			print ("Connection accepted")
			return newConnect

	def connect(self, host, port):
		#create new connection object
		newConnection = connection.Connection(self.port, port, host, 0, 0, "Nothing yet", self) #data is literally nothing yet, seqnum and acknum 0

		self.connections[(host, port)] = newConnection #add new connection to connection dictionary

		syn_packet = self.create_syn_packet(host, port) #create syn packet

		print("Sending SYN to: " + host + ":" + str(port))
		# self.udpSocket.sendto(packet.packet_to_bytes(syn_packet), (host, port))
		self.threaded_send(syn_packet, (host, port))
		# print("Seqnum: " + str(self.connections[(host, port)].seqNum))

		synAck_received = False

		timeout_start = time.time()
		timeout = 1

		#we should be using timeout from instance variables
		while (not synAck_received and time.time() < (timeout_start + timeout)):
			synAck_packet, address = self.udpSocket.recvfrom(1024);
			synAck_packet = packet.bytes_to_packet(synAck_packet)

			if synAck_packet is not None:
				pkt_src, pkt_dest, pkt_seqNum, pkt_ackNum, pkt_type, pkt_window, lastpacket, pkt_checksum, data = packet.split_packet(synAck_packet)

				if pkt_type == 3 and pkt_src == port and pkt_ackNum == 0:
					print("SYNACK received!")
					print("Seqnum: " + str(pkt_seqNum))
					print("Acknum: " + str(pkt_ackNum))
					synAck_received = True


		if synAck_received:
			self.connections[(host, port)].ackReceived = True
			self.connections[(host, port)].ackNum = pkt_seqNum
			# self.connections[(host, port)].seqNum += 1
			print("Sending ACK....")
			# print("Seqnum: " + str(self.connections[(host, port)].seqNum))

			if (self.window > pkt_window):
				print ("Changing window size from", self.window, "to", pkt_window)
				self.window = pkt_window
				self.connections[address].window_size = pkt_window

			ack_packet = self.create_ack(host, port)
			self.connections[address].expectedSeq += 1
			# self.udpSocket.sendto(packet.packet_to_bytes(ack_packet), (host, port))
			# self.threaded_send(ack_packet, (host, port))
			self.send_no_timeout(ack_packet, (host, port))
			self.connections[(host, port)].connected = True
			return self.connections[(host, port)]

	def recv(self): #should only be called on client side, because i know that there is only 1 connection in the connection table
		address = list(self.connections.keys())[0]

		listening = threading.Thread(target=self.listenThread)
		listening.setDaemon(True)  # Lets aplication still close on ctrl+c
		listening.start()

		gotData = False

		while not gotData:
			if len(self.connections[address].rcvBuff) > 0:
				# print ("Got Data")
				gotData = True
				data = self.connections[address].rcvBuff.pop()

				return data


	def close(self):
		for connect in list(self.connections.values()):
			self.closingConnections.appendleft(connect)

			# connect.seqNum += 1
			connect.expectedAck = connect.seqNum
			fin = self.create_fin_packet(connect.destIP, connect.destPort)
			# self.udpSocket.sendto(packet.packet_to_bytes(fin), (connect.destIP, connect.destPort))
			self.threaded_send(fin, (connect.destIP,  connect.destPort), fin=True)
			print("sending FIN to ", connect.destIP, connect.destPort)
			print("Seqnum: " + str(connect.seqNum))
			self.clearConnection(connect)


	def clearConnection(self, connect):
		print("Clearing connection with:", connect.destIP, connect.destPort)
		address = (connect.destIP, connect.destPort)
		del self.connections[address]

	def create_syn_packet(self, host, port):
		# create SYN packet for part 1 of handshake, type is set to 1, use connection table to get seqnum, acknum, window size, no data yet
		syn_packet = packet.create_packet(self.port, port, self.connections[(host, port)].seqNum, self.connections[(host, port)].ackNum, 1, self.connections[(host, port)].window_size, b'0')
		return syn_packet

	def create_synack(self, host, port):
		# create a synack for part 2 of handshake, type is set to 3 to represent syn+ack, connection table to get all info
		synAck_packet = packet.create_packet(self.port, port, self.connections[(host, port)].seqNum, self.connections[(host, port)].ackNum, 3, self.connections[(host, port)].window_size, b'0')
		return synAck_packet

	def create_ack(self, host, port):
		# create ACK packet for part 3 of handshake, type is set to 2, use connection table to get seqnum, acknum, window size, no data yet
		ack_packet = packet.create_packet(self.port, port, self.connections[(host, port)].seqNum, self.connections[(host, port)].ackNum, 2, self.connections[(host,port)].window_size, b'0')
		return ack_packet

	def create_data_packet(self, host, port, data, lastpacket):
		# packet for data that will not require more than 1 packet to encapsulate, type set to 4
		data_packet = packet.create_packet(self.port, port, self.connections[(host, port)].seqNum, self.connections[(host, port)].ackNum, 4, self.connections[(host,port)].window_size, data, lastpacket)
		return data_packet

	def create_fin_packet(self, host, port):
		fin_packet = packet.create_packet(self.port, port, self.connections[(host, port)].seqNum, self.connections[(host, port)].ackNum, 8, self.connections[(host,port)].window_size, b'0')
		return fin_packet

	def create_finack_packet(self, host, port):
		finack = packet.create_packet(self.port, port, self.connections[(host, port)].seqNum, self.connections[(host, port)].ackNum, 10, self.connections[(host,port)].window_size, b'0')
		return finack

	def send_no_timeout(self, send_packet, address):
		connection = self.connections[address]
		connection.seqNum += 1
		self.udpSocket.sendto(packet.packet_to_bytes(send_packet), address)

	def send_timeout(self, send_packet, address, fin):
		connection = self.connections[address]
		connection.seqNum += 1
		while (True):
			self.udpSocket.sendto(packet.packet_to_bytes(send_packet), address)
			connection.timeout = False
			t = threading.Timer(MAX_TIMEOUT, connection.timeout_conn)
			t.start()
			while(not connection.timeout and not connection.ackReceived): #wait until timeout detected or we get something valid back
				if (fin and connectin.finReceived):
					break
				pass
				# DO NOTHING
			if (connection.timeout): #if we timed out before we got something back, resend the packet
				continue
			if(connection.ackReceived):
				t.cancel()
				break

	def threaded_send(self, send_packet, address, fin=False):
		t = threading.Thread(target=self.send_timeout, args=(send_packet, address, fin))
		t.setDaemon(True)
		t.start()
		return t
