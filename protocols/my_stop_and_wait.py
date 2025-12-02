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

# test load_payload_chunks() extending skeleton code to 5 chunks for simpler testing
'''
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
      print("returned default list chunks")
      return [
         b"Chunk 1 placeholder",
         b"Chunk 2 placeholder",
         b"Chunk 3 placeholder",
         b"Chunk 4 placeholder",
         b"Chunk 5 placeholder",
      ]
    # Split the data into MSS-sized chunks
    # debug with 5 chunks 
   print("print full chunk list")
   chunk1 = data[0:MSS] or b"Chunk 1 placeholder"
   chunk2 = data[MSS:2*MSS] or b"Chunk 2 placeholder"
   chunk3 = data[2*MSS:3*MSS] or b"Chunk 3 placeholder"
   chunk4 = data[3*MSS:4*MSS] or b"Chunk 4 placeholder"
   chunk5 = data[4*MSS:5*MSS] or b"Chunk 5 placeholder"

   return [chunk1, chunk2, chunk3, chunk4, chunk5]
   #return [data[i : i + MSS] for i in range(0, len(data), MSS)]
'''

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

   return throughput, avg_delay, avg_jitter, metric


def print_stats(measurements: List[tuple]):
   throughputs, jitters_avg, delays_avg, metrics = [], [], [], []

   for t, j, d, m in measurements:
      throughputs.append(t)
      delays_avg.append(d)
      jitters_avg.append(j)
      metrics.append(m)
      print(f"Run: throughput={t:.2f}, avg_delay={d:.6f}, avg_jitter={j:.6f}, metric={m:.6f}")

   # Compute averages and standard deviations
   print("\n=== Summary over all runs ===")
   print(f"Throughput: mean={statistics.mean(throughputs):.2f}, std={statistics.stdev(throughputs):.2f}")
   print(f"Avg Delay: mean={statistics.mean(delays_avg):.6f}, std={statistics.stdev(delays_avg):.6f}")
   print(f"Avg Jitter: mean={statistics.mean(jitters_avg):.6f}, std={statistics.stdev(jitters_avg):.6f}")
   print(f"Performance Metric: mean={statistics.mean(metrics):.6f}, std={statistics.stdev(metrics):.6f}")



def main() -> None:
   chunks = load_payload_chunks()
   measurements = []
   print(f"[DEBUG] Loaded payload chunks ({len(chunks)} chunks):")
   for i, chunk in enumerate(chunks): # delete later
      print(f"  Chunk {i}: length={len(chunk)} content={chunk[:50]}{'...' if len(chunk) > 50 else ''}")

   transfers: List[Tuple[int, bytes]] = []
   delays = []

   seq = 0
   for chunk in chunks:
      # delete later
      print(f"[DEBUG] Adding chunk {i} to transfers with seq={seq}, length={len(chunk)}")
      transfers.append((seq, chunk))
      seq += len(chunk)
   print("seq: ", seq)# delete later


   # EOF marker
   transfers.append((seq, b""))
   print(f"[DEBUG] Added EOF marker with seq={seq}") # delete later
   print(f"[DEBUG] Total transfers list length: {len(transfers)}")  # delete later

   total_bytes = sum(len(chunk) for chunk in chunks)

   print(f"Connecting to receiver at {HOST}:{PORT}")
   # delete later
   print(
      f"Test transfer will send {total_bytes} bytes across {len(chunks)} packets (+EOF)."
   )

   start_time = time.time()

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
   measurements.append(calculate_metrics(total_bytes, duration, delays))
   print_stats(measurements)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Skeleton sender hit an error: {exc}", file=sys.stderr)
        sys.exit(1)
