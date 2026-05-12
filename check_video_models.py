import requests

headers = {'Authorization': 'Bearer sk-K6j8S971PxjDspBGX9igHzxCh6Z9d6fbH266Sj3jTp3rBBwC'}
resp = requests.get('https://api.apimart.ai/v1/models', headers=headers)
data = resp.json()

if data.get('code') == 200:
    print("=== Video Models ===")
    for m in data.get('data', []):
        model_id = m.get('id', '').lower()
        if 'video' in model_id or 'seedance' in model_id or 'kling' in model_id or 'wan' in model_id:
            print(f"{m.get('id')}: {m.get('name', 'N/A')}")
else:
    print('Error:', data)
