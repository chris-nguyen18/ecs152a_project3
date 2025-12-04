import statistics 

def print_averaged(results: dict):
   # Get the top-level key as the name
   dict_name = next(iter(results.keys()))
   averaged = results[dict_name].get("averaged", {})

   print(f"Averaged results for '{dict_name}':")
   print("Throughput (bytes/sec):", averaged.get("Throughput_bytes_per_sec", "N/A"))
   print("Avg Delay (sec):", averaged.get("Avg_Delay_sec", "N/A"))
   print("Avg Jitter (sec):", averaged.get("Avg_Jitter_sec", "N/A"))
   print("Score:", averaged.get("Score", "N/A"))


def compute_std(results: dict):
   # Extract the runs list (assuming only one key like 'fixed_sliding_window')
   dict_name = next(iter(results.keys()))
   runs = next(iter(results.values()))["runs"]

   # Extract each measurement
   throughputs = [run["throughput"] for run in runs]
   avg_delays = [run["avg_delay"] for run in runs]
   avg_jitters = [run["avg_jitter"] for run in runs]
   scores = [run["score"] for run in runs]

   # Compute standard deviations
   print(f"Standard deviations for '{dict_name}':")
   print("Standard deviation of throughput:", statistics.stdev(throughputs))
   print("Standard deviation of avg_delay:", statistics.stdev(avg_delays))
   print("Standard deviation of avg_jitter:", statistics.stdev(avg_jitters))
   print("Standard deviation of score:", statistics.stdev(scores))


# stop and wait
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
         {"run": 9, "throughput": 7268.1474938, "avg_delay": 0.1179414, "avg_jitter": 0.0038142, "score": 4229.7391447},
         {"run": 10, "throughput": 7276.7957630, "avg_delay": 0.1177941, "avg_jitter": 0.0052769, "score": 3140.0033756},
      ],
      "averaged": {
         "Throughput_bytes_per_sec": 7149.384,
         "Avg_Delay_sec": 0.120536,
         "Avg_Jitter_sec": 0.004267,
         "Score": 3895.731
      }
   }
}

print("-------------------------------------------------------------------------")
print_averaged(stop_and_wait_results)
compute_std(stop_and_wait_results)
print("-------------------------------------------------------------------------")
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

print_averaged(fixed_sliding_window_results)
compute_std(fixed_sliding_window_results)
print("-------------------------------------------------------------------------")
# tcp tahoe
tcp_tahoe_results = {
    "tcp_tahoe": {
        "runs": [
            {"run": 1, "throughput": 4145.0042532, "avg_delay": 0.1676767, "avg_jitter": 0.0094962, "score": 1788.8013551},
            {"run": 2, "throughput": 2624.8649459, "avg_delay": 0.1032305, "avg_jitter": 0.0092766, "score": 1956.7771925},
            {"run": 3, "throughput": 3002.3459342, "avg_delay": 0.2103435, "avg_jitter": 0.0140132, "score": 1237.4804258},
            {"run": 4, "throughput": 2221.7430458, "avg_delay": 0.2012348, "avg_jitter": 0.0239504, "score": 801.1219808},
            {"run": 5, "throughput": 580.9267752, "avg_delay": 0.0872355, "avg_jitter": 0.0243654, "score": 1020.2829357},
            {"run": 6, "throughput": 1032.3598041, "avg_delay": 0.0929162, "avg_jitter": 0.0139976, "score": 1450.2330767},
            {"run": 7, "throughput": 4511.2279025, "avg_delay": 0.4147221, "avg_jitter": 0.0159788, "score": 1023.5798153},
            {"run": 8, "throughput": 2022.7456011, "avg_delay": 0.4612205, "avg_jitter": 0.0255716, "score": 663.4633428},
            {"run": 9, "throughput": 359.0659019, "avg_delay": 0.0978250, "avg_jitter": 0.0429830, "score": 712.3269659},
            {"run": 10, "throughput": 5645.7085557, "avg_delay": 0.3696113, "avg_jitter": 0.0123212, "score": 1312.4626093}
        ],
        "averaged": {
            "Throughput_bytes_per_sec": 2614.599,
            "Avg_Delay_sec": 0.220602,
            "Avg_Jitter_sec": 0.019195,
            "Score": 1196.653
        }
    }
}

