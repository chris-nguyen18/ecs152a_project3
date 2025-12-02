#!/usr/bin/env python3 -u

from __future__ import annotations

import os
import socket
import sys
import time
import struct
from typing import List, Tuple

# imports for model
import numpy as np
from sklearn.linear_model import LogisticRegression
import joblib

PACKET_SIZE = 1024
SEQ_ID_SIZE = 4
MSS = PACKET_SIZE - SEQ_ID_SIZE
ACK_TIMEOUT = 1.0
MAX_TIMEOUTS = 5
TIMEOUT = 1.0

HOST = os.environ.get("RECEIVER_HOST", "127.0.0.1")
PORT = int(os.environ.get("RECEIVER_PORT", "5001"))

def train_model():
   X = np.load("X.npy")
   y = np.load("y.npy")

   model = LogisticRegression(
      multi_class='multinomial',
      solver='lbfgs',
      max_iter=500
   )

   model.fit(X, y)

   joblib.dump(model, "ml_cwnd_model.pkl")

   print("Training done.")