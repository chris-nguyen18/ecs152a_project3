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
ACK_TIMEOUT = 3.0
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

class tahoe:
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
        self.delays: List[float] = []
        self.timeouts = 0
        self.send_times = {}
        self.acked = set()

    def send_chunks(self, chunks: List[bytes]):
        start_time = time.time()
        total_bytes = sum(len(c) for c in chunks)
        max_loops = len(chunks) * 10
        loop_counter = 0

        while self.base < len(chunks) and loop_counter < max_loops:
            loop_counter += 1
            while self.next_seq < self.base + int(self.cwnd) and self.next_seq < len(chunks):
                seq_bytes = self.next_seq * MSS
                pkt = make_packet(seq_bytes, chunks[self.next_seq])
                if seq_bytes not in self.send_times:
                    self.send_times[seq_bytes] = time.time()
                self.socket.sendto(pkt, (self.host, self.port))
                self.total_bytes += len(chunks[self.next_seq])
                # debugging
                # print(f"[SEND] seq={seq_bytes} cwnd={self.cwnd} base={self.base}")
                # sys.stdout.flush()
                self.next_seq += 1

            try:
                ack_pkt, _ = self.socket.recvfrom(PACKET_SIZE)
                ack_id, _ = parse_ack(ack_pkt)
                recv_time = time.time()
                if ack_id in self.send_times and ack_id not in self.acked:
                    delay = recv_time - self.send_times[ack_id]
                    self.delays.append(delay)
                    self.acked.add(ack_id)
                    # debugging
                    # print(f"[ACK RECEIVED] ack_id={ack_id} delay={delay:.6f}s")
                    # sys.stdout.flush()
                if ack_id // MSS >= self.base:
                    self.base = ack_id // MSS + 1
                    if self.cwnd < self.ssthresh:
                        self.cwnd += 1
                    else:
                        self.cwnd += 1 / self.cwnd
            except socket.timeout:
                self.timeouts += 1
                self.ssthresh = max(int(self.cwnd / 2), 1)
                self.cwnd = 1
                # debugging
                # print(f"[TIMEOUT] base={self.base} cwnd={self.cwnd} timeouts={self.timeouts}")
                # sys.stdout.flush()
                if self.base < len(chunks):
                    seq_bytes = self.base * MSS
                    pkt = make_packet(seq_bytes, chunks[self.base])
                    if seq_bytes not in self.send_times:
                        self.send_times[seq_bytes] = time.time()
                    self.socket.sendto(pkt, (self.host, self.port))
                    # debugging
                    # print(f"[RETRANSMIT] seq={seq_bytes} due to timeout")
                    # sys.stdout.flush()
                if self.timeouts >= MAX_TIMEOUTS:
                    # debugging
                    # print("[MAX TIMEOUTS REACHED] stopping transmission")
                    # sys.stdout.flush()
                    break

        eof_seq = total_bytes
        eof_pkt = make_packet(eof_seq, b"")
        retries = 0
        while retries <= MAX_TIMEOUTS:
            self.socket.sendto(eof_pkt, (self.host, self.port))
            # debugging
            # print(f"[SEND EOF] seq={eof_seq}")
            # sys.stdout.flush()
            try:
                ack_pkt, _ = self.socket.recvfrom(PACKET_SIZE)
                ack_id, _ = parse_ack(ack_pkt)
                # debugging
                # print(f"[ACK RECEIVED EOF] ack_id={ack_id}")
                # sys.stdout.flush()
                if ack_id >= eof_seq:
                    break
            except socket.timeout:
                retries += 1
                # debugging
                # print(f"[TIMEOUT EOF] retries={retries}")
                # sys.stdout.flush()

        duration = time.time() - start_time
        return self.total_bytes, duration, self.delays

def main() -> None:
    chunks = load_payload_chunks()
    sender = tahoe(HOST, PORT)
    total_bytes, duration, delays = sender.send_chunks(chunks)
    calculate_metrics(total_bytes, duration, delays)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Tahoe sender error: {exc}", file=sys.stderr)
        sys.exit(1)
