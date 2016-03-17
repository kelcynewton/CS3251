import packet
import Queue
import time
from collections import deque

# Packet types:
# SYN = 1
# ACK = 2
# DATA = 4
# FIN = 8

class Connection():
    def __init__(self, sourcePort, destPort, destIP, seqNum, ackNum, data):
        self.src = sourcePort
        self.destPort = destPort
        self.destIP = destIP
        self.window_size = 1
        self.seqNum = seqNum
        self.ackNum = ackNum
        self.data = data
        self.rcvBuff = deque()
        self.sndBuff = Queue.Queue()
        self.connected = False



    def recv(self):
        time.sleep(1)
        if len(self.rcvBuff) > 0:
            pkt_data = self.rcvBuff.pop()
            return pkt_data

#later add in dynamic receiver window, for now window is 1 packet



def generate_packets(data, packet_size): #loop through the file and split it at intervals

    # #read the contents of the file
    # f = open(f, 'rb')
    # data = f.read() # read the entire content of the file
    # f.close()

    # # get the length of data, ie size of the input file in bytes
    # bytes = len(data)

    # #calculate the number of packets to be created
    # numPackets= bytes/packet_size
    # if(bytes%packet_size):
    #     numPackets+=1

    numBytes = len(data)
    numPackets = numBytes/packet_size
    if (numBytes%packet_size):
        numPackets+=1
#    for i in range(numPackets+1):






