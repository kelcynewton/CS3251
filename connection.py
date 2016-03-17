import packet
import time
import rtpsocket
from collections import deque

# Packet types:
# SYN = 1
# ACK = 2
# DATA = 4
# FIN = 8

class Connection():
    def __init__(self, sourcePort, destPort, destIP, seqNum, ackNum, data, rtpsocket):
        self.src = sourcePort
        self.destPort = destPort
        self.destIP = destIP
        self.window_size = 1
        self.seqNum = seqNum
        self.ackNum = ackNum
        self.data = data
        self.rcvBuff = deque()
        self.sndBuff = deque()
        self.connected = False
        self.finReceived = False
        self.rtpsocket = rtpsocket


    def recv(self):
        time.sleep(1)
        if len(self.rcvBuff) > 0:
            pkt_data = self.rcvBuff.pop()
            return pkt_data

    def send_s(self, data):
        address = (self.destIP, self.destPort)
        data_packet = self.rtpsocket.create_data_packet(self.destIP, self.destPort, data)
        self.sndBuff.appendleft(data_packet)
        if len(self.sndBuff) > 0 and self.connected:
                data_packet = self.sndBuff.pop()
                self.rtpsocket.udpSocket.sendto(packet.packet_to_bytes(data_packet), address)

#later add in dynamic receiver window, for now window is 1 packet


