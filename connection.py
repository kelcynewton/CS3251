import packet
import time
import rtpsocket
from math import ceil
from collections import deque

# Packet types:
# SYN = 1
# ACK = 2
# DATA = 4
# FIN = 8

class Connection():

    MAX_SIZE = 1024
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


    def recv(self):
        time.sleep(1)
        if len(self.rcvBuff) > 0:
            pkt_data = self.rcvBuff.pop()
            return pkt_data

    def send(self, data):
        num_packets = int(ceil(len(data) // 1024))
        for i in range(0, num_packets):
            start = i * 1024
            end = min(((i + 1) * 1024) - 1, len(data))
            data_packet = self.rtpsocket.create_data_packet(self.destIP, self.destPort, data[start:end])
            self.sndBuff.appendleft(data_packet)

        while(len(self.sndBuff) > 0 and self.connected):
            data_packet = self.sndBuff.pop()
            d_data = packet.split_packet(data_packet)
            self.rtpsocket.udpSocket.sendto(packet.packet_to_bytes(data_packet), (self.destIP, self.destPort))
            self.timeout = False
            t = threading.Timer(1, self.timeout_conn)
            while(not self.timeout and len(rcvBuff) == 0):
                pass
                # DO NOTHING
            if (self.timeout):
                self.sndBuff.appendright(data_packet)
                continue
            else:
                recv_pkt = self.rcvBuff.pop()
                p_data = [packet.split_packet(recv_pkt)]
                if (p_data[4] == 2 and p_data[3] == d_data[3]):
                    continue
                else:
                    self.rcvBuff.appendright(recv_pkt)
                    self.sndBuff.appendright(data_packet)
                    continue

    def timeout_conn(self):
        self.timeout = True






    def send_s(self, data):
        address = (self.destIP, self.destPort)
        data_packet = self.rtpsocket.create_data_packet(self.destIP, self.destPort, data)
        self.sndBuff.appendleft(data_packet)
        if len(self.sndBuff) > 0 and self.connected:
                data_packet = self.sndBuff.pop()
                self.rtpsocket.udpSocket.sendto(packet.packet_to_bytes(data_packet), address)

#later add in dynamic receiver window, for now window is 1 packet
