import os
import requests
from dotenv import load_dotenv

load_dotenv()

response = requests.post(
    f"{os.getenv('SUPABASE_URL')}/functions/v1/trigger-crawler",
    headers={
        'Authorization': f"Bearer {os.getenv('SUPABASE_ANON_KEY')}"
    }
)

print("回應狀態碼:", response.status_code)
print("回應內容:", response.json())