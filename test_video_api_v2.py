#!/usr/bin/env python3
"""测试 APIMart 视频生成 API 参数格式"""

import requests
import json
import time

API_KEY = "sk-K6j8S971PxjDspBGX9igHzxCh6Z9d6fbH266Sj3jTp3rBBwC"
API_BASE = "https://api.apimart.ai/v1"

# 创建不读取系统代理环境的 session
session = requests.Session()
session.trust_env = False

def test_text_to_video():
    """测试文生视频"""
    print("=" * 60)
    print("测试 1: 文生视频")
    print("=" * 60)
    
    payload = {
        "model": "doubao-seedance-2.0",
        "prompt": "一只小猫对着镜头打哈欠",
        "resolution": "720p",
        "size": "16:9",
        "duration": 5,
        "generate_audio": False
    }
    
    print(f"请求参数: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    resp = session.post(
        f"{API_BASE}/videos/generations",
        json=payload,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        timeout=60
    )
    
    print(f"状态码: {resp.status_code}")
    print(f"响应: {resp.text}")
    
    data = resp.json()
    if data.get("code") == 200:
        task_id = data["data"][0]["task_id"]
        print(f"任务提交成功: {task_id}")
        return task_id
    else:
        print(f"错误: {data.get('message', '未知错误')}")
        return None

def test_image_to_video():
    """测试图生视频 - 使用公网图片URL"""
    print("\n" + "=" * 60)
    print("测试 2: 图生视频")
    print("=" * 60)
    
    # 使用一个公网可访问的图片URL
    image_url = "https://images.unsplash.com/photo-1574158622682-e40e69881006?w=800"
    
    payload = {
        "model": "doubao-seedance-2.0",
        "prompt": "小猫站起来走向镜头",
        "image_urls": [image_url],
        "resolution": "720p",
        "size": "16:9",
        "duration": 5,
        "generate_audio": False
    }
    
    print(f"请求参数: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    resp = session.post(
        f"{API_BASE}/videos/generations",
        json=payload,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        timeout=60
    )
    
    print(f"状态码: {resp.status_code}")
    print(f"响应: {resp.text}")
    
    data = resp.json()
    if data.get("code") == 200:
        task_id = data["data"][0]["task_id"]
        print(f"任务提交成功: {task_id}")
        return task_id
    else:
        print(f"错误: {data.get('message', '未知错误')}")
        return None

def test_video_to_video():
    """测试视频生视频 - 使用公网视频URL"""
    print("\n" + "=" * 60)
    print("测试 3: 视频生视频")
    print("=" * 60)
    
    # 使用一个公网可访问的视频URL
    video_url = "https://www.w3schools.com/html/mov_bbb.mp4"
    
    payload = {
        "model": "doubao-seedance-2.0",
        "prompt": "将视频风格转换为动漫风格",
        "video_urls": [video_url],
        "resolution": "720p",
        "size": "16:9",
        "duration": 5,
        "generate_audio": False
    }
    
    print(f"请求参数: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    resp = session.post(
        f"{API_BASE}/videos/generations",
        json=payload,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        timeout=60
    )
    
    print(f"状态码: {resp.status_code}")
    print(f"响应: {resp.text}")
    
    data = resp.json()
    if data.get("code") == 200:
        task_id = data["data"][0]["task_id"]
        print(f"任务提交成功: {task_id}")
        return task_id
    else:
        print(f"错误: {data.get('message', '未知错误')}")
        return None

def query_task(task_id):
    """查询任务状态"""
    print(f"\n查询任务状态: {task_id}")
    
    resp = session.get(
        f"{API_BASE}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=30
    )
    
    print(f"状态码: {resp.status_code}")
    print(f"响应: {resp.text}")

if __name__ == "__main__":
    print("APIMart 视频生成 API 测试")
    print("=" * 60)
    
    # 测试文生视频
    task1 = test_text_to_video()
    if task1:
        time.sleep(2)
        query_task(task1)
    
    # 测试图生视频
    task2 = test_image_to_video()
    if task2:
        time.sleep(2)
        query_task(task2)
    
    # 测试视频生视频
    task3 = test_video_to_video()
    if task3:
        time.sleep(2)
        query_task(task3)
