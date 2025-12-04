#!/usr/bin/env python3 -u

from __future__ import annotations

# imports for model
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import pandas as pd

def data_preprocess(df):
   X = df[["loss", "delay", "throughput"]].values
   y = df["label"].values

   scaler = StandardScaler()

   # Scale the features using the entire combined dataset
   X_scaled = scaler.fit_transform(X)

   encoder = LabelEncoder()

   custom_label_mapping = {'decrease': 0, 'hold': 1, 'increase': 2}
   df['label'] = df['label'].map(custom_label_mapping)

   y_encoded = df['label'].values

   return X_scaled, y_encoded, scaler, encoder

def train_model(X, y):
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

def evaluate_model(model, X_test, y_test):
   y_pred = model.predict(X_test)

   # Calculate evaluation metrics
   accuracy = accuracy_score(y_test, y_pred)
   precision = precision_score(y_test, y_pred, average='weighted')  # 'weighted' handles imbalanced classes
   recall = recall_score(y_test, y_pred, average='weighted')
   f1 = f1_score(y_test, y_pred, average='weighted')

   print(f"Accuracy: {accuracy:.4f}")
   print(f"Precision: {precision:.4f}")
   print(f"Recall: {recall:.4f}")
   print(f"F1-Score: {f1:.4f}")

if __name__ == "__main__":
   pantheon_df = joblib.load("../pantheon_df.pkl")
   #reno_df = joblib.load("../reno_df.pkl")

   #combined_df = pd.concat([pantheon_df, reno_df], ignore_index=True)
   #print(combined_df.head())   

   # change to combined later
   X_scaled, y_encoded, scaler, encoder = data_preprocess(pantheon_df) 

   X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)

   joblib.dump(encoder, "label_encoder.pkl")
   joblib.dump(scaler, "scaler.pkl")

   np.save("X_train.npy", X_train)
   np.save("y_train.npy", y_train)
   np.save("X_test.npy", X_test)
   np.save("y_test.npy", y_test)

   # Train the model with the training data
   model = train_model(X_train, y_train)

   # Create a label encoder manually for printing the model's equations
   encoder = LabelEncoder()
   encoder.fit(['decrease', 'hold', 'increase'])  # Manually fit the encoder to the custom labels

   # Print the model's coefficients for each class
   print_model_equations(model, encoder)

   # Evaluate the model on the test data
   evaluate_model(model, X_test, y_test)