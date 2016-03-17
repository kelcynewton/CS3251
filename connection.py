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








