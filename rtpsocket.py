import socket
import sys
import Queue
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
		self.incomingConnections = Queue.Queue()

		# maps IP addresses to connection objects
		self.connections = {}
		self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #create udp socket to use
		self.timeout = self.udpSocket.settimeout(10)	# SET TIMEOUT
		self.host = '127.0.0.1' #local host
		self.port = random.randint(1000, 9000) #random port number between 1000 - 9000

	def listen(self):
		print "Listen called"
		listening = threading.Thread(target=self.listenThread)
		listening.start()

	def listenThread(self):
		print "Listen Thread Started"
		while (True):
			data, address = self.udpSocket.recvfrom(1024)
			dest_IP = address[0]
			dest_port = address[1]

			if data is not None and address is not None:
				print "data received from: " + str(address)
				arrived = packet.bytes_to_packet(data)
				pkt_src, pkt_dest, pkt_seqNum, pkt_ackNum, pkt_type, pkt_window, pkt_data = packet.split_packet(arrived)
				print "data received: " + pkt_data

			# IP address & port that hasn't been seen is trying to SYN, need to send synack & create new connection object
			if data is not None and pkt_type == 1 and address not in self.connections.keys():
				print "SYN received!"
				newConnection = connection.Connection(self.port, dest_port, dest_IP, 0, pkt_seqNum, "nothing") #new connection with client that sent SYN
				self.connections[address] = newConnection
				synack = self.create_synack(dest_IP, dest_port)
				print "Sending SYNACK..."
				self.udpSocket.sendto(packet.packet_to_bytes(synack), (dest_IP, dest_port))

			if data is not None and pkt_type == 2 and address in self.connections.keys():
				self.incomingConnections.put((data, address))


	def bind(self, host, port):
		self.host = host
		self.port = port
		self.udpSocket.bind((host, port))
		print("Socket bound to " + host + ":" + str(port))

	def accept():
		print "Trying to accept a connection"
		if not self.incomingConnections.empty():
			data, address = self.incomingConnections.get()

			pkt_src, pkt_dest, pkt_seqNum, pkt_ackNum, pkt_type, pkt_window, pkt_data = split_packet(data)

			self.connections[address].ackNum = pkt_seqNum
			self.connections[address].seqNum += 1
			self.connections[address] = True
			print "Connection established with: " + address

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

	def close(self):
		print "nice"

	def create_syn_packet(self, host, port):
		# create SYN packet for part 1 of handshake, type is set to 1, use connection table to get seqnum, acknum, window size, no data yet
		syn_packet = packet.create_packet(self.port, port, self.connections[(host, port)].seqNum, self.connections[(host, port)].ackNum, 1, self.connections[(host, port)].window_size, "Kelcy")
		return syn_packet

	def create_synack(self, host, port):
		# create a synack for part 2 of handshake, type is set to 3 to represent syn+ack, connection table to get all info
		synAck_packet = packet.create_packet(self.port, port, self.connections[(host, port)].seqNum, self.connections[(host, port)].ackNum, 3, self.connections[(host, port)].window_size, "Stefan")
		return synAck_packet

	def create_ack(self, host, port):
		# create ACK packet for part 3 of handshake, type is set to 2, use connection table to get seqnum, acknum, window size, no data yet
		ack_packet = packet.create_packet(self.port, port, self.connections[(host, port)].seqNum, self.connections[(host, port)].ackNum, 2, self.connections[(host,port)].window_size, "Drew")
		return ack_packet



