import requests

url = "http://localhost:8080/webhook/whatsapp"
data = {
    "From": "whatsapp:+254712345678",
    "To": "whatsapp:+14155238886",
    "Body": "Hello from local test",
    "NumMedia": "0",
    "MessageSid": "SM12345"
}

try:
    print(f"Sending POST to {url}...")
    response = requests.post(url, data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
