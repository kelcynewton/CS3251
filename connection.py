import packet
import Queue

class Connection():
    def __init__(self, sourcePort, destPort, destIP, window_size, seqNum, ackNum, data, rcvBuff, sndBuff):
        self.src = sourcePort
        self.destPort = destPort
        self.destIP = destIP
        self.window_size = 1
        self.seqNum = 0
        self.ackNum = 0
        self.data = data
        self.revBuff = queue.Queue()
        self.sndBuff = queue.Queue()

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






