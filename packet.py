import struct
import io
import ctypes
import pickle

# Header order: Src port, dest port, seqNum, type, window, checksum
HEADER_WITHOUT_CHECK = "!HHIIHH"
HEADER_FORMAT = "!HHIIHHH" #add H back for checksum, use above format without checksum
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
	def __init__(self, header, data): #, checkSum):
		self.head = header
		self.contents = data
		# self.checkSum = checkSum

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
	header = struct.pack(HEADER_WITHOUT_CHECK, srcPort, destPort, seqNum, ackNum, pckType, window_size)

	# calculate checksum before adding it to the header
	checkSum = calculate_checksum(header + data)

	# put checksum in header if it ever works
	header = struct.pack(HEADER_FORMAT, srcPort, destPort, seqNum, ackNum, pckType, window_size, checkSum)

	# create an actual packet with header and data and checkSum eventually
	returnPacket = Packet(header, data)
	return returnPacket

def packet_to_bytes(Packet):
    byteString = pickle.dumps(Packet)
    return byteString
	# byteString = bytearray()
	# pkt_src, pkt_dest, pkt_seqNum, pkt_ackNum, pkt_type, pkt_window, pkt_checkSum, pkt_data = split_packet(Packet) #checksum omitted
	# byteString.extend(bytearray(_uint16(pkt_src)))
	# byteString.extend(bytearray(_uint16(pkt_dest)))
	# byteString.extend(bytearray(_uint32(pkt_seqNum)))
	# byteString.extend(bytearray(_uint32(pkt_ackNum)))
	# byteString.extend(bytearray(_uint16(pkt_type)))
	# byteString.extend(bytearray(_uint16(pkt_window)))
	# byteString.extend(bytearray(_uint16(pkt_checkSum))) # check sum stuff
	# byteString.extend(bytearray(pkt_data, 'utf-8'))

def bytes_to_packet(bytestream):
    reassembled_packet = pickle.loads(bytestream)
    return reassembled_packet
	# pkt_src = _uint16.from_buffer(bytearray(bytestream[0:2])).value
	# pkt_dest = _uint16.from_buffer(bytearray(bytestream[2:4])).value
	# pkt_seqNum = _uint32.from_buffer(bytearray(bytestream[4:8])).value
	# pkt_ackNum = _uint32.from_buffer(bytearray(bytestream[8:12])).value
	# pkt_type = _uint16.from_buffer(bytearray(bytestream[12:14])).value
	# pkt_window = _uint16.from_buffer(bytearray(bytestream[14:16])).value
	# pkt_checkSum = _uint16.from_buffer(bytearray(bytestream[16:18])).value # check sum stuff
	# pkt_data = bytearray.decode(bytearray(bytestream[18:])) #switch to 18 when adding checksum back, otherwise 16

	# reassembled = create_packet(pkt_src, pkt_dest, pkt_seqNum, pkt_ackNum, pkt_type, pkt_window, pkt_data)

def split_packet(Packet):
	pkt_src, pkt_dest, pkt_seqNum, pkt_ackNum, pkt_type, pkt_window, check_sum = struct.unpack(HEADER_FORMAT, Packet.head)

	pkt_contents = Packet.contents

	return pkt_src, pkt_dest, pkt_seqNum, pkt_ackNum, pkt_type, pkt_window, check_sum, pkt_contents # return checksum before contents
