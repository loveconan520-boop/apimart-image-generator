#!/usr/bin/env python3
"""测试视频生成 API"""

import requests
import json
import os

API_BASE = "https://api.apimart.ai/v1"
API_KEY = os.environ.get('APIMART_API_KEY', '')

if not API_KEY:
    print("错误: 请设置 APIMART_API_KEY 环境变量")
    exit(1)

# 测试文生视频
request_data = {
    "model": "doubao-seedance-2.0-fast",
    "prompt": "一只可爱的猫咪在草地上奔跑",
    "size": "1080x1920",
    "duration": 5,
    "resolution": "480p",
    "generate_audio": False
}

print("请求数据:")
print(json.dumps(request_data, indent=2, ensure_ascii=False))

print("\n发送请求...")
resp = requests.post(
    f"{API_BASE}/videos/generations",
    json=request_data,
    headers={'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'},
    timeout=60
)

print(f"\n响应状态: {resp.status_code}")
print(f"响应内容:")
try:
    data = resp.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
except:
    print(resp.text)
