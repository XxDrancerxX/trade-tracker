import time
import hmac
import hashlib
import base64
import requests
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

API_KEY = os.getenv("COINBASE_API_KEY")
API_SECRET = os.getenv("COINBASE_API_SECRET")

# Step 1: prepare required values
timestamp = str(int(time.time()))
method = "GET"
request_path = "/api/v3/brokerage/accounts"  # Advanced Trade endpoint
body = ""

# Step 2: create prehash string
message = timestamp + method + request_path + body

# Step 3: create HMAC SHA256 signature
hmac_key = base64.b64decode(API_SECRET)
signature = hmac.new(hmac_key, message.encode('utf-8'), hashlib.sha256)
signature_b64 = base64.b64encode(signature.digest()).decode()

# Step 4: set headers
headers = {
    "CB-ACCESS-KEY": API_KEY,
    "CB-ACCESS-SIGN": signature_b64,
    "CB-ACCESS-TIMESTAMP": timestamp,
    "Content-Type": "application/json"
}

# Step 5: send request
url = f"https://api.coinbase.com{request_path}"
response = requests.get(url, headers=headers)

print("Status Code:", response.status_code)
try:
    print("Response JSON:", response.json())
except Exception as e:
    print("Error decoding response:", response.text)
