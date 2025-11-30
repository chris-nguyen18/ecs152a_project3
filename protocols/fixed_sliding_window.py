import socket 
import struct
import time

PACKET_SIZE = 1024 # bytes 
SERVER = ("127.0.0.1", 9000)
TIMEOUT = 1.0