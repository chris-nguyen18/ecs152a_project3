import requests
import json

url = "https://s3.amazonaws.com/stanford-pantheon/real-world/GCE-Iowa/reports/2020-04-17T10-16-GCE-London-to-GCE-Iowa-5-runs-3-flows-pantheon-perf.json"

response = requests.get(url)
data = response.json()  

# Save to local JSON file
with open("pantheon.json", "w") as f:
   json.dump(data, f, indent=4)

print("Saved as pantheon.json")
