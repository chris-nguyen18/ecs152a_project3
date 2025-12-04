import numpy as np
import json
import pandas as pd
import joblib

'''
Preprocessing for online pantheon json data 
'''

# Helper function to naively label CWND status features: decrease, hold, increase
def label_action(prev, curr, timeout=False, delay_thresh=0.01, tput_thresh=0.01):
   dl = curr["delay"] - prev["delay"]
   dl_loss = curr["loss"] - prev["loss"]
   dl_tput = curr["tput"] - prev["tput"]

   if timeout or dl_loss > 0 or dl > delay_thresh:
      return "decrease"
   if dl_tput > tput_thresh and dl <= delay_thresh and dl_loss <= 0:
      return "increase"
   return "hold"

# 
def convert(json_file):
   samples = []
   with open(json_file, "r") as f:
      data = json.load(f)

      for algo_label, runs in data.items():
         for run_id, flows in runs.items():

               # sort keys so all goes last
               ordered_keys = sorted(
                  flows.keys(),
                  key=lambda x: float("inf") if x=="all" else int(x)
               )

               # initialize flow
               prev_key = ordered_keys[0]
               prev = flows[prev_key]

               for k in ordered_keys[1:]:
                  curr = flows[k]

                  # Skip rows with missing fields
                  if not all(m in prev for m in ("loss","delay","tput")): 
                     prev = curr
                     continue
                  if not all(m in curr for m in ("loss","delay","tput")):
                     prev = curr
                     continue

                  # Feature extraction
                  features = {
                     "loss": prev["loss"],
                     "delay": prev["delay"],
                     "throughput": prev["tput"]
                  }

                  action = label_action(prev, curr)

                  samples.append({
                     "loss": features["loss"],
                     "delay": features["delay"],
                     "throughput": features["throughput"],
                     "label": action
                  })

                  prev = curr

   return samples

if __name__ == "__main__":

   pantheon_samples = convert("data/pantheon.json")
   df = pd.DataFrame(pantheon_samples)
   print(df.head())

   # save dataframe
   joblib.dump(df, "pantheon_df.pkl")