print_averaged(tcp_tahoe_results)
compute_std(tcp_tahoe_results)
print("-------------------------------------------------------------------------")

# tcp reno
tcp_reno_results = {
    "tcp_reno": {
        "runs": [
            {"run": 1, "throughput": 49586.7859969, "avg_delay": 0.3093125, "avg_jitter": 0.0277325, "score": 654.0770036},
            {"run": 2, "throughput": 37554.3858767, "avg_delay": 0.2799875, "avg_jitter": 0.0220048, "score": 806.7278210},
            {"run": 3, "throughput": 83523.5588274, "avg_delay": 0.3109275, "avg_jitter": 0.0205182, "score": 843.6497432},
            {"run": 4, "throughput": 64471.1552495, "avg_delay": 0.5031979, "avg_jitter": 0.0265784, "score": 633.9549352},
            {"run": 5, "throughput": 60550.8195746, "avg_delay": 0.6114246, "avg_jitter": 0.0227396, "score": 716.9179874},
            {"run": 6, "throughput": 53811.3347244, "avg_delay": 0.1230520, "avg_jitter": 0.0184086, "score": 1099.3050389},
            {"run": 7, "throughput": 29842.5995726, "avg_delay": 1.3086654, "avg_jitter": 0.0262297, "score": 598.6821036},
            {"run": 8, "throughput": 85984.8568073, "avg_delay": 0.2137420, "avg_jitter": 0.0158068, "score": 1112.7313695},
            {"run": 9, "throughput": 40940.7586950, "avg_delay": 1.0155453, "avg_jitter": 0.0305131, "score": 526.1054909},
            {"run": 10, "throughput": 47701.0596403, "avg_delay": 0.6115449, "avg_jitter": 0.0267953, "score": 617.0730586}
        ],
        "averaged": {
            "Throughput_bytes_per_sec": 55396.731,
            "Avg_Delay_sec": 0.528740,
            "Avg_Jitter_sec": 0.023733,
            "Score": 760.922
        }
    }
}

print_averaged(tcp_reno_results)
compute_std(tcp_reno_results)
print("-------------------------------------------------------------------------")

# custom
custom_protocol_results = {
    "custom_protocol": {
        "runs": [
            {"run": 1, "throughput": 3110.3954627, "avg_delay": 0.1236642, "avg_jitter": 0.0039295, "score": 4100.9109344},
            {"run": 2, "throughput": 1771.6020437, "avg_delay": 0.2145506, "avg_jitter": 0.0057508, "score": 2772.6122375},
            {"run": 3, "throughput": 1165.2585541, "avg_delay": 0.1287821, "avg_jitter": 0.0008359, "score": 18218.4259806},
            {"run": 4, "throughput": 1993.7817465, "avg_delay": 0.6337517, "avg_jitter": 0.0140062, "score": 1127.1858651},
            {"run": 5, "throughput": 1268.6139565, "avg_delay": 0.2655381, "avg_jitter": 0.0065426, "score": 2426.0577282},
            {"run": 6, "throughput": 1598.8763665, "avg_delay": 0.3778821, "avg_jitter": 0.0090213, "score": 1756.5998481},
            {"run": 7, "throughput": 1643.4572563, "avg_delay": 0.1272424, "avg_jitter": 0.0008395, "score": 18143.7092133},
            {"run": 8, "throughput": 1318.0131434, "avg_delay": 0.1529757, "avg_jitter": 0.0008914, "score": 17057.2689675},
            {"run": 9, "throughput": 1545.5084326, "avg_delay": 0.3826545, "avg_jitter": 0.0095005, "score": 1671.6167884},
            {"run": 10, "throughput": 1990.0564674, "avg_delay": 0.3041146, "avg_jitter": 0.0081834, "score": 1949.0621882}
        ],
        "averaged": {
            "Throughput_bytes_per_sec": 1740.556,
            "Avg_Delay_sec": 0.271116,
            "Avg_Jitter_sec": 0.005950,
            "Score": 6922.345
        }
    }
}

print_averaged(custom_protocol_results)
compute_std(custom_protocol_results)
print("-------------------------------------------------------------------------")