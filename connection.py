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
        self.window_size = 1
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

    def recv(self):
        while (len(self.rcvBuff) == 0):
            pass

        while (len(self.rcvBuff) > 0):
            return self.rcvBuff.pop()

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
            self.seqNum += 1
            data_packet = self.rtpsocket.create_data_packet(self.destIP, self.destPort, data)
            d_data = packet.split_packet(data_packet)
            self.rtpsocket.udpSocket.sendto(packet.packet_to_bytes(data_packet), (self.destIP, self.destPort))
            self.timeout = False
            t = threading.Timer(1, self.timeout_conn)
            while(not self.timeout and not self.ackReceived): #wait until timeout detected or we get something valid back
                # print ("ASGJAFG")
                pass
                # DO NOTHING
            if (self.timeout): #if we timed out before we got something back, resend the packet
                self.sndBuff.appendright(data_packet)
                self.seqNum -= 1
                continue
        print("finished sending")

    def timeout_conn(self):
        self.timeout = True

    def send_s(self, data):
        address = (self.destIP, self.destPort)
        self.seqNum += 1
        data_packet = self.rtpsocket.create_data_packet(self.destIP, self.destPort, data)
        self.sndBuff.appendleft(data_packet)
        if len(self.sndBuff) > 0 and self.connected:
                data_packet = self.sndBuff.pop()
                self.rtpsocket.udpSocket.sendto(packet.packet_to_bytes(data_packet), address)
                print("Sending data...")
                print("Seqnum: " + str(self.seqNum))

    def close(self):
        print("closingConnections len: " + str(len(self.rtpsocket.closingConnections)))
        if self in self.rtpsocket.closingConnections:
            self.rtpsocket.closingConnections.pop()
            print("closingConnections len after pop: " + str(len(self.rtpsocket.closingConnections)))
            self.rtpsocket.clearConnection(self)
#later add in dynamic receiver window, for now window is 1 packet
