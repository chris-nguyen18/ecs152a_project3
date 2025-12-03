#!/usr/bin/env python3 -u

from __future__ import annotations

import os
import socket
import sys
import time
import statistics
from typing import List, Tuple

PACKET_SIZE = 1024
SEQ_ID_SIZE = 4
MSS = PACKET_SIZE - SEQ_ID_SIZE
ACK_TIMEOUT = 1.0
MAX_TIMEOUTS = 5
TIMEOUT = 1.0

HOST = os.environ.get("RECEIVER_HOST", "127.0.0.1")
PORT = int(os.environ.get("RECEIVER_PORT", "5001"))


# test load_payload_chunks() extending skeleton code to 5 chunks for simpler testing
def load_payload_chunks() -> List[bytes]:
   """
   Reads the selected payload file (or falls back to file.zip) and returns
   up to two MSS-sized chunks for the demo transfer.
   """
   candidates = [
      os.environ.get("TEST_FILE"),
      os.environ.get("PAYLOAD_FILE"),
      "/hdd/file.zip",
      "file.zip",
   ]

   for path in candidates:
      if not path:
         continue
      expanded = os.path.expanduser(path)
      if os.path.exists(expanded):
         with open(expanded, "rb") as f:
            data = f.read()
         break
   else:
      print(
         "Could not find payload file (tried TEST_FILE, PAYLOAD_FILE, file.zip)",
         file=sys.stderr,
      )
      sys.exit(1)
   if not data:
      default = b"DemoPayloadForECS152A" * 100
      return [default[i:i+MSS] for i in range(0, len(default), MSS)]
   
   return [data[i:i+MSS] for i in range(0, len(data), MSS)]
'''

# test load_payload_chunks() function with 5 chunks for easier testing
def load_payload_chunks() -> List[bytes]:
   candidates = [
      os.environ.get("TEST_FILE"),
      os.environ.get("PAYLOAD_FILE"),
      "/hdd/file.zip",
      "file.zip",
   ]

   for path in candidates:
      if not path:
         continue
      expanded = os.path.expanduser(path)
      if os.path.exists(expanded):
         with open(expanded, "rb") as f:
               data = f.read()
         break
   #if not data:
        # Either file not found or empty → return demo placeholders
        #print("returned default list chunks")
        #return [b"Hello from ECS152A!", b"Second packet from skeleton sender"]
   
   if not data:
      print("DEBUG: returned default list chunks")
      return [
         b"Chunk 1 placeholder",
         b"Chunk 2 placeholder",
         b"Chunk 3 placeholder",
         b"Chunk 4 placeholder",
         b"Chunk 5 placeholder",
      ]
    # Split the data into MSS-sized chunks
    # debug with 5 chunks 
   print("DEBUG: print full chunk list")
   chunk1 = data[0:MSS] or b"Chunk 1 placeholder"
   chunk2 = data[MSS:2*MSS] or b"Chunk 2 placeholder"
   chunk3 = data[2*MSS:3*MSS] or b"Chunk 3 placeholder"
   chunk4 = data[3*MSS:4*MSS] or b"Chunk 4 placeholder"
   chunk5 = data[4*MSS:5*MSS] or b"Chunk 5 placeholder"

   return [chunk1, chunk2, chunk3, chunk4, chunk5]
'''
   
def make_packet(seq_id: int, payload: bytes) -> bytes:
   return int.to_bytes(seq_id, SEQ_ID_SIZE, byteorder="big", signed=True) + payload


def parse_ack(packet: bytes) -> Tuple[int, str]:
   seq = int.from_bytes(packet[:SEQ_ID_SIZE], byteorder="big", signed=True)
   msg = packet[SEQ_ID_SIZE:].decode(errors="ignore")
   return seq, msg


def calculate_metrics(total_bytes: int, duration: float, delays: List[float]) -> None:
   throughput = total_bytes / duration if duration > 0 else 0.0

   avg_delay = sum(delays) / len(delays) if delays else 0.0

   if len(delays) > 1:
      diffs = [abs(delays[i] - delays[i-1]) for i in range(1, len(delays))]
      avg_jitter = sum(diffs) / len(diffs)
   else:
      avg_jitter = 0.0

   safe_throughput = throughput if throughput > 0 else 1e-9
   safe_delay = avg_delay if avg_delay > 0 else 1e-9
   safe_jitter = avg_jitter if avg_jitter > 0 else 1e-9

   metric = (2000 / safe_throughput) + (15 / safe_jitter) + (35 / safe_delay)

   print("\nDemo transfer complete!")
   print(f"duration={duration:.3f}s throughput={throughput:.2f} bytes/sec")
   print(f"avg_delay={avg_delay:.6f}s avg_jitter={avg_jitter:.6f}s d") 
   print(f"{throughput:.7f},{avg_delay:.7f},{avg_jitter:.7f},{metric:.7f}")

   return 


def main() -> None:
   chunks = load_payload_chunks()
   seq = 0
   seq_numbers = []
   packets = []

   for chunk in chunks:
      packets.append(make_packet(seq, chunk))
      seq_numbers.append(seq)
      seq += len(chunk)

   packets.append(make_packet(seq, b""))
   seq_numbers.append(seq)

   total_bytes = sum(len(chunk) for chunk in chunks)
   total_packets = len(packets)   

   base, next_seq, window_size = 0,0,100

   send_time = {i: None for i in range(total_packets)}
   acked = {i: False for i in range(total_packets)}
   delays = []

   print(f"Connecting to receiver at {HOST}:{PORT}")  

   start_time = time.time()

   with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
      sock.settimeout(ACK_TIMEOUT)
      addr = (HOST, PORT)

      while base < total_packets:
         while next_seq < base + window_size and next_seq < total_packets:
            sock.sendto(packets[next_seq], addr)
            send_time[next_seq] = time.time()
            next_seq += 1

         try:
            ack_pkt,_ = sock.recvfrom(PACKET_SIZE)
            ack_id, msg = parse_ack(ack_pkt)

            if msg.strip().lower().startswith("fin"):
               fin_ack = make_packet(ack_id, b"FIN/ACK")
               sock.sendto(fin_ack, addr)
               duration = max(time.time() - start_time, 1e-6)
               break
            
            ack_index = next((i for i, s in enumerate(seq_numbers) if s >= ack_id), total_packets)
            for i in range(base, ack_index):
               if not acked[i]:
                  acked[i] = True
                  delay = time.time() - send_time[i]
                  delays.append(delay)
            base = ack_index

         except socket.timeout:

            for seq in range(base, next_seq):
               sock.sendto(packets[seq], addr)
               send_time[seq] = time.time()

   duration = time.time() - start_time
   calculate_metrics(total_bytes, duration, delays)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Skeleton sender hit an error: {exc}", file=sys.stderr)
        sys.exit(1)
