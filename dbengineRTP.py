import rtpsocket
import sys
import socket

s = rtpsocket.Rtpsocket()
host = '127.0.0.1'
students = {'903076259':['Anthony', 'Peterson', 231, 63, float(231/63.0)],
            '903084074':['Richard', 'Harris', 236, 66, float(236/66.0)],
            '903077650':['Joe', 'Miller', 224, 65, float(224/65.0)],
            '903083691':['Todd', 'Collins', 218, 56, float(218/56.0)],
            '903082265':['Laura', 'Stewart', 207, 64, float(207/64.0)],
            '903075951':['Marie', 'Cox', 246, 63, float(246/63.0)],
            '903084336':['Stephen', 'Baker', 234, 66, float(234/66.0)]
                                                                        }   #create database (dictionary)
port = 8080

 
s.bind(host, port) #bind the host ip with the port if it's valid
s.listen()         


print host + ":" + str(port) #print the host:port that server is using
