# modificaiton of TCP Reno implementation to collect data with: cwnd_size, loss, delay, and throughput

#!/usr/bin/env python3 -u

from __future__ import annotations

import csv
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
TIMEOUT = 1.0
WINDOW_SIZE = 1

HOST = os.environ.get("RECEIVER_HOST", "127.0.0.1")
PORT = int(os.environ.get("RECEIVER_PORT", "5001"))

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
    else:
        print("Could not find payload file", file=sys.stderr)
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
    safe_t = throughput if throughput > 0 else 1e-9
    safe_d = avg_delay if avg_delay > 0 else 1e-9
    safe_j = avg_jitter if avg_jitter > 0 else 1e-9
    metric = (2000 / safe_t) + (15 / safe_j) + (35 / safe_d)
    
    print("\nTransfer complete!")
    print(f"duration={duration:.3f}s throughput={throughput:.2f} bytes/sec")
    print(f"avg_delay={avg_delay:.6f}s avg_jitter={avg_jitter:.6f}s")
    print(f"{throughput:.7f},{avg_delay:.7f},{avg_jitter:.7f},{metric:.7f}")

class reno:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(ACK_TIMEOUT)
        self.cwnd = WINDOW_SIZE
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

         # Storing dataset
        self.dataset = []

    def get_action(self, prev_cwnd: float, curr_cwnd: float) -> str:
      """ Determine if the cwnd is decreasing, holding, or increasing """
      if curr_cwnd < prev_cwnd:
         return "decrease"
      elif curr_cwnd > prev_cwnd:
         return "increase"
      else:
         return "hold"


    def send_chunks(self, chunks: List[bytes]):
        start_time = time.time()
        total_bytes = sum(len(c) for c in chunks)
        prev_cwnd = self.cwnd 

        while self.base < len(chunks):
            while self.next_seq < self.base + int(self.cwnd) and self.next_seq < len(chunks):
                seq_bytes = self.next_seq * MSS
                pkt = make_packet(seq_bytes, chunks[self.next_seq])
                self.send_times[seq_bytes] = time.time()
                self.socket.sendto(pkt, (self.host, self.port))
                self.total_bytes += len(chunks[self.next_seq])
                self.next_seq += 1
            try:
                ack_pkt, _ = self.socket.recvfrom(PACKET_SIZE)
                ack_id, _ = parse_ack(ack_pkt)
                recv_time = time.time()
                delay = recv_time - self.send_times.get(ack_id, recv_time)
                self.delays.append(delay)

                # Gathering data 
                throughput = total_bytes / (recv_time - start_time)
                loss = self.dupacks / max(self.next_seq - self.base, 1)

                # Classify cwnd change: increase, hold, or decrease
                action = self.get_action(prev_cwnd, self.cwnd)
                
                # Save data to the dataset
                self.dataset.append({
                    'cwnd': self.cwnd,
                    'action': action,
                    'loss': loss,
                    'delay': delay,
                    'throughput': throughput
                })
                
                # Update previous cwnd for next iteration
                prev_cwnd = self.cwnd

                if ack_id == self.last_ack:
                    self.dupacks += 1
                else:
                    self.dupacks = 0
                self.last_ack = ack_id

                if self.dupacks == 3 and not self.in_fast_recovery:
                    self.ssthresh = max(int(self.cwnd / 2), 1)
                    self.cwnd = self.ssthresh + 3
                    missing_idx = ack_id // MSS
                    if missing_idx < len(chunks):
                        pkt = make_packet(missing_idx * MSS, chunks[missing_idx])
                        self.socket.sendto(pkt, (self.host, self.port))
                    self.in_fast_recovery = True
                    continue

                if self.in_fast_recovery:
                    if ack_id // MSS > self.base:
                        self.cwnd = self.ssthresh
                        self.base = (ack_id // MSS) + 1
                        self.in_fast_recovery = False
                    else:
                        self.cwnd += 1
                    continue

                if ack_id // MSS >= self.base:
                    self.base = (ack_id // MSS) + 1
                    if self.cwnd < self.ssthresh:
                        self.cwnd += 1
                    else:
                        self.cwnd += 1 / self.cwnd
                self.timeouts = 0

            except socket.timeout:
                self.timeouts += 1
                if self.timeouts >= MAX_TIMEOUTS:
                    break
                self.ssthresh = max(int(self.cwnd / 2), 1)
                self.cwnd = 1
                if self.base < len(chunks):
                    seq_bytes = self.base * MSS
                    pkt = make_packet(seq_bytes, chunks[self.base])
                    self.socket.sendto(pkt, (self.host, self.port))

        eof_seq = total_bytes
        eof_pkt = make_packet(eof_seq, b"")
        retries = 0
        while True:
            self.socket.sendto(eof_pkt, (self.host, self.port))
            try:
                ack_pkt, _ = self.socket.recvfrom(PACKET_SIZE)
                ack_id, _ = parse_ack(ack_pkt)
                if ack_id >= eof_seq:
                    break
            except socket.timeout:
                retries += 1
                if retries > MAX_TIMEOUTS:
                    break

        duration = time.time() - start_time
        return self.total_bytes, duration, self.delays

    def save_dataset(self, filename: str) -> None:
        """ Save the dataset to a CSV file """
        target_folder = os.path.join("..", "protocols", "custom_protocol", "data_collection_preprocessing", "data")
        
        # Ensure the 'data' folder exists
        os.makedirs(target_folder, exist_ok=True)
        
        # Define the full path to the CSV file
        filepath = os.path.join(target_folder, filename)
        
        # Save the dataset to the specified path
        with open(filepath, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['cwnd', 'action', 'loss', 'delay', 'throughput'])
            writer.writeheader()
            writer.writerows(self.dataset)
            print(f"Dataset saved to {filepath}")


def main() -> None:
    chunks = load_payload_chunks()
    sender = reno(HOST, PORT)

    for i in range(50):
        total_bytes, duration, delays = sender.send_chunks(chunks)
        calculate_metrics(total_bytes, duration, delays)

    sender.save_dataset("reno_dataset.csv")
    

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Reno sender error: {exc}", file=sys.stderr)
        sys.exit(1)
