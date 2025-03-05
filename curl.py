import requests
import pandas as pd

# Define the API endpoint
url = "http://localhost:5000/api/change_managements/"

# Define headers
headers = {
    "authority": "sherlock-api-dev.pfizer.com",
    "accept": "application/json",
    "accept-language": "en-CA,en-US;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "origin": "http://localhost:3000",
    "pragma": "no-cache",
    "referer": "http://localhost:3000/",
    "sec-ch-ua": '"Not A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
}

# Define JSON payload
payload = {
    "constraints": [],
    "end_date": "2023-12-31T22:59:59.999Z",
    "start_date": "2021-12-31T23:00:00.000Z"
}

# Make the request
response = requests.post(url, json=payload, headers=headers, verify=False)  # verify=False to ignore SSL warnings

# Check if the response is valid
if response.status_code == 200:
    data = response.json()
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV (optional)
    df.to_csv("change_managements.csv", index=False)
    
    print(df.head())  # Display first few rows
else:
    print(f"Request failed with status code {response.status_code}: {response.text}")
