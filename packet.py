import struct


# Header order: Src port, dest port, seqNum, type, window, checksum
HEADER_FORMAT = "!HHIIHHH"
# I = int, 4 bytes
# H = unsigned short, 2 bytes
# ! = network byte order

# Packet types:
# SYN = 1
# ACK = 2
# DATA = 4
# FIN = 8

class Packet:
	def __init__(self, header, data):
		self.head = header
		self.contents = data
		self.full = header + data

def calculate_checksum(data):
	i = len(data)

	# Handle the case where the length is odd
	if (i & 1):
		i -= 1
		sum = ord(data[i])
	else:
		sum = 0

    # Iterate through chars two by two and sum their byte values
	while i > 0:
		i -= 2
		sum += (ord(data[i + 1]) << 8) + ord(data[i])

    # Wrap overflow around
	sum = (sum >> 16) + (sum & 0xffff)

	result = (~ sum) & 0xffff  # One's complement
	result = result >> 8 | ((result & 0xff) << 8)  # Swap bytes
	return result


def create_packet(srcPort, destPort, seqNum, ackNum, pckType, window_size, data):
	header = struct.pack(HEADER_FORMAT, srcPort, destPort, seqNum, ackNum, pckType, window_size, 0)

	# calculate checksum before adding it to the header
	checkSum = calculate_checksum(header + data)

	# put checksum in header
	header = struct.pack(HEADER_FORMAT, srcPort, destPort, seqNum, ackNum, pckType, window_size, checkSum)

	# create an actual packet with header and data
	returnPacket = Packet(header, data)
	return returnPacket

def split_packet(Packet):
	pkt_src, pkt_dest, pkt_seqNum, pkt_ackNum, pkt_type, pkt_window, pkt_checksum = struct.unpack(HEADER_FORMAT, Packet.head)

	pkt_contents = Packet.contents

	return pkt_src, pkt_dest, pkt_seqNum, pkt_ackNum, pkt_type, pkt_window, pkt_checksum, pkt_contents


print "starting test"
data = "Hello my name is Stefan"
mypkt = create_packet(1342, 8080, 34893243, 21492018, 16, 25, data)
print mypkt.head
print mypkt.contents
print mypkt.full

source, dest, seq, ack, typ, window, csum, data = split_packet(mypkt)
print source
print dest
print seq
print ack
print typ
print window
print csum
print data

