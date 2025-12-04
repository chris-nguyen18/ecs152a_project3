# ECS 152A Programming Project 3 (Fall 2025)

This project is meant to teach TCP congestion control algorithms through implementation. You will build sender programs that transfer files over an emulated network with variable bandwidth, latency, and packet loss.

## Notes about structure 
1. **Project Structure** All of our implementations will be in the protocols
    ``` .
    ├── README.md
    ├── SETUP.md
    ├── docker
    │   ├── Dockerfile
    │   ├── docker-script.sh
    │   ├── file.mp3
    │   ├── file.zip
    │   ├── hdd
    │   │   └── file.zip
    │   ├── receiver.py
    │   ├── sender_skeleton.py
    │   ├── start-simulator.sh
    │   ├── start_sim.bat
    │   ├── test_sender.bat
    │   ├── test_sender.sh
    │   └── training_profile.sh
    ├── protocols
    │   ├── TROUBLESHOOTING.md
    │   ├── custom_protocol
    │   │   ├── X.npy
    │   │   ├── data_collection_preprocessing
    │   │   │   ├── data
    │   │   │   │   └── pantheon.json
    │   │   │   ├── pantheon_data_collection.py
    │   │   │   ├── pantheon_data_preprocess.py
    │   │   │   └── pantheon_df.pkl
    │   │   ├── label_encoder.pkl
    │   │   ├── ml_cwnd_model.pkl
    │   │   ├── model.py
    │   │   ├── scaler.pkl
    │   │   └── y.npy
    │   ├── my_custom_protocol.py
    │   ├── my_fixed_sliding_window.py
    │   ├── my_stop_and_wait.py
    │   ├── my_tcp_reno.py
    │   ├── my_tcp_tahoe.py
    │   └── protocol_stats.py
    └── submissionPage3_ChrisNguyen_921229957_AndreVojtenyi_919403594.pdf
    ```
2. **Custom protocol** The sender file is custom_file.py. The custom_protocol folder includes steps about data collection, preprocessing, model training, and saves the model and other data used. It has external libraries such as sklearn and pandas and isn't run inside the docker container. In case you want to recreate the instructions are below assuming python3 is already installed.

---

## Setting up the Python environment

1. **Create a virtual environment** (recommended to avoid conflicts with system libraries):  
   ```bash
   python3 -m venv venv
    ```
2. Activate the virtual environment 
### Linux / macOS
```bash
source venv/bin/activate
```
### Windows
```bash
venv\Scripts\activate.bat
```
3. **Installing Libraries**
```
#!/bin/bash

# Activate the virtual environment first (if not already activated)
# Linux/macOS: source venv/bin/activate
# Windows (Git Bash): source venv/Scripts/activate

# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install numpy pandas scikit-learn

# Verify installations
python -c "import numpy; import pandas; import sklearn; print('All packages installed successfully!')"
```

4. **Running Python**
```
# Preprocess Pantheon dataset
python3 protocols/custom_protocol/pantheon_data_preprocess.py

# Train or load the ML CWND model
python3 protocols/custom_protocol/model.py
```

## Quick Start

1. **Setup** (one time): Install Docker - see [SETUP.md](SETUP.md)
2. **Testing**: Use the simplified test script (optionally pass a custom payload):
```bash
cd docker
# Build + launch simulator (detached, keeps running)
./start-simulator.sh

# Test your implementation (optional payload arg)
./test_sender.sh ../protocols/my_stop_and_wait.py [payload.zip]
```
3. **Troubleshooting**: Having issues? Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Quick Test Workflow

**macOS/Linux:**

```bash
cd docker

# Build + launch simulator (detached, keeps running)
./start-simulator.sh

# Test your implementation (optional payload arg)
./test_sender.sh ../protocols/my_stop_and_wait.py [payload.zip]
```

**Windows (Command Prompt/Batch):**

```batch
cd docker

# Build + launch simulator (detached, keeps running)
start_sim.bat

# Test your implementation (optional payload arg)
test_sender.bat ../protocols/my_stop_and_wait.py [payload.zip]
```

**What the test scripts are supposed to do:**

- ✓ Verify Docker/daemon status
- ✓ Ensure the long-running simulator container is up
- ✓ Copy your sender and the chosen payload into `/app` and `/hdd`
- ✓ Start a fresh in-container receiver for every run (instead of restarting the container)
- ✓ Run your sender, collect metrics, and print CSV + averages

### Payload files 101

