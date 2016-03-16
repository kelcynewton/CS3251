import packet
import Queue

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
        self.revBuff = Queue.Queue()
        self.sndBuff = Queue.Queue()
        self.connected = False

#later add in dynamic receiver window, for now window is 1 packet








