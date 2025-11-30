import socket 
import struct
import time

PACKET_SIZE = 1024 # bytes 
SERVER = ("127.0.0.1", 9000)
TIMEOUT = 1.0

def stop_and_wait_send(messages):
   sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   sock.settimeout(TIMEOUT)

   seq = 0
   for message in messages:
      packet = struct.pack("!I", seq) + message.encode('utf-8') 

      sock.sendto(packet,SERVER)
      print(f"Sent packet with sequence number {seq}")

      while True:
         try:
            ack_data, _ = sock.recvfrom(PACKET_SIZE)
            ack_seq = struct.unpack("!I", ack_data[:4])[0]

            if ack_seq == seq:
               seq = 1 - seq
               print(f"Received ACK {ack_seq}")
               break
               
         except socket.timeout:
            print("Timeout! Retransmitting...")
            sock.sendto(packet, SERVER)

   sock.close()


