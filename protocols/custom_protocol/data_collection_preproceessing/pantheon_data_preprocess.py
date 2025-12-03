import numpy as np
import json
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib

'''
Preprocessing for online pantheon json data 
'''

# Helper function to naively label CWND status features: decrease, hold, increase
def label_action(prev, curr):
   dl = curr["delay"] - prev["delay"]
   dl_loss = curr["loss"] - prev["loss"]
   dl_tput = curr["tput"] - prev["tput"]

   # Decrease if delay or loss increases
   if dl_loss > 0 or dl > 0:
      return "decrease"

   # Increase if throughput increases and delay/loss don't increase
   if dl_tput > 0 and dl <= 0 and dl_loss <= 0:
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
   pantheon_samples = convert("pantheon.json")
