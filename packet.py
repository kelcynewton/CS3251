import struct
import io
import ctypes
import pickle

# Header order: Src port, dest port, seqNum, type, window, lastpacket, checksum
HEADER_WITHOUT_CHECK = "!HHIIHHI"
HEADER_FORMAT = "!HHIIHHIH" #add H back for checksum, use above format without checksum
# I = int, 4 bytes
# H = unsigned short, 2 bytes
# ! = network byte order

# Packet types:
# SYN = 1
# ACK = 2
# DATA = 4
# FIN = 8

_uint16 = ctypes.c_uint16
_uint32 = ctypes.c_uint32
string = ctypes.c_char_p

class Packet:
	def __init__(self, header, data, lastpacket=0):
		self.head = header
		self.contents = data
		self.lastpacket = lastpacket
		# self.checkSum = checkSum

def calculate_checksum(data):
	# i = len(data)
	#
	# # Handle the case where the length is odd
	# if (i & 1):
	# 	i -= 1
	# 	sum = ord(data[i])
	# else:
	# 	sum = 0
	#
    # # Iterate through chars two by two and sum their byte values
	# while i > 0:
	# 	i -= 2
	# 	sum += (ord(data[i + 1]) << 8) + ord(data[i])
	#
    # # Wrap overflow around
	# sum = (sum >> 16) + (sum & 0xffff)
	#
	# result = (~ sum) & 0xffff  # One's complement
	# result = result >> 8 | ((result & 0xff) << 8)  # Swap bytes

	b = bytearray(data)

	result = sum(b) % 65535
	return result


def create_packet(srcPort, destPort, seqNum, ackNum, pckType, window_size, data, lastpacket=0):

	header = struct.pack(HEADER_WITHOUT_CHECK, srcPort, destPort, seqNum, ackNum, pckType, window_size, lastpacket)

	# calculate checksum before adding it to the header
	checkSum = calculate_checksum(header + data)

	# put checksum in header if it ever works
	header = struct.pack(HEADER_FORMAT, srcPort, destPort, seqNum, ackNum, pckType, window_size, lastpacket, checkSum)

	# create an actual packet with header and data and checkSum eventually
	returnPacket = Packet(header, data, lastpacket)
	return returnPacket

def packet_to_bytes(Packet):
    byteString = pickle.dumps(Packet)
    return byteString

def bytes_to_packet(bytestream):
    reassembled_packet = pickle.loads(bytestream)
    return reassembled_packet

def split_packet(packet):
	pkt_src, pkt_dest, pkt_seqNum, pkt_ackNum, pkt_type, pkt_window, lastpacket, check_sum = struct.unpack(HEADER_FORMAT, packet.head)

	pkt_contents = packet.contents

	return pkt_src, pkt_dest, pkt_seqNum, pkt_ackNum, pkt_type, pkt_window, lastpacket, check_sum, pkt_contents # return checksum before contents
