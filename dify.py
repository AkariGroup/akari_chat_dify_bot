import json
from lib.dify_client.client import ChatClient

api_key = "app-IgrjyqIOEZrr9Qt9b35kfQbr"
base_url = "https://192.168.0.35/v1"

# Initialize ChatClient
print("OK1")
chat_client = ChatClient(api_key,base_url)

print("OK2")
# Create Chat Message using ChatClient
chat_response = chat_client.create_chat_message(inputs={}, query="Hello", user="user_id", response_mode="streaming")
print("OK3")
chat_response.raise_for_status()

print("OK4")
for line in chat_response.iter_lines(decode_unicode=True):
    line = line.split('data:', 1)[-1]
    if line.strip():
        line = json.loads(line.strip())
        print(line.get('answer'))
