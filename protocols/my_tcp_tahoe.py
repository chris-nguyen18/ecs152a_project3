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
WINDOW_SIZE = 1

HOST = os.environ.get("RECEIVER_HOST", "127.0.0.1")
PORT = int(os.environ.get("RECEIVER_PORT", "5001"))
