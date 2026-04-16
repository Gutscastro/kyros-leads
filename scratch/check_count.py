import os
import requests
from dotenv import load_dotenv

load_dotenv('config/.env')
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

h = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Prefer': 'count=exact'
}

r = requests.get(f"{url}/rest/v1/leads_prospeccao?status=eq.novo&select=id", headers=h)
print(f"PENDENTES: {r.headers.get('Content-Range')}")
