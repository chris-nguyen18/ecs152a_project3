#!/usr/bin/env python3

from __future__ import annotations

import os
import socket
import sys
import time

from typing import List, Tuple

PACKET_SIZE = 1024
SEQ_ID_SIZE = 4
MSS = PACKET_SIZE - SEQ_ID_SIZE
ACK_TIMEOUT = 1.0
MAX_TIMEOUTS = 5
MAX_CWND = 1000
MIN_CWND = 10
MAX_RETRIES = 5

HOST = os.environ.get("RECEIVER_HOST", "127.0.0.1")
PORT = int(os.environ.get("RECEIVER_PORT", "5001"))

class custom_protocol:
   def __init__(self, host: str, port: int):
      self.host = host
      self.port = port
      self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.socket.settimeout(ACK_TIMEOUT)
      self.cwnd = 50
      self.ssthresh = 64
      self.base = 0
      self.next_seq = 0
      self.total_bytes = 0
      self.delays = []
      self.timeouts = 0
      self.last_ack = -1        
      self.dupacks = 0
      self.in_fast_recovery = False
      self.send_times = {}     

   def send_chunks(self, chunks: List[bytes]):
      start_time = time.time()
      total_bytes = sum(len(chunk) for chunk in chunks)

      # send loop
      while self.base < len(chunks):

         # sends packets while within window
         while self.next_seq < self.base + int(self.cwnd) and self.next_seq < len(chunks):
            seq_bytes = self.next_seq * MSS
            pkt = make_packet(seq_bytes, chunks[self.next_seq])

            # track timestamp for delay measurement
            self.send_times[seq_bytes] = time.time()

            # send packet
            self.socket.sendto(pkt, (self.host, self.port))
            self.total_bytes += len(chunks[self.next_seq])
            self.next_seq += 1

         try:
            # receive acknowledgment
            ack_pkt, _ = self.socket.recvfrom(PACKET_SIZE)
            ack_id, _ = parse_ack(ack_pkt)
            recv_time = time.time()

            # calc delay
            delay = recv_time - self.send_times.get(ack_id, recv_time)
            self.delays.append(delay)

            sent_time = self.send_times.get(ack_id, recv_time)
            delay = recv_time - sent_time
            self.delays.append(delay)

            if ack_id >= (self.base * MSS):
               self.base = (ack_id // MSS) + 1

            # timeout counter reset
            self.timeouts = 0

            # detect duplicate ACK detection
            if ack_id == self.last_ack:
               self.dupacks += 1
            else:
               self.dupacks = 0
               self.in_fast_recovery = False

            self.last_ack = ack_id

            # Compute metrics for cwnd classification
            throughput = total_bytes / (recv_time - start_time)
            loss = self.dupacks / max(self.next_seq - self.base, 1)

            # ML-based congestion window update
            self.cwnd = classify_cwnd(loss, delay, throughput, self.cwnd)

            # Fast retransmit on 3 duplicate ACKs
            if self.dupacks == 3 and not self.in_fast_recovery:
               self.ssthresh = max(int(self.cwnd / 2), 1)
               self.cwnd = self.ssthresh + 3  # inflate temporarily

               # Retransmit missing packet
               missing_idx = ack_id // MSS
               if missing_idx < len(chunks):
                  pkt = make_packet(missing_idx * MSS, chunks[missing_idx])
                  self.send_times[missing_idx * MSS] = time.time()
                  self.socket.sendto(pkt, (self.host, self.port))

               self.in_fast_recovery = True

         # Handling timeout
         except socket.timeout:
            # Timeout occurs → retransmit first unacked packet
            self.timeouts += 1
            print("Timeout: Retransmitting...")

            if self.timeouts >= MAX_TIMEOUTS:
               break

            # Standard TCP-like multiplicative decrease
            self.ssthresh = max(int(self.cwnd // 2), 2)
            self.cwnd = MIN_CWND

            # Retransmit earliest unacked packet
            if self.base < len(chunks):
               seq_bytes = self.base * MSS
               pkt = make_packet(seq_bytes, chunks[self.base])
               self.send_times[seq_bytes] = time.time()
               self.socket.sendto(pkt, (self.host, self.port))

            # Restart sending from the base
            self.next_seq = self.base

      # Send EOF marker (sequence number at end-of-file)
      eof_seq = total_bytes
      eof_pkt = make_packet(eof_seq, b"")

      # Retry EOF packet until acknowledged or max attempts reached
      retries = 0
      while retries < MAX_TIMEOUTS:
         self.socket.sendto(eof_pkt, (self.host, self.port))
         try:
            ack_pkt, _ = self.socket.recvfrom(PACKET_SIZE)
            ack_id, _ = parse_ack(ack_pkt)
            if ack_id >= eof_seq:
               break
         except socket.timeout:
            retries += 1

      duration = time.time() - start_time
      return self.total_bytes, duration, self.delays
      


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

   print("\nDemo transfer complete!")
   print(f"duration={duration:.3f}s throughput={throughput:.2f} bytes/sec")
   print(f"avg_delay={avg_delay:.6f}s avg_jitter={avg_jitter:.6f}s d") 
   print(f"{throughput:.7f},{avg_delay:.7f},{avg_jitter:.7f},{metric:.7f}")


# Uses equations as hardcoded values from model
def classify_cwnd(loss, delay, throughput, current_cwnd):
   # Logistic regression coefficients
   score_decrease = (-0.076597 * loss +
                      -0.200254 * delay +
                      -0.002375 * throughput +
                      0.893127)

   score_hold = (0.003699 * loss +
               -0.000245 * delay +
               0.452747 * throughput +
               0.084082)

   score_increase = (0.072897 * loss +
                     0.200499 * delay +
                     -0.450373 * throughput +
                     -0.977209)

   # select best action based off of score
   scores = {
      "decrease": score_decrease,
      "hold": score_hold,
      "increase": score_increase
   }

   best_action = max(scores, key=scores.get)

   if best_action == "increase":
      # increase current window
      return min(current_cwnd + (current_cwnd // 10), MAX_CWND)
   elif best_action == "decrease":
      # decrease by fixed amount
      return max(current_cwnd - 5, MIN_CWND)
   else:
      return current_cwnd


def main() -> None:
   chunks = load_payload_chunks()
   sender = custom_protocol(HOST, PORT)
   total_bytes, duration, delays = sender.send_chunks(chunks)
   calculate_metrics(total_bytes, duration, delays)
   

if __name__ == "__main__":
   try:
      main()
   except Exception as exc:
      print(f"Skeleton sender hit an error: {exc}", file=sys.stderr)
      sys.exit(1)
