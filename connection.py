import packet
from packet import Packet
import time
import rtpsocket
import threading
from math import ceil
from collections import deque
from sys import getsizeof

# Packet types:
# SYN = 1
# ACK = 2
# DATA = 4
# FIN = 8

class Connection():

    MAX_SIZE = 700
    TIMEOUT = 1

    def __init__(self, sourcePort, destPort, destIP, seqNum, ackNum, data, rtpsocket):
        self.src = sourcePort
        self.destPort = destPort
        self.destIP = destIP
        self.seqNum = seqNum
        self.ackNum = ackNum
        self.data = data
        self.rcvBuff = deque()
        self.sndBuff = deque()
        self.connected = False
        self.finReceived = False
        self.rtpsocket = rtpsocket
        self.timeout = False
        self.ackReceived = False
        self.expectedSeq = 0
        self.expectedAck = 0
        self.window_size = self.rtpsocket.window

    def recv(self):
        while (len(self.rcvBuff) == 0):
            pass
        data = self.rcvBuff.pop()
        return data

    def send(self, data):
        if (isinstance(data, str)):
            data = data.encode()

        print("Sending", getsizeof(data))
        num_packets = int(ceil(getsizeof(data) / float(self.MAX_SIZE)))

        print("Packets: ", num_packets)

        for i in range(0, num_packets):
            start = i * self.MAX_SIZE
            end = min(((i + 1) * self.MAX_SIZE), len(data))
            self.sndBuff.appendleft(data[start:end])

        while(len(self.sndBuff) > 0 and self.connected):

            self.ackReceived = False
            data = self.sndBuff.pop()
            # self.seqNum += 1
            self.expectedAck = self.seqNum
            if (len(self.sndBuff) == 0):
                # last packet sets the lastpacket bit to 1
                data_packet = self.rtpsocket.create_data_packet(self.destIP, self.destPort, data, 1)
            else:
                data_packet = self.rtpsocket.create_data_packet(self.destIP, self.destPort, data, 0)
            # d_data = packet.split_packet(data_packet)
            # self.rtpsocket.udpSocket.sendto(packet.packet_to_bytes(data_packet), (self.destIP, self.destPort))
            # self.timeout = False
            # t = threading.Timer(1, self.timeout_conn)
            # t.start()
            # while(not self.timeout and not self.ackReceived): #wait until timeout detected or we get something valid back
            #     pass
            #     # DO NOTHING
            # if (self.timeout): #if we timed out before we got something back, resend the packet
            #     self.sndBuff.append(data)
            #     self.seqNum -= 1
            #     continue
            # if(self.ackReceived):
            #     t.cancel()
            self.rtpsocket.send_timeout(data_packet, (self.destIP, self.destPort), False)
        print("finished sending")

    def timeout_conn(self):
        self.timeout = True

    def close(self):
        print("closingConnections len: " + str(len(self.rtpsocket.closingConnections)))
        if self in self.rtpsocket.closingConnections:
            self.rtpsocket.closingConnections.pop()
            print("closingConnections len after pop: " + str(len(self.rtpsocket.closingConnections)))
            self.rtpsocket.clearConnection(self)
