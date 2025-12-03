import statistics 

# stop and wait
# fill in with full simulations
stop_and_wait_results = {
   "stop_and_wait": {
      "runs": [
         {"run": 1, "throughput": 6916.7456166, "avg_delay": 0.1252654, "avg_jitter": 0.0032775, "score": 4856.3759529},
         {"run": 2, "throughput": 7326.5278396, "avg_delay": 0.1190395, "avg_jitter": 0.0051026, "score": 3233.9509907},
         {"run": 3, "throughput": 7793.6016608, "avg_delay": 0.1345394, "avg_jitter": 0.0039352, "score": 4072.1876596},
         {"run": 4, "throughput": 7797.4453662, "avg_delay": 0.1089885, "avg_jitter": 0.0049641, "score": 3343.0802613},
         {"run": 5, "throughput": 7166.2268511, "avg_delay": 0.1198366, "avg_jitter": 0.0034363, "score": 4657.5479269},
         {"run": 6, "throughput": 7004.8859287, "avg_delay": 0.1228598, "avg_jitter": 0.0040974, "score": 3946.0550054},
         {"run": 7, "throughput": 7031.4239718, "avg_delay": 0.1216384, "avg_jitter": 0.0047392, "score": 3453.1277119},
         {"run": 8, "throughput": 7265.1363770, "avg_delay": 0.1174599, "avg_jitter": 0.0040247, "score": 4025.2370894},
         # start from here
         {"run": 9, "throughput": 7859.8121666, "avg_delay": 0.1080938, "avg_jitter": 0.0030586, "score": 5228.2893431},
         {"run": 10, "throughput": 7821.4401048, "avg_delay": 0.1086299, "avg_jitter": 0.0019803, "score": 7897.0425822},
      ],
      "averaged": {
         "Throughput_bytes_per_sec": 7794.070,
         "Avg_Delay_sec": 0.109009,
         "Avg_Jitter_sec": 0.003093,
         "Score": 5902.577
      }
   }
}

# print(stop_and_wait_results)

# sliding window
fixed_sliding_window_results = {
   "fixed_sliding_window": {
      "runs": [
         {"run": 1, "throughput": 86365.9821651, "avg_delay": 0.4358238, "avg_jitter": 0.0013903, "score": 10869.1819877},
         {"run": 2, "throughput": 78002.8487925, "avg_delay": 0.4676507, "avg_jitter": 0.0028041, "score": 5424.1301693},
         {"run": 3, "throughput": 75917.7347883, "avg_delay": 0.4916577, "avg_jitter": 0.0030955, "score": 4916.9189382},
         {"run": 4, "throughput": 75159.9925763, "avg_delay": 0.4775255, "avg_jitter": 0.0024224, "score": 6265.6095897},
         {"run": 5, "throughput": 92057.9442681, "avg_delay": 0.3662451, "avg_jitter": 0.0013502, "score": 11205.0041653},
         {"run": 6, "throughput": 70298.0908846, "avg_delay": 0.5149054, "avg_jitter": 0.0028323, "score": 5364.0488978},
         {"run": 7, "throughput": 76842.3082031, "avg_delay": 0.4645461, "avg_jitter": 0.0020507, "score": 7389.8464322},
         {"run": 8, "throughput": 74444.6610137, "avg_delay": 0.4832388, "avg_jitter": 0.0028638, "score": 5310.2803791},
         {"run": 9, "throughput": 78942.5605268, "avg_delay": 0.4361074, "avg_jitter": 0.0017682, "score": 8563.5386854},
         {"run": 10, "throughput": 84214.7935395, "avg_delay": 0.4158211, "avg_jitter": 0.0013480, "score": 11211.8221086},
      ],
      "averaged": {
         "Throughput_bytes_per_sec": 79224.692,
         "Avg_Delay_sec": 0.455352,
         "Avg_Jitter_sec": 0.002193,
         "Score": 7652.038
      }
   }
}


# tcp tahoe

# tcp reno

# custom