- **Default file**: Every script uses `file.zip` (from `docker/` or `docker/hdd/`) when you omit the third argument.
- **Custom file**: Pass any relative or absolute path (`./test_sender.sh my_sender.py assets/mytrace.zip`). The script copies it into `/hdd/` inside the container with the same basename.
- **Receivers**: The test harness sets `PAYLOAD_FILE`/`TEST_FILE` env vars before starting in-container receivers. The stock `receiver.py` and the provided Python sender templates consume these to find both the source file (`/hdd/<name>`) and the output (`/hdd/<name>_received.*`).

### Skeleton sender for smoke testing

Need to verify Docker, the simulator, and the receiver are all behaving before you start coding? Use the baked-in skeleton:

```bash
cd docker
./test_sender.sh sender_skeleton.py [payload.zip]
```

It sends two quick demo packets (plus the EOF marker) and prints metrics so you can confirm the end-to-end flow. Feel free to copy `docker/sender_skeleton.py` as a starting point for your own sender; it already demonstrates:

- how to read `PAYLOAD_FILE` / `TEST_FILE` from the environment
- how to format packets (`SEQ_ID` + payload) and parse ACK/FIN responses
- how to emit the CSV metrics line that the grading scripts expect

## What You'll Implement

Four congestion control algorithms:

1. **Stop-and-Wait** - Send one packet, wait for ACK (simplest)
2. **Sliding Window** - Send multiple packets up to a window size, wait for ACKs
3. **TCP Tahoe** - Slow start + congestion avoidance + fast retransmit
4. **TCP Reno** - Adds fast recovery to Tahoe for better performance
5. **Custom Protocol** - Design your own congestion control algorithm to beat TCP Reno

## Documentation

- **[SETUP.md](SETUP.md)** - Docker installation guide for all platforms
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions

## Project Structure

```
docker/
├── start-simulator.sh      # Start the receiver and network emulator (macOS/Linux)
├── start_sim.bat           # Start the receiver and network emulator (Windows)
├── test_sender.sh          # Test your sender (optional payload) - Bash
├── test_sender.bat         # Test your sender (optional payload) - Batch
├── receiver.py             # Pre-built receiver (DO NOT MODIFY)
├── training_profile.sh     # Network emulation script (DO NOT MODIFY)
├── docker-script.sh        # Container startup script
├── Dockerfile              # Container configuration
├── skeleton_sender.py      # Skeleton code for a sender
└── hdd/
    ├── file.zip            # File to transfer (~20 MB)
```

## Network Simulation

The shipping `training_profile.sh` drives a 5-phase traffic pattern by reshaping the loopback interface with `tc`. Each phase lasts 20–40 seconds before randomly switching, so you should expect long stretches of bufferbloat punctuated by shorter recovery periods.

| Phase | Scenario (from `training_profile.sh`)            | Bandwidth (kbps) | Base Delay (ms) | Loss (%)   | Queue Limit (packets) |
| ----- | ------------------------------------------------ | ---------------- | --------------- | ---------- | --------------------- |
| 1     | Moderate bottleneck, large queue                 | 1,200 – 2,500    | 60 – 110        | 0.20 – 0.60 | 40,000                |
| 2     | Tight bottleneck, aggressive queuing             | 600 – 1,400      | 80 – 140        | 0.25 – 0.70 | 50,000                |
| 3     | Light congestion / higher capacity               | 2,500 – 4,500    | 40 – 80         | 0.30 – 1.10 | 25,000                |
| 4     | Moderate capacity                                | 3,500 – 6,000    | 30 – 70         | 0.25 – 0.85 | 20,000                |
| 5     | Sudden squeeze to force instant queue build-up   | 800 – 1,400      | 70 – 120        | 0.20 – 0.70 | 45,000                |

All phases run over the `lo` interface, so you still test locally, but the HTB + netem stack enforces the above limits.

## Important Notes

⚠️ **You are NOT supposed to make changes to any file in this repository except your own sender implementations.**

Files you should NOT modify:

- `receiver.py` - Pre-built receiver
- `training_profile.sh` - Network emulation configuration
- `docker-script.sh` - Container startup logic
- `Dockerfile` - Container setup

## Getting Help

2. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
3. Review Week 7 discussion code: [receiver.py example](https://github.com/shaoormunir/ecs152a-fall-2025/blob/main/week7/code/receiver.py)
4. Post on course discussion board on Canvas
5. Attend office hours

## Additional Resources

- [TCP Congestion Control (RFC 5681)](https://datatracker.ietf.org/doc/html/rfc5681)
- [Docker Documentation](https://docs.docker.com/)

Good luck! 🚀
