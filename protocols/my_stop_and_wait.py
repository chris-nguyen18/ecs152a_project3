#!/usr/bin/env python3 -u

from __future__ import annotations

import os
import socket
import sys
import time
import struct
from typing import List, Tuple

PACKET_SIZE = 1024
SEQ_ID_SIZE = 4
MSS = PACKET_SIZE - SEQ_ID_SIZE
ACK_TIMEOUT = 1.0
MAX_TIMEOUTS = 5
TIMEOUT = 1.0

HOST = os.environ.get("RECEIVER_HOST", "127.0.0.1")
PORT = int(os.environ.get("RECEIVER_PORT", "5001"))

def load_payload_chunks() ->List[bytes]:
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

   # return list of chunks instead of just first two
   return [data[i : i + MSS] for i in range(0, len(data), MSS)]


def make_packet(seq_id: int, payload: bytes) -> bytes:
   return int.to_bytes(seq_id, SEQ_ID_SIZE, byteorder="big", signed=True) + payload

def parse_ack(packet: bytes) -> Tuple[int, str]:
   seq = int.from_bytes(packet[:SEQ_ID_SIZE], byteorder="big", signed=True)
   msg = packet[SEQ_ID_SIZE:].decode(errors="ignore")
   return seq, msg

def print_metrics(total_bytes: int, duration: float, delays: List[float]) -> None:
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
   print(f"avg_delay={avg_delay:.6f}s avg_jitter={avg_jitter:.6f}s (TODO: Calculate actual values)") # finish later
   print(f"{throughput:.7f},{avg_delay:.7f},{avg_jitter:.7f},{metric:.7f}")
   
def main() -> None:
   chunks = load_payload_chunks()
   print("chunks", chunks)# debug
   print("length chunks", len(chunks))# debug 
   transfers: List[Tuple[int, bytes]] = []
   print("transfers", transfers)# debug
   print("transfers chunks", len(transfers))# debug 

   seq = 0
   for chunk in chunks:
      transfers.append((seq, chunk))
      seq += len(chunk)

   transfers.append((seq, b""))
   total_bytes = sum(len(chunk) for chunk in chunks)

   print("transfers", transfers)# debug
   print("transfers chunks", len(transfers))# debug 
   print("total_bytes: ", total_bytes)

   delays = []

   print(f"Connecting to receiver at {HOST}:{PORT}")
   print(f"Transfer will send {total_bytes} bytes across {len(chunks)} packets (+EOF).")

   start = time.time()
   with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
      sock.settimeout(ACK_TIMEOUT)
      addr = (HOST, PORT)

      for seq_id, payload in transfers:
         pkt = make_packet(seq_id, payload)
         print(f"Sending frame seq={seq_id}, bytes={len(payload)}")
         retries = 0

         while True:
            send_time = time.time()
            sock.sendto(pkt, addr)
            try:
               ack_pkt, _ = sock.recvfrom(PACKET_SIZE)
            except socket.timeout:
               retries += 1
               if retries > MAX_TIMEOUTS:
                  raise RuntimeError("Receiver did not respond (max retries exceeded)")
               print(f"Timeout waiting for ACK (seq={seq_id}). Retrying ({retries}/{MAX_TIMEOUTS})...")
               continue

            ack_id, msg = parse_ack(ack_pkt)
            print(f"Received {msg.strip()} for ack_id={ack_id}")

            if msg.startswith("ack") and ack_id >= seq_id + len(payload):
               delays.append(time.time() - send_time)
               break
   
   while True:
      try:
         ack_pkt, _ = sock.recvfrom(PACKET_SIZE)
      except socket.timeout:
         continue
      ack_id = parse_ack(ack_pkt)
      if msg.startswith("fin"):
         fin_ack = make_packet(ack_id, b"FIN/ACK")
         sock.sendto(fin_ack, addr)
         #duration = time.time() - start
         #print_metrics(total_bytes, duration, delays)
         break

   duration = time.time() - start
   print_metrics(total_bytes, duration, delays)

if __name__ == "__main__":
   try:
      main()
   except Exception as exc:
      print(f"Skeleton sender hit an error: {exc}", file=sys.stderr)
      sys.exit(1)