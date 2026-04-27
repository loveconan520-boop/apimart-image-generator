#!/usr/bin/env python3
"""测试网络连接问题"""

import requests
import socket
import os

API_KEY = 'sk-K6j8S971PxjDspBGX9igHzxCh6Z9d6fbH266Sj3jTp3rBBwC'

def test_direct():
    """直接测试 API"""
    print("=" * 50)
    print("测试 1: 直接访问 api.apimart.ai")
    print("=" * 50)
    try:
        resp = requests.post(
            'https://api.apimart.ai/v1/images/generations',
            json={'model': 'flux-2-pro', 'prompt': 'test', 'size': '1024x1024'},
            headers={'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'},
            timeout=10
        )
        print(f"[OK] 成功! Status: {resp.status_code}")
        print(f"Response: {resp.text[:200]}")
        return True
    except Exception as e:
        print(f"[ERR] 失败: {e}")
        return False

def test_proxy():
    """测试系统代理设置"""
    print("\n" + "=" * 50)
    print("测试 2: 检查系统代理")
    print("=" * 50)
    http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
    https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    
    if http_proxy or https_proxy:
        print(f"HTTP_PROXY: {http_proxy}")
        print(f"HTTPS_PROXY: {https_proxy}")
        print("[WARN] 检测到系统代理，可能干扰连接")
    else:
        print("[OK] 未检测到系统代理")

def test_dns():
    """测试 DNS 解析"""
    print("\n" + "=" * 50)
    print("测试 3: DNS 解析")
    print("=" * 50)
    try:
        ip = socket.gethostbyname('api.apimart.ai')
        print(f"[OK] api.apimart.ai -> {ip}")
    except Exception as e:
        print(f"[ERR] DNS 解析失败: {e}")

def test_with_no_proxy():
    """强制不走代理测试"""
    print("\n" + "=" * 50)
    print("测试 4: 强制不走代理")
    print("=" * 50)
    try:
        session = requests.Session()
        session.trust_env = False  # 忽略系统代理
        resp = session.post(
            'https://api.apimart.ai/v1/images/generations',
            json={'model': 'flux-2-pro', 'prompt': 'test', 'size': '1024x1024'},
            headers={'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'},
            timeout=10
        )
        print(f"[OK] 成功! Status: {resp.status_code}")
        return True
    except Exception as e:
        print(f"[ERR] 失败: {e}")
        return False

if __name__ == '__main__':
    test_proxy()
    test_dns()
    
    direct_ok = test_direct()
    if not direct_ok:
        print("\n直接连接失败，尝试绕过代理...")
        test_with_no_proxy()
    
    print("\n" + "=" * 50)
    print("诊断建议:")
    print("=" * 50)
    print("1. 如果测试 4 成功但测试 1 失败 -> 关闭系统代理")
    print("2. 如果都失败 -> 检查防火墙/杀毒软件")
    print("3. 临时关闭 Windows Defender 实时保护试试")
