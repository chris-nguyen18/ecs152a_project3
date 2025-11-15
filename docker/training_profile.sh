#!/bin/bash
bandwidth=50000
delay=50
pl=0.1


tc qdisc add dev lo root handle 1: htb default 1
tc class add dev lo parent 1: classid 1:1 htb rate ${bandwidth}kbit ceil ${bandwidth}kbit
tc qdisc add dev lo parent 1:1 handle 10: netem delay ${delay}ms loss ${pl}%

phase=1
counter=0
phase_duration=$((10 + RANDOM % 11))  # Random duration 10-20 seconds

echo "Starting network simulation with random phases..."

while true; do
    counter=$((counter + 1))
    
    case $phase in
        1)  
            bandwidth=$((45000 + RANDOM % 10000))  # 45-55 Mbps
            delay=$((40 + RANDOM % 30))             # 40-70ms
            pl=$(echo "scale=2; $(($RANDOM % 30)) / 100" | bc)  # 0-0.3%
            ;;
            
        2)  
            bandwidth=$((8000 + RANDOM % 5000))     # 8-13 Mbps
            delay=$((60 + RANDOM % 40))             # 60-100ms
            pl=$(echo "scale=2; 0.5 + $(($RANDOM % 150)) / 100" | bc)  # 0.5-2%
            ;;
            
        3)  
            bandwidth=$((25000 + RANDOM % 15000))   # 25-40 Mbps
            delay=$((100 + RANDOM % 150))           # 100-250ms
            pl=$(echo "scale=2; $(($RANDOM % 100)) / 100" | bc)  # 0-1%
            ;;
            
        4)  
            bandwidth=$((35000 + RANDOM % 10000))   # 35-45 Mbps
            delay=$((50 + RANDOM % 50))             # 50-100ms
            if [ $((RANDOM % 5)) -eq 0 ]; then
                pl=$((10 + RANDOM % 10))            # 10-20% loss burst
            else
                pl=$(echo "scale=2; $(($RANDOM % 20)) / 100" | bc)  # 0-0.2%
            fi
            ;;
            
        5)  
            bandwidth=$((40000 + RANDOM % 15000))   # 40-55 Mbps
            delay=$((30 + RANDOM % 40))             # 30-70ms
            pl=$(echo "scale=2; $(($RANDOM % 50)) / 100" | bc)  # 0-0.5%
            reorder_delay=$((delay / 4))
            reorder_prob=$((10 + RANDOM % 15))      # 10-25% reordering
            tc qdisc change dev lo parent 1:1 handle 10: netem \
                delay ${delay}ms ${reorder_delay}ms \
                reorder ${reorder_prob}% \
                loss ${pl}%
            ;;
    esac
    

    if [ $phase -ne 5 ]; then
        tc class change dev lo parent 1: classid 1:1 htb rate ${bandwidth}kbit ceil ${bandwidth}kbit
        tc qdisc change dev lo parent 1:1 handle 10: netem delay ${delay}ms loss ${pl}%
    else
        tc class change dev lo parent 1: classid 1:1 htb rate ${bandwidth}kbit ceil ${bandwidth}kbit
    fi
    
    echo "Phase: $phase, Time: $counter/$phase_duration, BW: ${bandwidth}kbit, Delay: ${delay}ms, Loss: ${pl}%"

    if [ $counter -ge $phase_duration ]; then
        next_phase=$phase
        while [ $next_phase -eq $phase ]; do
            next_phase=$((1 + RANDOM % 5))
        done
        
        echo "=== Transitioning from Phase $phase to Phase $next_phase ==="
        phase=$next_phase
        counter=0
        phase_duration=$((10 + RANDOM % 11))  
    fi
    
    sleep 1
done