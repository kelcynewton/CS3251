import rtpsocket
import sys

s = rtpsocket.Rtpsocket()

host = '127.0.0.1'
port = 8080

s.connect(host, port)