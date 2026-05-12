#!/usr/bin/env python3
"""
APIMart Image Generator - 一体化应用
支持文生图 + 图生图 + 视频生成
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import requests
import os
import webbrowser
import threading
import base64
import io
import hashlib
import time
import traceback
import socket
import subprocess
from urllib.parse import parse_qs, urlparse

# 创建不读取系统代理环境的 session
requests_session = requests.Session()
requests_session.trust_env = False

API_BASE = "https://api.apimart.ai/v1"

# Cloudinary 配置
CLOUDINARY_CLOUD_NAME = "di2xsvfti"
CLOUDINARY_API_KEY = "884691543767275"
CLOUDINARY_API_SECRET = "n7ha309rH9nSVDbIDMMOCgsXl8E"

# 初始化 Cloudinary
import cloudinary
import cloudinary.uploader
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)

ACCESS_PASSWORD = "athena80127678!"

HTML_CONTENT = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 图像生成器 - APIMart</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #f97316;
            --primary-light: #fb923c;
            --primary-dark: #ea580c;
            --secondary: #06b6d4;
            --accent: #a855f7;
            --bg-dark: #0a0a0f;
            --bg-card: rgba(30, 30, 40, 0.85);
            --bg-input: rgba(40, 40, 55, 0.9);
            --border: rgba(255, 255, 255, 0.15);
            --text-primary: #ffffff;
            --text-secondary: #a0aec0;
            --text-muted: #718096;
            --success: #48bb78;
            --warning: #ed8936;
            --error: #fc8181;
            --shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8);
            --glow: 0 0 50px rgba(249, 115, 22, 0.4);
        }
        [data-theme="light"] {
            --primary: #ea580c;
            --primary-light: #f97316;
            --primary-dark: #c2410c;
            --secondary: #0891b2;
            --accent: #7c3aed;
            --bg-dark: #f1f5f9;
            --bg-card: #ffffff;
            --bg-input: #f8fafc;
            --border: rgba(0, 0, 0, 0.12);
            --text-primary: #0f172a;
            --text-secondary: #334155;
            --text-muted: #64748b;
            --success: #16a34a;
            --warning: #d97706;
            --error: #dc2626;
            --shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.2);
            --glow: 0 0 30px rgba(249, 115, 22, 0.2);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background:
                radial-gradient(ellipse at 20% 0%, rgba(249, 115, 22, 0.15) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 0%, rgba(168, 85, 247, 0.1) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 100%, rgba(6, 182, 212, 0.08) 0%, transparent 50%),
                linear-gradient(180deg, #0f0a1a 0%, #0a0a0f 50%, #0a0f1a 100%);
            min-height: 100vh;
            padding: 24px;
            color: var(--text-primary);
            font-size: 15px;
            line-height: 1.6;
            transition: background 0.5s ease, color 0.3s ease;
        }
        [data-theme="light"] body {
            background:
                radial-gradient(ellipse at 20% 0%, rgba(249, 115, 22, 0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 0%, rgba(168, 85, 247, 0.06) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 100%, rgba(6, 182, 212, 0.05) 0%, transparent 50%),
                linear-gradient(180deg, #f8fafc 0%, #ffffff 50%, #f1f5f9 100%);
        }
        .container { max-width: 1000px; margin: 0 auto; animation: fadeIn 0.6s ease-out; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        .header { text-align: center; margin-bottom: 40px; padding: 20px 0; }
        .logo { display: inline-flex; align-items: center; gap: 12px; margin-bottom: 12px; }
        .logo-icon {
            width: 56px; height: 56px;
            background: linear-gradient(135deg, #f97316 0%, #ec4899 50%, #8b5cf6 100%);
            border-radius: 16px; display: flex; align-items: center; justify-content: center;
            font-size: 28px;
            box-shadow: 0 0 30px rgba(249, 115, 22, 0.5), 0 0 60px rgba(236, 72, 153, 0.3);
            animation: pulse 2s ease-in-out infinite;
        }
        @keyframes pulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.05); } }
        h1 { font-size: 36px; font-weight: 800;
            background: linear-gradient(135deg, #fff 0%, var(--primary-light) 30%, var(--secondary) 70%, var(--accent) 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
            letter-spacing: -0.02em; text-shadow: 0 0 60px rgba(249, 115, 22, 0.3);
        }
        [data-theme="light"] h1 {
            background: linear-gradient(135deg, #1e293b 0%, #f97316 30%, #06b6d4 70%, #8b5cf6 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
        }
        .subtitle { color: var(--text-secondary); font-size: 15px; font-weight: 400; }
        [data-theme="light"] .subtitle { color: #64748b; }
        .card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 20px; padding: 28px; margin-bottom: 24px; backdrop-filter: blur(20px); box-shadow: var(--shadow); transition: all 0.3s ease; }
        .card:hover { border-color: rgba(249, 115, 22, 0.3); }
        [data-theme="light"] .card { backdrop-filter: blur(10px); border: 1px solid rgba(0, 0, 0, 0.1); box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
        [data-theme="light"] .card:hover { border-color: rgba(249, 115, 22, 0.4); box-shadow: 0 15px 50px -10px rgba(0,0,0,0.15); }
        .tabs { display: flex; gap: 8px; margin-bottom: 28px; background: rgba(0,0,0,0.5); padding: 6px; border-radius: 14px; border: 1px solid var(--border); }
        [data-theme="light"] .tabs { background: rgba(255,255,255,0.9); border: 1px solid rgba(0,0,0,0.1); }
        .tab { flex: 1; padding: 12px 20px; background: transparent; border: none; border-radius: 10px; color: var(--text-secondary); font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.3s ease; width: auto; }
        .tab:hover { color: var(--text-primary); }
        .tab.active { background: linear-gradient(135deg, rgba(249,115,22,0.9) 0%, rgba(236,72,153,0.8) 100%); color: #fff; box-shadow: 0 4px 20px rgba(249,115,22,0.4); border: 1px solid rgba(249,115,22,0.5); }
        .mode-tabs { display: flex; gap: 12px; margin-bottom: 28px; flex-wrap: wrap; }
        .mode-tab { flex: 1; min-width: 100px; padding: 14px 12px; background: var(--bg-input); border: 1px solid var(--border); border-radius: 14px; color: var(--text-secondary); font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; gap: 6px; }
        [data-theme="light"] .mode-tab { background: #ffffff; border: 1px solid rgba(0,0,0,0.12); color: #475569; }
        .mode-tab:hover { border-color: rgba(249,115,22,0.5); color: var(--text-primary); }
        .mode-tab.active { background: linear-gradient(135deg, rgba(249,115,22,0.9) 0%, rgba(236,72,153,0.8) 50%, rgba(139,92,246,0.7) 100%); border-color: #f97316; color: #fff; box-shadow: 0 4px 20px rgba(249,115,22,0.35); }
        .form-group { margin-bottom: 24px; }
        label { display: block; color: var(--text-secondary); margin-bottom: 10px; font-size: 14px; font-weight: 500; }
        [data-theme="light"] label { color: #475569; }
        textarea, input, select { width: 100%; padding: 14px 16px; border: 1px solid var(--border); border-radius: 12px; background: var(--bg-input); color: var(--text-primary); font-size: 15px; font-family: inherit; transition: all 0.3s ease; }
        [data-theme="light"] textarea, [data-theme="light"] input, [data-theme="light"] select { border: 1px solid rgba(0,0,0,0.15); box-shadow: 0 2px 8px rgba(0,0,0,0.04); background: #ffffff; color: #1e293b; }
        textarea { min-height: 120px; resize: vertical; line-height: 1.6; }
        textarea:focus, input:focus, select:focus { outline: none; border-color: #f97316; background: rgba(249,115,22,0.08); box-shadow: 0 0 0 3px rgba(249,115,22,0.15), 0 0 20px rgba(249,115,22,0.1); }
        [data-theme="light"] textarea:focus, [data-theme="light"] input:focus, [data-theme="light"] select:focus { background: #fff7ed; }
        textarea::placeholder, input::placeholder { color: var(--text-muted); }
        [data-theme="light"] textarea::placeholder, [data-theme="light"] input::placeholder { color: #94a3b8; }
        .row { display: flex; gap: 20px; } .col { flex: 1; }
        button { width: 100%; padding: 16px 24px; border: none; border-radius: 12px; font-size: 15px; font-weight: 600; cursor: pointer; transition: all 0.3s ease; font-family: inherit; }
        .btn-primary { background: linear-gradient(135deg, #f97316 0%, #ec4899 50%, #8b5cf6 100%); color: white; box-shadow: 0 4px 25px rgba(249,115,22,0.5), 0 0 40px rgba(236,72,153,0.2); position: relative; overflow: hidden; }
        .btn-primary::before { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent); transition: left 0.5s; }
        .btn-primary:hover::before { left: 100%; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 35px rgba(249,115,22,0.6), 0 0 60px rgba(236,72,153,0.3); }
        .btn-primary:disabled { background: #334155; cursor: not-allowed; transform: none; box-shadow: none; }
        .btn-secondary { background: var(--bg-input); color: var(--text-primary); border: 1px solid var(--border); padding: 12px 20px; font-size: 14px; }
        [data-theme="light"] .btn-secondary { background: #f1f5f9; border: 1px solid rgba(0,0,0,0.12); color: #334155; }
        .btn-secondary:hover { background: rgba(249,115,22,0.15); border-color: #f97316; color: #fb923c; }
        [data-theme="light"] .btn-secondary:hover { background: rgba(249,115,22,0.1); color: #ea580c; }
        .quick-prompts { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }
        .quick-prompt { padding: 8px 16px; background: var(--bg-input); border: 1px solid var(--border); border-radius: 20px; color: var(--text-secondary); font-size: 13px; cursor: pointer; transition: all 0.3s ease; }
        [data-theme="light"] .quick-prompt { background: #f1f5f9; border: 1px solid rgba(0,0,0,0.1); color: #475569; }
        .quick-prompt:hover { background: linear-gradient(135deg, rgba(249,115,22,0.9) 0%, rgba(236,72,153,0.8) 100%); border-color: #f97316; color: #fff; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(249,115,22,0.3); }
        .upload-area { border: 2px dashed var(--border); border-radius: 16px; padding: 48px; text-align: center; cursor: pointer; transition: all 0.3s ease; background: var(--bg-input); }
        .upload-area:hover { border-color: #f97316; background: linear-gradient(135deg, rgba(249,115,22,0.12) 0%, rgba(236,72,153,0.08) 100%); }
        .upload-area.has-file { border-style: solid; border-color: var(--success); background: rgba(16,185,129,0.1); }
        [data-theme="light"] .upload-area { background: #f8fafc; border-color: rgba(0,0,0,0.15); }
        [data-theme="light"] .upload-area:hover { background: #fff7ed; }
        [data-theme="light"] .upload-area.has-file { background: rgba(34,197,94,0.12); }
        .image-preview-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 12px; margin-top: 16px; }
        .preview-item { position: relative; aspect-ratio: 1; border-radius: 12px; overflow: hidden; border: 2px solid var(--border); transition: all 0.3s ease; }
        [data-theme="light"] .preview-item { border-color: rgba(0,0,0,0.1); }
        .preview-item:hover { border-color: var(--primary); transform: scale(1.05); }
        .preview-item img { width: 100%; height: 100%; object-fit: cover; }
        .preview-item .remove-btn { position: absolute; top: 4px; right: 4px; width: 24px; height: 24px; border-radius: 50%; background: rgba(239,68,68,0.9); border: none; color: white; font-size: 14px; cursor: pointer; display: flex; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.2s ease; padding: 0; }
        .preview-item:hover .remove-btn { opacity: 1; }
        .preview-item .remove-btn:hover { background: rgba(239,68,68,1); transform: scale(1.1); }
        .preview-item .image-index { position: absolute; bottom: 4px; left: 4px; background: rgba(0,0,0,0.6); color: white; font-size: 11px; padding: 2px 6px; border-radius: 4px; }
        .upload-actions { display: flex; gap: 10px; }
        .upload-icon { width: 72px; height: 72px; background: linear-gradient(135deg, #f97316 0%, #ec4899 50%, #06b6d4 100%); border-radius: 20px; display: flex; align-items: center; justify-content: center; font-size: 32px; margin: 0 auto 16px; box-shadow: 0 0 30px rgba(249,115,22,0.4), 0 0 50px rgba(6,182,212,0.2); animation: float 3s ease-in-out infinite; }
        @keyframes float { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
        .upload-text { color: var(--text-secondary); } .upload-text h4 { color: var(--text-primary); margin-bottom: 6px; font-weight: 500; } .upload-text p { font-size: 13px; }
        [data-theme="light"] .upload-text { color: #64748b; }
        [data-theme="light"] .upload-text h4 { color: #1e293b; }
        .strength-slider { width: 100%; margin-top: 12px; -webkit-appearance: none; height: 6px; border-radius: 3px; background: var(--bg-input); outline: none; }
        .strength-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 22px; height: 22px; border-radius: 50%; background: linear-gradient(135deg, #f97316 0%, #ec4899 50%, #8b5cf6 100%); cursor: pointer; box-shadow: 0 2px 15px rgba(249,115,22,0.5); border: 2px solid #fff; }
        .strength-labels { display: flex; justify-content: space-between; color: var(--text-muted); font-size: 12px; margin-top: 8px; }
        [data-theme="light"] .strength-labels { color: #64748b; }
        .result { text-align: center; animation: fadeIn 0.5s ease-out; } .result img { max-width: 100%; border-radius: 16px; margin-bottom: 20px; box-shadow: var(--shadow); }
        .loading { display: none; text-align: center; padding: 48px; }
        [data-theme="light"] .loading { color: #475569; }
        .loading.active { display: block; }
        .spinner { width: 60px; height: 60px; border: 4px solid rgba(249,115,22,0.15); border-top-color: #f97316; border-right-color: #ec4899; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px; box-shadow: 0 0 20px rgba(249,115,22,0.3); }
        [data-theme="light"] .spinner { border: 4px solid rgba(249,115,22,0.2); }
        @keyframes spin { to { transform: rotate(360deg); } }
        .progress-bar { width: 100%; height: 8px; background: var(--bg-input); border-radius: 4px; overflow: hidden; margin-top: 20px; }
        [data-theme="light"] .progress-bar { background: #e2e8f0; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #f97316 0%, #ec4899 50%, #06b6d4 100%); border-radius: 4px; transition: width 0.5s ease; box-shadow: 0 0 15px rgba(249,115,22,0.6); }
        .status-text { color: var(--text-secondary); margin-top: 12px; font-size: 14px; }
        [data-theme="light"] .status-text { color: #64748b; }
        .error { background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.4); color: #fca5a5; padding: 16px 20px; border-radius: 12px; margin-top: 20px; font-size: 14px; display: flex; align-items: center; gap: 10px; }
        [data-theme="light"] .error { background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); color: #dc2626; }
        .model-info { background: linear-gradient(135deg, rgba(249,115,22,0.15) 0%, rgba(236,72,153,0.1) 50%, rgba(6,182,212,0.08) 100%); border: 1px solid rgba(249,115,22,0.25); padding: 20px; border-radius: 14px; margin-top: 24px; font-size: 13px; color: var(--text-secondary); line-height: 1.8; }
        [data-theme="light"] .model-info { background: linear-gradient(135deg, rgba(249,115,22,0.08) 0%, rgba(236,72,153,0.05) 50%, rgba(6,182,212,0.03) 100%); border: 1px solid rgba(249,115,22,0.15); color: #475569; }
        .model-info strong { background: linear-gradient(135deg, #f97316 0%, #ec4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-weight: 700; }
        [data-theme="light"] .model-info strong { -webkit-text-fill-color: #ea580c; color: #ea580c; }
        .history { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; margin-top: 24px; }
        .history-item { background: var(--bg-input); border: 1px solid var(--border); border-radius: 14px; overflow: hidden; cursor: pointer; transition: all 0.3s ease; }
        [data-theme="light"] .history-item { background: #ffffff; border: 1px solid rgba(0,0,0,0.1); }
        .history-item:hover { transform: translateY(-4px); border-color: #f97316; box-shadow: 0 10px 30px rgba(0,0,0,0.4), 0 0 20px rgba(249,115,22,0.2); }
        [data-theme="light"] .history-item:hover { box-shadow: 0 10px 30px rgba(0,0,0,0.12), 0 0 20px rgba(249,115,22,0.15); }
        .history-item img { width: 100%; height: 160px; object-fit: cover; transition: transform 0.3s ease; }
        .history-item:hover img { transform: scale(1.05); }
        .history-item .prompt { padding: 12px 16px; font-size: 13px; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        [data-theme="light"] .history-item .prompt { color: #64748b; }
        .panel { display: none; } .panel.active { display: block; animation: fadeIn 0.4s ease-out; }
        #modelHint { display: block; margin-top: 8px; color: #fb923c; font-size: 12px; font-weight: 500; }
        [data-theme="light"] #modelHint { color: #ea580c; }
        .theme-toggle { position: fixed; top: 20px; right: 20px; width: 50px; height: 50px; border-radius: 50%; background: linear-gradient(135deg, #fbbf24 0%, #f97316 100%); border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 24px; box-shadow: 0 4px 20px rgba(251,191,36,0.4); transition: all 0.3s ease; z-index: 1000; }
        .theme-toggle:hover { transform: scale(1.1) rotate(15deg); box-shadow: 0 6px 30px rgba(251,191,36,0.6); }
        [data-theme="light"] .theme-toggle { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); box-shadow: 0 4px 20px rgba(99,102,241,0.4); }
        [data-theme="light"] .theme-toggle:hover { box-shadow: 0 6px 30px rgba(99,102,241,0.6); }
        @media (max-width: 640px) { .row { flex-direction: column; gap: 16px; } h1 { font-size: 24px; } .card { padding: 20px; } .mode-tabs { flex-direction: row; flex-wrap: wrap; } .mode-tab { min-width: 80px; font-size: 12px; padding: 10px 8px; } }
    </style>
</head>
<body>
    <!-- 密码验证层 -->
    <div id="passwordOverlay" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(135deg, #0a0a0f 0%, #1a0a2e 50%, #0f0a1a 100%); z-index: 10000; display: flex; align-items: center; justify-content: center;">
        <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 40px; max-width: 400px; width: 90%; text-align: center; backdrop-filter: blur(20px);">
            <div style="font-size: 48px; margin-bottom: 20px;">🔒</div>
            <h2 style="color: #fff; margin-bottom: 10px; font-size: 24px;">访问受限</h2>
            <p style="color: #94a3b8; margin-bottom: 30px; font-size: 14px;">请输入密码以继续使用</p>
            <input type="password" id="passwordInput" placeholder="输入密码..." style="width: 100%; padding: 14px 16px; border: 1px solid rgba(255,255,255,0.2); border-radius: 12px; background: rgba(0,0,0,0.3); color: #fff; font-size: 15px; margin-bottom: 16px; text-align: center;">
            <button onclick="checkPassword()" style="width: 100%; padding: 14px; background: linear-gradient(135deg, #f97316 0%, #ec4899 100%); border: none; border-radius: 12px; color: #fff; font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.3s;">进入系统</button>
            <p id="passwordError" style="color: #f43f5e; margin-top: 16px; font-size: 14px; display: none;">密码错误,请重试</p>
        </div>
    </div>

    <button class="theme-toggle" id="themeToggle" onclick="toggleTheme()" title="切换主题">☀️</button>
    <div class="container" id="mainContainer" style="display: none;">
        <div class="header">
            <div class="logo"><div class="logo-icon">✨</div><h1>AI 图像生成器</h1></div>
            <p class="subtitle">基于 APIMart 的强大 AI 图像/视频生成服务</p>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="switchTab('generate')">🎨 生成</button>
            <button class="tab" onclick="switchTab('history')">📷 历史</button>
            <button class="tab" onclick="switchTab('config')">⚙️ 设置</button>
        </div>

        <div id="generate-panel" class="panel active">
            <div class="card">
                <div class="mode-tabs">
                    <button class="mode-tab active" onclick="switchMode('text')" id="tab-text">文生图</button>
                    <button class="mode-tab" onclick="switchMode('image')" id="tab-image">图生图</button>
                    <button class="mode-tab" onclick="switchMode('video-text')" id="tab-video-text">文生视频</button>
                    <button class="mode-tab" onclick="switchMode('video-image')" id="tab-video-image">图生视频</button>
                    <button class="mode-tab" onclick="switchMode('video-keyframes')" id="tab-video-keyframes">首尾帧</button>
                    <button class="mode-tab" onclick="switchMode('video-video')" id="tab-video-video">视频生视频</button>
                </div>

                <div id="text-mode-panel">
                    <div class="form-group">
                        <label>描述你想要的内容</label>
                        <textarea id="prompt" placeholder="例如: 反骨西游海报,孙悟空金甲红袍..."></textarea>
                        <div class="quick-prompts">
                            <span class="quick-prompt" onclick="setPrompt('孙悟空')">孙悟空</span>
                            <span class="quick-prompt" onclick="setPrompt('杨戬')">杨戬</span>
                            <span class="quick-prompt" onclick="setPrompt('哪吒')">哪吒</span>
                            <span class="quick-prompt" onclick="setPrompt('反骨西游海报')">反骨西游</span>
                            <span class="quick-prompt" onclick="setPrompt('天庭场景')">天庭场景</span>
                        </div>
                    </div>
                </div>

                <div id="image-mode-panel" style="display: none;">
                    <div class="form-group">
                        <label>上传参考图 <span id="imageCount" style="color: var(--primary-light); font-size: 12px;">(0/5)</span></label>
                        <div class="upload-area" id="uploadArea" onclick="document.getElementById('imageInput').click()">
                            <div class="upload-text" id="uploadText">
                                <div class="upload-icon">🖼️</div>
                                <h4>点击上传图片</h4>
                                <p>或拖拽到此处, 最多5张</p>
                            </div>
                        </div>
                        <input type="file" id="imageInput" accept="image/*" multiple onchange="handleImageUpload(event)">
                        <div class="image-preview-grid" id="imagePreviewGrid" style="display: none;"></div>
                        <div class="upload-actions" id="uploadActions" style="display: none; margin-top: 12px;">
                            <button type="button" class="btn-secondary" onclick="clearAllImages()" style="width: auto; padding: 8px 16px; font-size: 13px;">清空</button>
                            <button type="button" class="btn-secondary" onclick="document.getElementById('imageInput').click()" style="width: auto; padding: 8px 16px; font-size: 13px;">继续添加</button>
                        </div>
                    </div>
                    <div class="form-group" id="imagePromptGroup">
                        <label>图片修改描述</label>
                        <textarea id="imagePrompt" placeholder="描述修改方式, 如: 转换为动漫风格..."></textarea>
                    </div>
                    <div class="form-group" id="strengthGroup">
                        <label>参考强度</label>
                        <input type="range" id="strength" class="strength-slider" min="0.1" max="1.0" step="0.1" value="0.7" oninput="updateStrengthLabel(this.value)">
                        <div class="strength-labels"><span>保留原图</span><span id="strengthValue">0.7</span><span>完全重绘</span></div>
                    </div>
                </div>

                <div id="video-upload-panel" style="display: none;">
                    <div class="form-group">
                        <label>参考视频URL（公网可访问）</label>
                        <input type="text" id="videoUrl" placeholder="https://example.com/video.mp4">
                    </div>
                    <div class="form-group">
                        <label>视频风格描述（可选）</label>
                        <textarea id="videoPrompt" placeholder="描述想要的视频风格..."></textarea>
                    </div>
                </div>

                <div id="keyframes-panel" style="display: none;">
                    <div class="form-group">
                        <label>首帧图片</label>
                        <input type="file" id="firstFrameInput" accept="image/*" onchange="handleFirstFrameUpload(event)" style="display: none;">
                        <div class="upload-area" id="firstFrameUploadArea" onclick="document.getElementById('firstFrameInput').click()" style="padding: 30px; border: 2px dashed var(--border); border-radius: 12px; text-align: center; cursor: pointer; margin-bottom: 12px;">
                            <div class="upload-icon">🖼️</div>
                            <h4>点击上传首帧图片</h4>
                            <p>作为视频的起始画面</p>
                        </div>
                        <div id="firstFramePreview" style="display: none; margin-top: 12px;">
                            <img id="firstFrameImg" style="max-width: 200px; max-height: 150px; border-radius: 8px; border: 1px solid var(--border);">
                            <button type="button" class="btn-secondary" onclick="clearFirstFrame()" style="margin-left: 12px; width: auto; padding: 8px 16px; font-size: 13px;">清除</button>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>尾帧图片</label>
                        <input type="file" id="lastFrameInput" accept="image/*" onchange="handleLastFrameUpload(event)" style="display: none;">
                        <div class="upload-area" id="lastFrameUploadArea" onclick="document.getElementById('lastFrameInput').click()" style="padding: 30px; border: 2px dashed var(--border); border-radius: 12px; text-align: center; cursor: pointer; margin-bottom: 12px;">
                            <div class="upload-icon">🖼️</div>
                            <h4>点击上传尾帧图片</h4>
                            <p>作为视频的结束画面</p>
                        </div>
                        <div id="lastFramePreview" style="display: none; margin-top: 12px;">
                            <img id="lastFrameImg" style="max-width: 200px; max-height: 150px; border-radius: 8px; border: 1px solid var(--border);">
                            <button type="button" class="btn-secondary" onclick="clearLastFrame()" style="margin-left: 12px; width: auto; padding: 8px 16px; font-size: 13px;">清除</button>
                        </div>
                    </div>
                </div>

                <div class="row" id="video-params" style="display: none;">
                    <div class="col">
                        <div class="form-group">
                            <label>视频质量</label>
                            <select id="videoResolution">
                                <option value="480p">480P</option>
                                <option value="720p" selected>720P</option>
                                <option value="1080p">1080P</option>
                            </select>
                        </div>
                    </div>
                    <div class="col">
                        <div class="form-group">
                            <label>视频时长 (5-15秒)</label>
                            <input type="number" id="videoDuration" min="5" max="15" value="5">
                        </div>
                    </div>
                    <div class="col">
                        <div class="form-group">
                            <label>有声视频</label>
                            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; text-transform: none; font-weight: normal;">
                                <input type="checkbox" id="generateAudio" style="width: 18px; height: 18px;">
                                <span>生成配套音频</span>
                            </label>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col">
                        <div class="form-group">
                            <label>图片质量</label>
                            <select id="imageQuality">
                                <option value="high" selected>高清 (High)</option>
                                <option value="medium">标准 (Medium)</option>
                                <option value="low">快速 (Low)</option>
                            </select>
                        </div>
                    </div>
                    <div class="col">
                        <div class="form-group">
                            <label>模型</label>
                            <select id="model" onchange="handleModelChange()">
                                <option value="gpt-image-2" selected>gpt-image-2 (推荐)</option>
                                <option value="image2.0">image2.0</option>
                                <option value="flux-2-pro">flux-2-pro</option>
                                <option value="doubao-seedance-2.0">doubao-seedance-2.0 (视频)</option>
                                <option value="doubao-seedance-2.0-fast">doubao-seedance-2.0-fast (视频)</option>
                                <option value="sora-2-pro">sora-2-pro (视频)</option>
                                <option value="kling-v3">kling-v3 (视频)</option>
                                <option value="veo3.1-quality">veo3.1-quality (视频)</option>
                                <option value="wan2.7">wan2.7 (视频)</option>
                            </select>
                            <small id="modelHint" style="display: none;">图生图模式强制使用 gpt-image-2 模型</small>
                        </div>
                    </div>
                    <div class="col">
                        <div class="form-group">
                            <label id="sizeLabel">图片尺寸</label>
                            <select id="size">
                                <option value="1:1" selected>正方形 1:1</option>
                                <option value="9:16">竖版 9:16</option>
                                <option value="16:9">横版 16:9</option>
                                <option value="4:3">横版 4:3</option>
                                <option value="3:4">竖版 3:4</option>
                            </select>
                        </div>
                    </div>
                </div>

                <button class="btn-primary" id="generateBtn" onclick="generate()">生成</button>

                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p id="loadingText">正在提交任务...</p>
                    <div class="progress-bar"><div class="progress-fill" id="progressFill" style="width: 0%"></div></div>
                    <p class="status-text" id="statusText">进度: 0%</p>
                </div>
            </div>

            <div class="card result" id="result" style="display: none;">
                <img id="resultImage" src="" alt="生成结果" style="display: block;">
                <video id="resultVideo" src="" controls crossorigin="anonymous" playsinline style="display: none; width: 100%; border-radius: 12px; margin-bottom: 16px;"></video>
                <button class="btn-primary" onclick="downloadResult()">下载</button>
            </div>

            <div class="error" id="error" style="display: none;"></div>

            <div class="model-info">
                <strong>使用提示</strong><br>
                • <b>文生图</b>: 输入文字描述, AI 从零生成图片, gpt-image-2 支持图片质量选项<br>
                • <b>图生图</b>: 上传参考图 + 描述, AI 基于原图修改, 强制使用 gpt-image-2<br>
                • <b>文生视频</b>: 输入描述生成视频, 5-15秒<br>
                • <b>图生视频</b>: 上传图片生成动态视频<br>
                • <b>首尾帧</b>: 上传首帧和尾帧图片生成过渡视频<br>
                • <b>视频生视频</b>: 输入公网可访问的视频URL进行风格转换<br>
                • <b>有声视频</b>: 勾选后可生成带音频的视频<br>
                • 图片/视频链接有效期 24 小时, 请及时下载保存
            </div>
        </div>

        <div id="history-panel" class="panel">
            <div class="card">
                <h3 style="color: var(--text-primary); margin-bottom: 20px;">生成历史</h3>
                <div class="history" id="history"></div>
            </div>
        </div>

        <div id="config-panel" class="panel">
            <div class="card">
                <h3 style="color: var(--text-primary); margin-bottom: 20px;">API 设置</h3>
                <div class="form-group">
                    <label>APIMart API Key</label>
                    <input type="password" id="apiKeyInput" placeholder="输入你的 APIMart API Key...">
                    <small style="color: var(--text-muted); font-size: 12px; margin-top: 6px; display: block;">如果服务器已配置默认 Key, 可留空使用服务器 Key</small>
                </div>
                <button class="btn-primary" onclick="saveApiKey()" style="width: auto; padding: 12px 24px;">保存设置</button>
                <p id="configStatus" style="margin-top: 12px; font-size: 14px;"></p>
            </div>
        </div>
    </div>

    <script>
        let currentMode = 'text';
        let uploadedImages = [];
        const MAX_IMAGES = 5;
        let firstFrameData = null;
        let lastFrameData = null;
        let currentImageUrl = '';
        let currentVideoUrl = '';
        let currentTaskId = '';

        // 密码验证 - 后端验证, 密码不暴露在前端
        async function checkPassword() {
            const input = document.getElementById('passwordInput').value;
            const error = document.getElementById('passwordError');
            try {
                const resp = await fetch('/api/auth', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ password: input })
                });
                const data = await resp.json();
                if (data.success) {
                    document.getElementById('passwordOverlay').style.display = 'none';
                    document.getElementById('mainContainer').style.display = 'block';
                    sessionStorage.setItem('authenticated', 'true');
                } else {
                    error.style.display = 'block';
                    document.getElementById('passwordInput').value = '';
                }
            } catch (e) {
                error.textContent = '验证失败, 请重试';
                error.style.display = 'block';
            }
        }

        // 初始化验证
        async function initAuth() {
            if (sessionStorage.getItem('authenticated') === 'true') {
                try {
                    const resp = await fetch('/api/auth/check');
                    const data = await resp.json();
                    if (data.valid) {
                        document.getElementById('passwordOverlay').style.display = 'none';
                        document.getElementById('mainContainer').style.display = 'block';
                    } else {
                        sessionStorage.removeItem('authenticated');
                    }
                } catch (e) {
                    sessionStorage.removeItem('authenticated');
                }
            }
        }

        // 回车提交密码
        document.addEventListener('DOMContentLoaded', () => {
            const passwordInput = document.getElementById('passwordInput');
            if (passwordInput) {
                passwordInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') checkPassword();
                });
            }
            initAuth();
            switchMode('text');
            loadHistory();
            loadApiKey();
        });

        function toggleTheme() {
            const body = document.body;
            const isLight = body.getAttribute('data-theme') === 'light';
            body.setAttribute('data-theme', isLight ? 'dark' : 'light');
            document.getElementById('themeToggle').textContent = isLight ? '☀️' : '🌙';
            localStorage.setItem('theme', isLight ? 'dark' : 'light');
        }

        // 初始化主题
        (function() {
            const saved = localStorage.getItem('theme');
            if (saved === 'light') {
                document.body.setAttribute('data-theme', 'light');
                setTimeout(() => {
                    const btn = document.getElementById('themeToggle');
                    if (btn) btn.textContent = '🌙';
                }, 100);
            }
        })();

        function setPrompt(text) {
            document.getElementById('prompt').value = text;
        }

        function switchTab(tab) {
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            document.getElementById(tab + '-panel').classList.add('active');
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            const tabIndex = { 'generate': 0, 'history': 1, 'config': 2 };
            document.querySelectorAll('.tab')[tabIndex[tab]].classList.add('active');
        }

        function switchMode(mode) {
            currentMode = mode;
            document.querySelectorAll('.mode-tab').forEach(t => t.classList.remove('active'));
            document.getElementById('tab-' + mode).classList.add('active');

            const modelSelect = document.getElementById('model');
            const modelHint = document.getElementById('modelHint');
            const sizeSelect = document.getElementById('size');
            const sizeLabel = document.getElementById('sizeLabel');
            const videoParams = document.getElementById('video-params');
            const generateBtn = document.getElementById('generateBtn');

            // 统一重置所有面板
            document.getElementById('text-mode-panel').style.display = 'none';
            document.getElementById('image-mode-panel').style.display = 'none';
            document.getElementById('video-upload-panel').style.display = 'none';
            document.getElementById('keyframes-panel').style.display = 'none';

            const isVideo = mode.startsWith('video');

            if (!isVideo) {
                document.getElementById('text-mode-panel').style.display = 'block';
                modelSelect.disabled = (mode === 'image');
                modelHint.style.display = (mode === 'image') ? 'block' : 'none';
                sizeLabel.textContent = '图片尺寸';
                sizeSelect.style.display = 'block';
                videoParams.style.display = 'none';
                generateBtn.textContent = '生成图片';
                setupImageSizes();
                if (mode === 'text') {
                    modelSelect.value = 'gpt-image-2';
                } else {
                    modelSelect.value = 'gpt-image-2';
                }
                updateImageQualityVisibility();
            } else {
                document.getElementById('text-mode-panel').style.display = 'block';
                if (mode === 'video-image') {
                    document.getElementById('image-mode-panel').style.display = 'block';
                    document.getElementById('imagePromptGroup').style.display = 'none';
                    document.getElementById('strengthGroup').style.display = 'none';
                    const grid = document.getElementById('imagePreviewGrid');
                    const actions = document.getElementById('uploadActions');
                    if (grid && uploadedImages.length > 0) grid.style.display = 'grid';
                    if (actions && uploadedImages.length > 0) actions.style.display = 'flex';
                } else if (mode === 'video-keyframes') {
                    document.getElementById('keyframes-panel').style.display = 'block';
                } else if (mode === 'video-video') {
                    document.getElementById('video-upload-panel').style.display = 'block';
                }
                modelSelect.disabled = false;
                modelHint.style.display = 'none';
                sizeLabel.textContent = '视频比例';
                setupVideoSizes();
                videoParams.style.display = 'flex';
                generateBtn.textContent = '生成视频';
                if (mode === 'video-text' || mode === 'video-image') {
                    modelSelect.value = 'doubao-seedance-2.0';
                }
                // 视频模式隐藏图片质量
                document.getElementById('imageQuality').closest('.form-group').style.display = 'none';
            }
        }

        function setupImageSizes() {
            const sizeSelect = document.getElementById('size');
            const model = document.getElementById('model').value;
            if (model === 'gpt-image-2') {
                sizeSelect.innerHTML = `
                    <option value="1:1" selected>正方形 1:1</option>
                    <option value="9:16">竖版 9:16</option>
                    <option value="16:9">横版 16:9</option>
                    <option value="4:3">横版 4:3</option>
                    <option value="3:4">竖版 3:4</option>
                `;
            } else {
                sizeSelect.innerHTML = `
                    <option value="1024x1024">正方形 1024×1024</option>
                    <option value="1024x1536">竖版 1024×1536</option>
                    <option value="1536x1024" selected>横版 1536×1024</option>
                `;
            }
        }

        function setupVideoSizes() {
            const sizeSelect = document.getElementById('size');
            sizeSelect.innerHTML = `
                <option value="9:16" selected>竖屏 9:16</option>
                <option value="16:9">横屏 16:9</option>
                <option value="1:1">方形 1:1</option>
                <option value="4:3">传统 4:3</option>
                <option value="3:4">竖向 3:4</option>
                <option value="21:9">超宽 21:9</option>
            `;
        }

        function updateImageQualityVisibility() {
            const model = document.getElementById('model').value;
            const qualityGroup = document.getElementById('imageQuality').closest('.form-group');
            qualityGroup.style.display = (model === 'gpt-image-2' && !currentMode.startsWith('video')) ? 'block' : 'none';
        }

        function handleModelChange() {
            if (currentMode === 'text' || currentMode === 'image') {
                setupImageSizes();
                updateImageQualityVisibility();
            }
        }

        function updateStrengthLabel(val) {
            document.getElementById('strengthValue').textContent = val;
        }

        function handleImageUpload(event) {
            const files = event.target.files;
            if (files.length > 0) handleFiles(files);
        }

        function handleFiles(files) {
            const remaining = MAX_IMAGES - uploadedImages.length;
            if (remaining <= 0) { alert('最多上传 ' + MAX_IMAGES + ' 张'); return; }
            const imageFiles = [];
            for (let i = 0; i < Math.min(files.length, remaining); i++) {
                if (files[i].type.startsWith('image/')) {
                    imageFiles.push(files[i]);
                } else {
                    alert(files[i].name + ' 不是图片, 已跳过');
                }
            }
            if (imageFiles.length === 0) return;
            let processed = 0;
            imageFiles.forEach(file => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    uploadedImages.push({
                        name: file.name,
                        base64: e.target.result.split(',')[1],
                        preview: e.target.result
                    });
                    processed++;
                    if (processed === imageFiles.length) updateImagePreview();
                };
                reader.readAsDataURL(file);
            });
        }

        function updateImagePreview() {
            const grid = document.getElementById('imagePreviewGrid');
            const uploadArea = document.getElementById('uploadArea');
            const actions = document.getElementById('uploadActions');
            const count = document.getElementById('imageCount');
            count.textContent = '(' + uploadedImages.length + '/' + MAX_IMAGES + ')';
            if (uploadedImages.length === 0) {
                grid.style.display = 'none';
                actions.style.display = 'none';
                uploadArea.style.display = 'block';
                uploadArea.classList.remove('has-file');
                return;
            }
            uploadArea.style.display = 'none';
            grid.style.display = 'grid';
            actions.style.display = 'flex';
            grid.innerHTML = '';
            uploadedImages.forEach((img, index) => {
                const item = document.createElement('div');
                item.className = 'preview-item';
                item.innerHTML = '<img src="' + img.preview + '"><button class="remove-btn" onclick="removeImage(' + index + ')">×</button><div class="image-index">' + (index + 1) + '</div>';
                grid.appendChild(item);
            });
        }

        function removeImage(index) {
            uploadedImages.splice(index, 1);
            updateImagePreview();
        }

        function clearAllImages() {
            uploadedImages = [];
            updateImagePreview();
        }

        function handleFirstFrameUpload(event) {
            const file = event.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (e) => {
                firstFrameData = e.target.result.split(',')[1];
                document.getElementById('firstFrameImg').src = e.target.result;
                document.getElementById('firstFramePreview').style.display = 'block';
                document.getElementById('firstFrameUploadArea').style.display = 'none';
            };
            reader.readAsDataURL(file);
        }

        function clearFirstFrame() {
            firstFrameData = null;
            document.getElementById('firstFramePreview').style.display = 'none';
            document.getElementById('firstFrameUploadArea').style.display = 'block';
            document.getElementById('firstFrameInput').value = '';
        }

        function handleLastFrameUpload(event) {
            const file = event.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (e) => {
                lastFrameData = e.target.result.split(',')[1];
                document.getElementById('lastFrameImg').src = e.target.result;
                document.getElementById('lastFramePreview').style.display = 'block';
                document.getElementById('lastFrameUploadArea').style.display = 'none';
            };
            reader.readAsDataURL(file);
        }

        function clearLastFrame() {
            lastFrameData = null;
            document.getElementById('lastFramePreview').style.display = 'none';
            document.getElementById('lastFrameUploadArea').style.display = 'block';
            document.getElementById('lastFrameInput').value = '';
        }

        // API Key 管理
        function loadApiKey() {
            const saved = localStorage.getItem('apimart_api_key');
            if (saved) document.getElementById('apiKeyInput').value = saved;
        }

        function saveApiKey() {
            const key = document.getElementById('apiKeyInput').value.trim();
            if (key) {
                localStorage.setItem('apimart_api_key', key);
            } else {
                localStorage.removeItem('apimart_api_key');
            }
            document.getElementById('configStatus').textContent = '设置已保存';
            document.getElementById('configStatus').style.color = 'var(--success)';
            setTimeout(() => { document.getElementById('configStatus').textContent = ''; }, 3000);
        }

        function getApiKey() {
            return localStorage.getItem('apimart_api_key') || '__SERVER_DEFAULT__';
        }

        // 主生成入口
        async function generate() {
            const apiKey = getApiKey();
            if (!apiKey) { showError('请先在"设置"中配置 API Key'); switchTab('config'); return; }

            const isVideo = currentMode.startsWith('video');
            const prompt = document.getElementById('prompt').value.trim();
            const size = document.getElementById('size').value;
            const model = document.getElementById('model').value;

            // 验证
            if (isVideo) {
                if (!prompt) { showError('请输入视频描述'); return; }
                if (currentMode === 'video-image' && uploadedImages.length === 0) { showError('请上传参考图片'); return; }
                if (currentMode === 'video-video') {
                    const videoUrl = document.getElementById('videoUrl').value.trim();
                    if (!videoUrl) { showError('请输入视频URL'); return; }
                }
                if (currentMode === 'video-keyframes') {
                    if (!firstFrameData) { showError('请上传首帧图片'); return; }
                    if (!lastFrameData) { showError('请上传尾帧图片'); return; }
                }
            } else {
                if (!prompt) { showError('请输入图片描述'); return; }
                if (currentMode === 'image' && uploadedImages.length === 0) { showError('请上传参考图片'); return; }
            }

            document.getElementById('loading').classList.add('active');
            document.getElementById('result').style.display = 'none';
            document.getElementById('error').style.display = 'none';
            document.getElementById('generateBtn').disabled = true;
            document.getElementById('progressFill').style.width = '0%';
            document.getElementById('statusText').textContent = '进度: 0%';
            document.getElementById('loadingText').textContent = isVideo ? '正在提交视频任务...' : '正在提交任务...';

            try {
                if (isVideo) {
                    await generateVideo(apiKey, model, size, prompt);
                } else {
                    await generateImage(apiKey, model, size, prompt);
                }
            } catch (error) {
                showError(error.message);
            } finally {
                document.getElementById('loading').classList.remove('active');
                document.getElementById('generateBtn').disabled = false;
            }
        }

        async function generateImage(apiKey, model, size, prompt) {
            const quality = document.getElementById('imageQuality').value;
            const body = { apiKey, prompt, size };
            if (currentMode === 'image') {
                body.mode = 'image';
                body.images = uploadedImages.map(img => img.base64);
                body.strength = parseFloat(document.getElementById('strength').value);
                body.model = 'gpt-image-2';
                body.quality = quality;
            } else {
                body.model = model;
                if (model === 'gpt-image-2') body.quality = quality;
            }

            const resp = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            const data = await resp.json();
            if (!resp.ok || data.error) throw new Error(data.error || '提交失败: ' + resp.status);

            currentTaskId = data.taskId;
            document.getElementById('loadingText').textContent = '任务已提交, 正在生成...';
            const result = await pollTaskStatus(currentTaskId, apiKey);

            currentImageUrl = result.images[0].url[0];
            document.getElementById('resultImage').src = currentImageUrl;
            document.getElementById('resultImage').style.display = 'block';
            document.getElementById('resultVideo').style.display = 'none';
            document.getElementById('result').style.display = 'block';
            addToHistory(prompt, currentImageUrl, size, model, currentMode, false);
        }

        async function generateVideo(apiKey, model, size, prompt) {
            const duration = parseInt(document.getElementById('videoDuration').value);
            const resolution = document.getElementById('videoResolution').value;
            const generateAudio = document.getElementById('generateAudio').checked;

            if (duration < 5 || duration > 15) throw new Error('视频时长必须在 5-15 秒之间');

            const body = { apiKey, model, prompt, size, duration, resolution, generate_audio: generateAudio };

            if (currentMode === 'video-text') {
                body.mode = 'text';
            } else if (currentMode === 'video-image') {
                body.mode = 'image';
                body.images = uploadedImages.map(img => img.base64);
            } else if (currentMode === 'video-video') {
                body.mode = 'video';
                body.video_urls = [document.getElementById('videoUrl').value.trim()];
            } else if (currentMode === 'video-keyframes') {
                body.mode = 'keyframes';
                body.first_frame = firstFrameData;
                body.last_frame = lastFrameData;
            }

            const resp = await fetch('/api/video/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            const data = await resp.json();
            if (!resp.ok || data.error) throw new Error(data.error || '提交失败: ' + resp.status);

            currentTaskId = data.taskId;
            document.getElementById('loadingText').textContent = '视频任务已提交, 正在生成(可能需要几分钟)...';
            const result = await pollVideoTaskStatus(currentTaskId, apiKey);

            let videoUrl = '';
            if (result.video && result.video.url) videoUrl = result.video.url;
            else if (result.videos && result.videos[0] && result.videos[0].url) videoUrl = result.videos[0].url;
            else if (result.url) videoUrl = result.url;
            else throw new Error('无法获取视频URL');

            currentVideoUrl = videoUrl;
            document.getElementById('resultVideo').src = '/api/proxy/video?url=' + encodeURIComponent(videoUrl);
            document.getElementById('resultVideo').style.display = 'block';
            document.getElementById('resultImage').style.display = 'none';
            document.getElementById('result').style.display = 'block';
            addToHistory(prompt, videoUrl, size, model, currentMode, true);
        }

        async function pollTaskStatus(taskId, apiKey) {
            for (let i = 0; i < 60; i++) {
                const resp = await fetch('/api/task', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ apiKey, taskId })
                });
                const data = await resp.json();
                if (data.error) throw new Error(data.error);
                const task = data.task;
                const progress = task.progress || 0;
                document.getElementById('progressFill').style.width = progress + '%';
                document.getElementById('statusText').textContent = '进度: ' + progress + '%';
                if (task.status === 'completed') return task.result;
                if (task.status === 'failed') throw new Error(task.error || '生成失败');
                await new Promise(r => setTimeout(r, 2000));
            }
            throw new Error('任务超时');
        }

        async function pollVideoTaskStatus(taskId, apiKey) {
            for (let i = 0; i < 180; i++) {
                const resp = await fetch('/api/video/task', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ apiKey, taskId })
                });
                const data = await resp.json();
                if (data.error) throw new Error(data.error);
                const task = data.task;
                const progress = task.progress || 0;
                document.getElementById('progressFill').style.width = progress + '%';
                document.getElementById('statusText').textContent = '进度: ' + progress + '%';
                if (task.status === 'completed') return task.result;
                if (task.status === 'failed') throw new Error(task.error || '生成失败');
                await new Promise(r => setTimeout(r, 2000));
            }
            throw new Error('视频生成超时');
        }

        function showError(message) {
            const el = document.getElementById('error');
            el.textContent = '⚠️ ' + message;
            el.style.display = 'flex';
        }

        function addToHistory(prompt, url, size, model, mode, isVideo) {
            let history = JSON.parse(localStorage.getItem('image_history') || '[]');
            const modeLabels = { 'text':'文生图', 'image':'图生图', 'video-text':'文生视频', 'video-image':'图生视频', 'video-keyframes':'首尾帧视频', 'video-video':'视频生视频' };
            history.unshift({ prompt, url, size, model, mode: modeLabels[mode] || mode, isVideo, time: new Date().toLocaleString('zh-CN') });
            history = history.slice(0, 20);
            localStorage.setItem('image_history', JSON.stringify(history));
            loadHistory();
        }

        function loadHistory() {
            const history = JSON.parse(localStorage.getItem('image_history') || '[]');
            const container = document.getElementById('history');
            if (history.length === 0) {
                container.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 40px;">暂无历史记录</p>';
                return;
            }
            container.innerHTML = history.map((item, i) =>
                '<div class="history-item" onclick="viewHistory(' + i + ')">' +
                    (item.isVideo ?
                        '<video src="/api/proxy/video?url=' + encodeURIComponent(item.url) + '" muted style="width:100%;height:160px;object-fit:cover;"></video>' :
                        '<img src="' + item.url + '" alt="历史图片" onerror="this.src=\'data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22100%22 height=%22100%22><rect fill=%22%231e293b%22 width=%22100%22 height=%22100%22/><text fill=%22%2364748b%22 x=%2250%22 y=%2250%22 text-anchor=%22middle%22>已过期</text></svg>\'">'
                    ) +
                    '<div class="prompt">' + item.mode + ' | ' + (item.model || '') + '</div>' +
                '</div>'
            ).join('');
        }

        function viewHistory(index) {
            const history = JSON.parse(localStorage.getItem('image_history') || '[]');
            const item = history[index];
            if (!item) return;
            if (item.isVideo) {
                currentVideoUrl = item.url;
                document.getElementById('resultVideo').src = '/api/proxy/video?url=' + encodeURIComponent(item.url);
                document.getElementById('resultVideo').style.display = 'block';
                document.getElementById('resultImage').style.display = 'none';
            } else {
                currentImageUrl = item.url;
                document.getElementById('resultImage').src = item.url;
                document.getElementById('resultImage').style.display = 'block';
                document.getElementById('resultVideo').style.display = 'none';
            }
            document.getElementById('prompt').value = item.prompt || '';
            document.getElementById('size').value = item.size || '';
            switchTab('generate');
            document.getElementById('model').value = item.model || 'gpt-image-2';
            document.getElementById('result').style.display = 'block';
        }

        function downloadResult() {
            const isVideo = document.getElementById('resultVideo').style.display !== 'none';
            const url = isVideo ? currentVideoUrl : currentImageUrl;
            if (!url) return;
            const a = document.createElement('a');
            a.href = url;
            a.download = isVideo ? 'ai-video-' + Date.now() + '.mp4' : 'ai-image-' + Date.now() + '.png';
            a.target = '_blank';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }
    </script>
</body>
</html>
'''

class APIHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)

    # --- 认证系统 ---
    _auth_tokens = {}  # token -> creation_time

    def _verify_auth_cookie(self, cookie_str):
        for part in cookie_str.split(';'):
            part = part.strip()
            if part.startswith('auth_token='):
                token = part.split('=', 1)[1]
                if token in APIHandler._auth_tokens:
                    if time.time() - APIHandler._auth_tokens[token] < 86400:
                        return True
                    else:
                        del APIHandler._auth_tokens[token]
                return False
        return False

    def _handle_auth(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = json.loads(self.rfile.read(content_length))
            password = post_data.get('password', '')
            if password == ACCESS_PASSWORD:
                token = hashlib.sha256(f'{ACCESS_PASSWORD}{time.time()}{os.urandom(16).hex()}'.encode()).hexdigest()
                APIHandler._auth_tokens[token] = time.time()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Set-Cookie', f'auth_token={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age=86400')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode('utf-8'))
            else:
                self._send_json(401, {'success': False, 'error': '密码错误'})
        except Exception as e:
            self._send_json(500, {'success': False, 'error': str(e)})

    # --- 通用 ---
    def _send_json(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _get_api_key(self, post_data):
        api_key = post_data.get('apiKey', '')
        if api_key == '__SERVER_DEFAULT__':
            api_key = os.environ.get('APIMART_API_KEY', '')
        if not api_key:
            api_key = os.environ.get('APIMART_API_KEY', '')
        return api_key

    # --- 路由 ---
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode('utf-8'))
        elif self.path == '/api/config':
            has_default_key = bool(os.environ.get('APIMART_API_KEY', ''))
            self._send_json(200, {'hasDefaultKey': has_default_key})
        elif self.path == '/api/auth/check':
            cookie = self.headers.get('Cookie', '')
            valid = 'auth_token=' in cookie and self._verify_auth_cookie(cookie)
            self._send_json(200, {'valid': valid})
        elif self.path.startswith('/api/proxy/video'):
            self._handle_video_proxy()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/generate':
            self._handle_generate()
        elif self.path == '/api/task':
            self._handle_task_query()
        elif self.path == '/api/video/generate':
            self._handle_video_generate()
        elif self.path == '/api/video/task':
            self._handle_video_task_query()
        elif self.path == '/api/auth':
            self._handle_auth()
        else:
            self.send_response(404)
            self.end_headers()

    # --- 图像生成 ---
    def _handle_generate(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = json.loads(self.rfile.read(content_length))

            api_key = self._get_api_key(post_data)
            model = post_data.get('model', 'gpt-image-2')
            prompt = post_data.get('prompt')
            size = post_data.get('size', '1024x1024')
            mode = post_data.get('mode', 'text')
            quality = post_data.get('quality')
            strength = post_data.get('strength', 0.7)

            if not api_key:
                return self._send_json(400, {'error': 'API Key is required'})

            if mode == 'image':
                # 图生图 - 上传图片到 Cloudinary
                images_base64 = post_data.get('images')
                image_base64 = post_data.get('image')

                image_urls = []
                if images_base64 and isinstance(images_base64, list):
                    try:
                        print(f"[DEBUG] Uploading {len(images_base64)} images to Cloudinary...")
                        for img_b64 in images_base64:
                            clean = img_b64.split(',')[1] if ',' in img_b64 else img_b64
                            img_data = base64.b64decode(clean)
                            result = cloudinary.uploader.upload(io.BytesIO(img_data), folder="apimart_image2image")
                            image_urls.append(result.get('secure_url'))
                    except Exception as e:
                        print(f"[ERROR] Cloudinary upload failed: {e}")
                        traceback.print_exc()
                        return self._send_json(500, {'error': f'图片上传失败: {str(e)}'})
                elif image_base64:
                    try:
                        clean = image_base64.split(',')[1] if ',' in image_base64 else image_base64
                        img_data = base64.b64decode(clean)
                        result = cloudinary.uploader.upload(io.BytesIO(img_data), folder="apimart_image2image")
                        image_urls = [result.get('secure_url')]
                    except Exception as e:
                        print(f"[ERROR] Cloudinary upload failed: {e}")
                        traceback.print_exc()
                        return self._send_json(500, {'error': f'图片上传失败: {str(e)}'})
                else:
                    return self._send_json(400, {'error': '请提供图片'})

                request_data = {
                    'model': 'gpt-image-2',
                    'prompt': prompt,
                    'size': size,
                    'n': 1,
                    'image_urls': image_urls,
                    'strength': float(strength)
                }
                if quality:
                    request_data['quality'] = quality
            else:
                request_data = {'model': model, 'prompt': prompt, 'size': size, 'n': 1}
                if quality and model == 'gpt-image-2':
                    request_data['quality'] = quality

            resp = requests_session.post(
                f"{API_BASE}/images/generations",
                json=request_data,
                headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
                timeout=60
            )
            data = resp.json()
            if resp.status_code != 200 or data.get('code') != 200:
                error_msg = data.get('message', f'API Error: {resp.status_code}')
                return self._send_json(500, {'error': error_msg})

            task_id = data['data'][0]['task_id']
            self._send_json(200, {'taskId': task_id})
        except Exception as e:
            self._send_json(500, {'error': str(e)})

    # --- 图像任务查询 ---
    def _handle_task_query(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = json.loads(self.rfile.read(content_length))
            api_key = self._get_api_key(post_data)
            task_id = post_data.get('taskId')
            if not api_key or not task_id:
                return self._send_json(400, {'error': 'API Key and Task ID required'})
            resp = requests_session.get(
                f"{API_BASE}/tasks/{task_id}",
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=30
            )
            data = resp.json()
            if resp.status_code != 200 or data.get('code') != 200:
                return self._send_json(500, {'error': data.get('message', f'API Error: {resp.status_code}')})
            self._send_json(200, {'task': data['data']})
        except Exception as e:
            self._send_json(500, {'error': str(e)})

    # --- 视频生成 ---
    def _handle_video_generate(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = json.loads(self.rfile.read(content_length))

            # 调试日志(截断大字段)
            debug_data = {k: (f'<{len(str(v))} chars>' if k in ('images', 'first_frame', 'last_frame', 'apiKey') and isinstance(v, (str, list)) and len(str(v)) > 200 else v) for k, v in post_data.items()}
            print(f"[DEBUG] Video request: {json.dumps(debug_data, ensure_ascii=False)}")

            api_key = self._get_api_key(post_data)
            model = post_data.get('model', 'doubao-seedance-2.0')
            prompt = post_data.get('prompt', '') or ''
            mode = post_data.get('mode', 'text')
            size = post_data.get('size', '16:9')
            duration = post_data.get('duration', 5)
            resolution = post_data.get('resolution', '720p')
            generate_audio = post_data.get('generate_audio', False)
            if isinstance(generate_audio, str):
                generate_audio = generate_audio.lower() == 'true'
            try:
                duration = int(duration)
            except (ValueError, TypeError):
                duration = 5

            if not api_key:
                return self._send_json(400, {'error': 'API Key is required'})
            if not prompt:
                return self._send_json(400, {'error': 'Prompt is required'})
            if duration < 5 or duration > 15:
                return self._send_json(400, {'error': f'视频时长须在 5-15 秒之间, 当前: {duration}'})

            request_data = {
                'model': model, 'prompt': prompt, 'resolution': resolution,
                'size': size, 'duration': duration, 'generate_audio': bool(generate_audio)
            }

            # 图生视频
            if mode == 'image':
                images = post_data.get('images', [])
                if images and len(images) > 0:
                    first_img = images[0] if isinstance(images, list) else images
                    if isinstance(first_img, str) and first_img.startswith('http'):
                        request_data['image_url'] = images if isinstance(images, list) else [images]
                    else:
                        try:
                            clean = first_img.split(',')[1] if ',' in first_img else first_img
                            img_data = base64.b64decode(clean)
                            result = cloudinary.uploader.upload(io.BytesIO(img_data), folder="apimart_video")
                            request_data['image_url'] = [result.get('secure_url')]
                        except Exception as e:
                            traceback.print_exc()
                            return self._send_json(500, {'error': f'图片上传失败: {str(e)}'})
                else:
                    return self._send_json(400, {'error': '请提供图片'})

            # 视频生视频
            elif mode == 'video':
                video_urls = post_data.get('video_urls', [])
                if video_urls and len(video_urls) > 0:
                    request_data['video_urls'] = video_urls
                else:
                    return self._send_json(400, {'error': '请提供视频URL'})

            # 首尾帧视频
            elif mode == 'keyframes':
                first_frame = post_data.get('first_frame', '')
                last_frame = post_data.get('last_frame', '')
                if not first_frame or not last_frame:
                    return self._send_json(400, {'error': '请提供首帧和尾帧图片'})
                try:
                    clean_first = first_frame.split(',')[1] if ',' in first_frame else first_frame
                    first_data = base64.b64decode(clean_first)
                    first_result = cloudinary.uploader.upload(io.BytesIO(first_data), folder="apimart_keyframes")
                    first_url = first_result.get('secure_url')

                    clean_last = last_frame.split(',')[1] if ',' in last_frame else last_frame
                    last_data = base64.b64decode(clean_last)
                    last_result = cloudinary.uploader.upload(io.BytesIO(last_data), folder="apimart_keyframes")
                    last_url = last_result.get('secure_url')

                    request_data['image_with_roles'] = [
                        {'url': first_url, 'role': 'first_frame'},
                        {'url': last_url, 'role': 'last_frame'}
                    ]
                except Exception as e:
                    traceback.print_exc()
                    return self._send_json(500, {'error': f'图片上传失败: {str(e)}'})

            print(f"[DEBUG] Final request_data: {json.dumps(request_data, ensure_ascii=False)}")

            resp = requests_session.post(
                f"{API_BASE}/videos/generations",
                json=request_data,
                headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
                timeout=120
            )
            data = resp.json()
            if resp.status_code != 200 or data.get('code') != 200:
                error_msg = data.get('message', f'API Error: {resp.status_code}')
                if resp.status_code == 400:
                    return self._send_json(400, {'error': error_msg})
                return self._send_json(500, {'error': error_msg})

            task_id = data['data'][0]['task_id']
            self._send_json(200, {'taskId': task_id})
        except Exception as e:
            self._send_json(500, {'error': str(e)})

    # --- 视频代理 ---
    def _handle_video_proxy(self):
        try:
            query = urlparse(self.path).query
            params = parse_qs(query)
            video_url = params.get('url', [''])[0]
            if not video_url:
                self.send_response(400)
                self.end_headers()
                return
            resp = requests_session.get(video_url, timeout=60, stream=True)
            content_length = resp.headers.get('Content-Length')
            self.send_response(resp.status_code)
            self.send_header('Content-Type', resp.headers.get('Content-Type', 'video/mp4'))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'public, max-age=3600')
            if content_length:
                self.send_header('Content-Length', content_length)
            self.end_headers()
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    self.wfile.write(chunk)
        except Exception as e:
            print(f"[ERROR] Video proxy error: {e}")
            self.send_response(500)
            self.end_headers()

    # --- 视频任务查询 ---
    def _handle_video_task_query(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = json.loads(self.rfile.read(content_length))
            api_key = self._get_api_key(post_data)
            task_id = post_data.get('taskId')
            if not api_key or not task_id:
                return self._send_json(400, {'error': 'API Key and Task ID required'})
            resp = requests_session.get(
                f"{API_BASE}/tasks/{task_id}",
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=30
            )
            data = resp.json()
            if resp.status_code != 200 or data.get('code') != 200:
                return self._send_json(500, {'error': data.get('message', f'API Error: {resp.status_code}')})
            self._send_json(200, {'task': data['data']})
        except Exception as e:
            self._send_json(500, {'error': str(e)})

    def log_message(self, format, *args):
        print(f"[Server] {format % args}")


def run_server(port=None):
    port = int(os.environ.get('PORT', port or 8080))
    is_cloud = os.environ.get('PORT') or os.environ.get('RENDER') or os.environ.get('RAILWAY_SERVICE_ID')
    host = '0.0.0.0' if is_cloud else '127.0.0.1'

    # 端口冲突检测与自动释放
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.settimeout(1)
        result = test_socket.connect_ex((host, port))
        test_socket.close()
        if result == 0:
            print(f"[WARN] Port {port} is in use, attempting to free it...")
            if host == '127.0.0.1':
                try:
                    r = subprocess.run(
                        f'netstat -ano | findstr :{port} | findstr LISTENING',
                        capture_output=True, text=True, shell=True
                    )
                    for line in r.stdout.strip().split('\n'):
                        parts = line.strip().split()
                        if parts:
                            pid = parts[-1]
                            if pid.isdigit():
                                print(f"[INFO] Killing PID: {pid}")
                                os.system(f'taskkill /F /PID {pid}')
                    time.sleep(1)
                except Exception as e:
                    print(f"[WARN] Failed to free port: {e}")
    except Exception:
        pass

    try:
        server = HTTPServer((host, port), APIHandler)
    except OSError as e:
        print(f"[ERROR] Failed to start server: {e}")
        return

    print("=" * 60)
    print("APIMart Image Generator")
    print("=" * 60)
    print(f"\nServer running at: http://{host}:{port}")
    print("\nPress Ctrl+C to stop")
    print("=" * 60 + "\n")

    if host == '127.0.0.1':
        def open_browser():
            time.sleep(1)
            webbrowser.open(f'http://127.0.0.1:{port}')
        threading.Thread(target=open_browser, daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n[Stop] 服务器已停止")

if __name__ == '__main__':
    run_server()
