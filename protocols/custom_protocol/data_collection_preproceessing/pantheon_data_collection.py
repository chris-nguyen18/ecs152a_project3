import requests
import json
import os

'''
Retrieves the Panthon dataset and saves it into a JSON file
'''

url = "https://s3.amazonaws.com/stanford-pantheon/real-world/GCE-Iowa/reports/2020-04-17T10-16-GCE-London-to-GCE-Iowa-5-runs-3-flows-pantheon-perf.json"

response = requests.get(url)
data = response.json()  

os.makedirs('data', exist_ok=True)
file_path = os.path.join('data', 'pantheon.json')

# Save to local JSON file
with open(file_path, "w") as f:
   json.dump(data, f, indent=4)

print(f"Saved as {file_path}")
