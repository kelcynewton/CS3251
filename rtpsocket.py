import socket
import sys
from collections import deque
import packet
import connection
import threading
import random
import time

# Packet types:
# SYN = 1
# ACK = 2
# SYNACK = 3
# DATA = 4
# FIN = 8

class Rtpsocket():	
	def __init__(self):
		self.incomingConnections = deque() # queue of connections waiting to be accepted, SERVER ONLY
		self.closingConnections = deque() # queue of connections waiting to be closed, SERVER ONLY
		self.connections = {} # maps (IP addresses, port) tuple to connection objects
		self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #create udp socket to use
		self.timeout = self.udpSocket.settimeout(10)	# SET TIMEOUT
		self.host = '127.0.0.1' #local host
		self.port = random.randint(1000, 9000) #random port number between 1000 - 9000

	def listen(self):
		listening = threading.Thread(target=self.listenThread)
		listening.start()

	def listenThread(self):
		while (True):
			data, address = self.udpSocket.recvfrom(1024)
			dest_IP = address[0]
			dest_port = address[1]

			if data is not None and address is not None:
				print "data received from: " + str(address)
				arrived = packet.bytes_to_packet(data)
				pkt_src, pkt_dest, pkt_seqNum, pkt_ackNum, pkt_type, pkt_window, pkt_data = packet.split_packet(arrived)
				print "data received: " + pkt_data
				print "seqNum: " + str(pkt_seqNum)
				print "ackNum: " + str(pkt_ackNum)
				print "type: " + str(pkt_type)

				# IP address & port that hasn't been seen is trying to SYN, need to send synack & create new connection object
				if pkt_type == 1 and address not in self.connections.keys():
					print "SYN received!"
					newConnection = connection.Connection(self.port, dest_port, dest_IP, 0, pkt_seqNum, "nothing") #new connection with client that sent SYN
					print newConnection
					if isinstance(newConnection, connection.Connection):
						print "Adding new connection to the table"
						self.connections[(newConnection.destIP, newConnection.destPort)] = newConnection
						print self.connections
					synack = self.create_synack(dest_IP, dest_port)
					print "Sending SYNACK..."
					self.udpSocket.sendto(packet.packet_to_bytes(synack), (dest_IP, dest_port))

				if pkt_type == 2 and address in self.connections.keys():
					print self.connections[address]
					self.incomingConnections.appendleft(self.connections[address]) #place connection object in queue for potential connections
					print "Waiting to accept connection with: " + str(address)

				# listening for data packets to automatically place them in the correct receive buffer
				if pkt_type == 4 and address in self.connections.keys():
					#not putting entire packet in receive, only the data because it wasn't working otherwise
					self.connections[address].rcvBuff.appendleft(pkt_data)
					print "Data packet placed in appropriate receive buffer, data: " + pkt_data + ", address: " + str(address)


	def bind(self, host, port):
		self.host = host
		self.port = port
		self.udpSocket.bind((host, port))
		print("Socket bound to " + host + ":" + str(port))

	def accept(self):
		if len(self.incomingConnections) > 0:
			newConnect = self.incomingConnections.pop()

			print type(newConnect)

			dest_IP = newConnect.destIP
			dest_port = newConnect.destPort
			address = (dest_IP, dest_port)
			self.connections[address].ackNum += 1
			self.connections[address].seqNum += 1
			self.connections[address].connected = True
			return newConnect


	def connect(self, host, port):
		#create new connection object
		newConnection = connection.Connection(self.port, port, host, 0, 0, "Nothing yet") #data is literally nothing yet, seqnum and acknum 0
		
		self.connections[(host, port)] = newConnection #add new connection to connection dictionary

		syn_packet = self.create_syn_packet(host, port) #create syn packet

		print "Sending SYN to: " + host + ":" + str(port)
		self.udpSocket.sendto(packet.packet_to_bytes(syn_packet), (host, port))

		synAck_received = False

		timeout_start = time.time()
		timeout = 1
		
		#we should be using timeout from instance variables
		while (not synAck_received and time.time() < (timeout_start + timeout)):
			synAck_packet, address = self.udpSocket.recvfrom(2048);
			synAck_packet = packet.bytes_to_packet(synAck_packet)

			if synAck_packet is not None:
				pkt_src, pkt_dest, pkt_seqNum, pkt_ackNum, pkt_type, pkt_window, data = packet.split_packet(synAck_packet)

				if pkt_type == 3 and pkt_src == port and pkt_ackNum == 0:
					print "SYNACK received! Data: " + data
					print "seqNum: " + str(pkt_seqNum)
					print "ackNum: " + str(pkt_ackNum)
					synAck_received = True
					self.connections[(host, port)].ackNum = pkt_seqNum
			else:
				self.udpSocket.sendto(syn_packet, (host, port))

				
		if synAck_received:
			self.connections[(host, port)].seqNum += 1
			print "Sending ACK...."
			ack_packet = self.create_ack(host, port)
			self.udpSocket.sendto(packet.packet_to_bytes(ack_packet), (host, port))
			self.connections[(host, port)].connected = True

	def send_s(self, connect, data):
		connectionHost = connect.destIP
		connectionPort = connect.destPort
		connectionSeq = connect.seqNum
		isconnected = connect.connected
		print str(connectionHost)
		print str(connectionPort)
		print str(connectionSeq)
		print str(isconnected)

		print type(connect)

		isValid = False

		if ((str(connectionHost), connectionPort) in self.connections.keys()):
			print "keys match"
			print len(self.connections.values())

		if isinstance(self.connections[(str(connectionHost), connectionPort)], connection.Connection):
			print "Valid connection"
			isValid = True
			self.connections[(str(connectionHost), connectionPort)].seqNum += 1
		
		data_packet = self.create_data_packet(connectionHost, connectionPort, data)
		connect.sndBuff.put(data_packet)
		sending = threading.Thread(target=self.sendThread)
		sending.start()

	def sendThread(self):
		for address, connect in self.connections.items():
			if not connect.sndBuff.empty() and connect.connected:
				data_packet = connect.sndBuff.get()
				self.udpSocket.sendto(packet.packet_to_bytes(data_packet), address)
				print "attempting to send data packet containing: " + str(data_packet.contents)

	def recv(self):
		data, address = self.udpSocket.recvfrom(1024)
		dest_IP = address[0]
		dest_port = address[1]

		if data is not None and address is not None:
				print "data received from: " + str(address)
				arrived = packet.bytes_to_packet(data)
				pkt_src, pkt_dest, pkt_seqNum, pkt_ackNum, pkt_type, pkt_window, pkt_data = packet.split_packet(arrived)

				return pkt_data


	# def close(self):
	# 	for connect in self.connections.values():
	# 		fin = create_fin_packet(connect.destIP, connect.destPort)
	# 		self.udpSocket.sendto(packet.packet_to_bytes(fin), (connect.destIP, connect.destPort))


	def create_syn_packet(self, host, port):
		# create SYN packet for part 1 of handshake, type is set to 1, use connection table to get seqnum, acknum, window size, no data yet
		syn_packet = packet.create_packet(self.port, port, self.connections[(host, port)].seqNum, self.connections[(host, port)].ackNum, 1, self.connections[(host, port)].window_size, "SYN")
		return syn_packet

	def create_synack(self, host, port):
		# create a synack for part 2 of handshake, type is set to 3 to represent syn+ack, connection table to get all info
		synAck_packet = packet.create_packet(self.port, port, self.connections[(host, port)].seqNum, self.connections[(host, port)].ackNum, 3, self.connections[(host, port)].window_size, "SYNACK")
		return synAck_packet

	def create_ack(self, host, port):
		# create ACK packet for part 3 of handshake, type is set to 2, use connection table to get seqnum, acknum, window size, no data yet
		ack_packet = packet.create_packet(self.port, port, self.connections[(host, port)].seqNum, self.connections[(host, port)].ackNum, 2, self.connections[(host,port)].window_size, "ACK")
		return ack_packet

	def create_data_packet(self, host, port, data):
		# packet for data that will not require more than 1 packet to encapsulate, type set to 4
		data_packet = packet.create_packet(self.port, port, self.connections[(host, port)].seqNum, self.connections[(host, port)].ackNum, 4, self.connections[(host,port)].window_size, data)
		return data_packet

	def create_fin_packet(self, host, port):
		fin_packet = packet.create_packet(self.port, port, self.connections[(host, port)].seqNum, self.connections[(host, port)].ackNum, 8, self.connections[(host,port)].window_size, "FIN")
		return fin_packet

