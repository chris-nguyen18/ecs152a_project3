#!/usr/bin/env python3 -u

from __future__ import annotations

# imports for model
import numpy as np
import json
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib

DATA_FILE = "pantheon.json"

def convert(json_file):
   samples = []
   with open(json_file, "r") as f:
      data = json.load(f)

      for label, runs in data.items():          
         for run_id, flows in runs.items():    
            for flow_id, metrics in flows.items():     
               if "loss" not in metrics or "delay" not in metrics or "tput" not in metrics:
                  continue
                  
               samples.append({
                  "loss": metrics["loss"],
                  "delay": metrics["delay"],
                  "throughput": metrics["tput"],  
                  "label": label
               })
   
   return samples


def data_preprocess(samples):
   X = []
   y = []

   for s in samples:
      if s["loss"] is None or s["delay"] is None or s["throughput"] is None:
         continue
      if s["loss"] < 0 or s["delay"] < 0 or s["throughput"] < 0:
         continue

      X.append([s["loss"], s["delay"], s["throughput"]])
      y.append(s["label"])

   X = np.array(X)

   encoder = LabelEncoder()
   y_encoded = encoder.fit_transform(y)

   scaler = StandardScaler()
   X_scaled = scaler.fit_transform(X)

   return X_scaled, y_encoded, encoder, scaler


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
   return model

def print_model_equations(model, encoder):
   classes = encoder.classes_
   coef = model.coef_
   intercept = model.intercept_

   for idx, cls in enumerate(classes):
      w = coef[idx]
      b = intercept[idx]

      print(f"\nClass '{cls}' equation:")
      print(f"   score_{cls}(x) = "
            f"{w[0]:.6f} * loss + "
            f"{w[1]:.6f} * delay + "
            f"{w[2]:.6f} * throughput "
            f"+ ({b:.6f})")


if __name__ == "__main__":
   samples = convert("pantheon.json")
   X_scaled, y_encoded, encoder, scaler = data_preprocess(samples)

   np.save("X.npy", X_scaled)
   np.save("y.npy", y_encoded)

   joblib.dump(encoder, "label_encoder.pkl")
   joblib.dump(scaler, "scaler.pkl")

   model = train_model()
   encoder = joblib.load("label_encoder.pkl")

   print_model_equations(model, encoder)
