#!/usr/bin/env python3
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

HOST = os.environ.get("RECEIVER_HOST", "127.0.0.1")
PORT = int(os.environ.get("RECEIVER_PORT", "5001"))


def load_payload_chunks() -> List[bytes]:
   """
   Extension of the skeleton code creating a full list of MSS-sized chunks instead of two demo chunks
   Reads the selected payload file (or falls back to file.zip) and returns
   long repeated string split into MSS-sized chunks up to full payload length
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

   print("\nTransfer complete!")
   print(f"duration={duration:.3f}s throughput={throughput:.2f} bytes/sec")
   print(f"avg_delay={avg_delay:.6f}s avg_jitter={avg_jitter:.6f}s ") 
   print(f"{throughput:.7f},{avg_delay:.7f},{avg_jitter:.7f},{metric:.7f}")

   #return throughput, avg_delay, avg_jitter, metric


def main() -> None:
   chunks = load_payload_chunks()
   #measurements = []

   transfers: List[Tuple[int, bytes]] = []
   delays = []

   seq = 0
   for chunk in chunks:
      transfers.append((seq, chunk))
      #seq += len(chunk)
      seq += 1

   # EOF marker
   transfers.append((seq, b""))

   total_bytes = sum(len(chunk) for chunk in chunks)

   # debugging
   # print(f"Connecting to receiver at {HOST}:{PORT}")

   start_time = time.time()

   with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
      sock.settimeout(ACK_TIMEOUT)
      addr = (HOST, PORT)

      for seq_id, payload in transfers:
         pkt = make_packet(seq_id, payload)
         # debugging
         # print(f"Sending frame seq={seq_id}, bytes={len(payload)}")
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
               # debugging
               # print(f"Timeout waiting for ACK (seq={seq_id}). Retrying ({retries}/{MAX_TIMEOUTS})...")
               continue

            ack_id, msg = parse_ack(ack_pkt)
            # debugging
            # print(f"Received {msg.strip()} for ack_id={ack_id}")

            if msg.startswith("ack") and ack_id >= seq_id + len(payload):
               delays.append(time.time() - send_time)
               break

   
      eof_pkt = make_packet(seq, b"")
      retries = 0
      while True:
         sock.sendto(eof_pkt, addr)
         try:
            ack_pkt, _ = sock.recvfrom(PACKET_SIZE)
         except socket.timeout:
            retries += 1
            if retries > MAX_TIMEOUTS:
                  raise RuntimeError("Receiver did not respond to EOF")
            continue

         ack_id, msg = parse_ack(ack_pkt)
         if msg.startswith("ack") and ack_id >= seq:
            break

   duration = time.time() - start_time
   calculate_metrics(total_bytes, duration, delays)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Skeleton sender hit an error: {exc}", file=sys.stderr)
        sys.exit(1)
