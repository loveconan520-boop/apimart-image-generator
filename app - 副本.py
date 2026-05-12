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

# 创建不读取系统代理环境的 session
requests_session = requests.Session()
requests_session.trust_env = False

API_BASE = "https://api.apimart.ai/v1"

# Cloudinary 配置（用于图生视频图片上传）
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
            --bg-card: rgba(255, 255, 255, 0.04);
            --bg-input: rgba(255, 255, 255, 0.06);
            --border: rgba(255, 255, 255, 0.1);
            --text-primary: #ffffff;
            --text-secondary: #cbd5e1;
            --text-muted: #94a3b8;
            --success: #22c55e;
            --warning: #fbbf24;
            --error: #f43f5e;
            --shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
            --glow: 0 0 50px rgba(249, 115, 22, 0.4);
        }
        
        [data-theme="light"] {
            --primary: #f97316;
            --primary-light: #fb923c;
            --primary-dark: #ea580c;
            --secondary: #06b6d4;
            --accent: #8b5cf6;
            --bg-dark: #f8fafc;
            --bg-card: rgba(255, 255, 255, 0.8);
            --bg-input: #ffffff;
            --border: rgba(0, 0, 0, 0.08);
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --text-muted: #94a3b8;
            --success: #22c55e;
            --warning: #f59e0b;
            --error: #ef4444;
            --shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.15);
            --glow: 0 0 30px rgba(249, 115, 22, 0.25);
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: 
                radial-gradient(ellipse at 20% 0%, rgba(249, 115, 22, 0.25) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 0%, rgba(168, 85, 247, 0.2) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 100%, rgba(6, 182, 212, 0.15) 0%, transparent 50%),
                linear-gradient(180deg, #0f0a1a 0%, #0a0a0f 50%, #0a0f1a 100%);
            min-height: 100vh;
            padding: 24px;
            color: var(--text-primary);
            line-height: 1.6;
            transition: background 0.5s ease, color 0.3s ease;
        }
        
        [data-theme="light"] body {
            background: 
                radial-gradient(ellipse at 20% 0%, rgba(249, 115, 22, 0.12) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 0%, rgba(168, 85, 247, 0.1) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 100%, rgba(6, 182, 212, 0.08) 0%, transparent 50%),
                linear-gradient(180deg, #fff7ed 0%, #fff 50%, #f0f9ff 100%);
        }
        
        .container { 
            max-width: 1000px; 
            margin: 0 auto;
            animation: fadeIn 0.6s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Header */
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 20px 0;
        }
        
        .logo {
            display: inline-flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }
        
        .logo-icon {
            width: 56px;
            height: 56px;
            background: linear-gradient(135deg, #f97316 0%, #ec4899 50%, #8b5cf6 100%);
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            box-shadow: 0 0 30px rgba(249, 115, 22, 0.5), 0 0 60px rgba(236, 72, 153, 0.3);
            animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        h1 { 
            font-size: 36px;
            font-weight: 800;
            background: linear-gradient(135deg, #fff 0%, var(--primary-light) 30%, var(--secondary) 70%, var(--accent) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.02em;
            text-shadow: 0 0 60px rgba(249, 115, 22, 0.3);
        }
        
        [data-theme="light"] h1 {
            background: linear-gradient(135deg, #1e293b 0%, #f97316 30%, #06b6d4 70%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: none;
        }
        
        .subtitle { 
            color: var(--text-secondary);
            font-size: 15px;
            font-weight: 400;
        }
        
        /* Card */
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 28px;
            margin-bottom: 24px;
            backdrop-filter: blur(20px);
            box-shadow: var(--shadow);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            border-color: rgba(249, 115, 22, 0.2);
        }
        
        [data-theme="light"] .card {
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 0, 0, 0.06);
        }
        
        [data-theme="light"] .card:hover {
            border-color: rgba(249, 115, 22, 0.3);
            box-shadow: 0 15px 50px -10px rgba(0, 0, 0, 0.2);
        }
        
        /* Tabs */
        .tabs { 
            display: flex; 
            gap: 8px; 
            margin-bottom: 28px;
            background: rgba(0, 0, 0, 0.3);
            padding: 6px;
            border-radius: 14px;
            border: 1px solid var(--border);
        }
        
        [data-theme="light"] .tabs {
            background: rgba(255, 255, 255, 0.6);
            border: 1px solid rgba(0, 0, 0, 0.06);
        }
        
        .tab {
            flex: 1;
            padding: 12px 20px;
            background: transparent;
            border: none;
            border-radius: 10px;
            color: var(--text-secondary);
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            width: auto;
        }
        
        .tab:hover { color: var(--text-primary); }
        
        .tab.active { 
            background: linear-gradient(135deg, rgba(249, 115, 22, 0.25) 0%, rgba(236, 72, 153, 0.15) 100%);
            color: #fff;
            box-shadow: 0 4px 20px rgba(249, 115, 22, 0.3);
            border: 1px solid rgba(249, 115, 22, 0.3);
        }
        
        /* Mode Tabs */
        .mode-tabs {
            display: flex;
            gap: 12px;
            margin-bottom: 28px;
        }
        
        .mode-tab {
            flex: 1;
            padding: 16px;
            background: var(--bg-input);
            border: 1px solid var(--border);
            border-radius: 14px;
            color: var(--text-secondary);
            font-size: 15px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        
        [data-theme="light"] .mode-tab {
            background: #ffffff;
            border: 1px solid rgba(0, 0, 0, 0.08);
        }
        
        .mode-tab:hover {
            border-color: rgba(249, 115, 22, 0.4);
            color: var(--text-primary);
        }
        
        .mode-tab.active {
            background: linear-gradient(135deg, rgba(249, 115, 22, 0.2) 0%, rgba(236, 72, 153, 0.1) 50%, rgba(139, 92, 246, 0.1) 100%);
            border-color: #f97316;
            color: #fb923c;
            box-shadow: 0 0 25px rgba(249, 115, 22, 0.25);
        }
        
        /* Form Elements */
        .form-group { margin-bottom: 24px; }
        
        label { 
            display: block; 
            color: var(--text-secondary); 
            margin-bottom: 10px; 
            font-size: 14px;
            font-weight: 500;
        }
        
        textarea, input, select {
            width: 100%;
            padding: 14px 16px;
            border: 1px solid var(--border);
            border-radius: 12px;
            background: var(--bg-input);
            color: var(--text-primary);
            font-size: 15px;
            font-family: inherit;
            transition: all 0.3s ease;
        }
        
        [data-theme="light"] textarea,
        [data-theme="light"] input,
        [data-theme="light"] select {
            border: 1px solid rgba(0, 0, 0, 0.1);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }
        
        textarea { min-height: 120px; resize: vertical; line-height: 1.6; }
        
        textarea:focus, input:focus, select:focus {
            outline: none;
            border-color: #f97316;
            background: rgba(249, 115, 22, 0.08);
            box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.15), 0 0 20px rgba(249, 115, 22, 0.1);
        }
        
        textarea::placeholder, input::placeholder {
            color: var(--text-muted);
        }
        
        .row { display: flex; gap: 20px; }
        .col { flex: 1; }
        
        /* Buttons */
        button {
            width: 100%;
            padding: 16px 24px;
            border: none;
            border-radius: 12px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: inherit;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #f97316 0%, #ec4899 50%, #8b5cf6 100%);
            color: white;
            box-shadow: 0 4px 25px rgba(249, 115, 22, 0.5), 0 0 40px rgba(236, 72, 153, 0.2);
            position: relative;
            overflow: hidden;
        }
        
        .btn-primary::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.5s;
        }
        
        .btn-primary:hover::before {
            left: 100%;
        }
        
        .btn-primary:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 8px 35px rgba(249, 115, 22, 0.6), 0 0 60px rgba(236, 72, 153, 0.3);
        }
        
        .btn-primary:disabled { 
            background: #334155;
            cursor: not-allowed; 
            transform: none;
            box-shadow: none;
        }
        
        .btn-secondary {
            background: var(--bg-input);
            color: var(--text-primary);
            border: 1px solid var(--border);
            padding: 12px 20px;
            font-size: 14px;
        }
        
        [data-theme="light"] .btn-secondary {
            background: #ffffff;
            border: 1px solid rgba(0, 0, 0, 0.1);
        }
        
        .btn-secondary:hover { 
            background: rgba(255,255,255,0.08);
            border-color: rgba(249, 115, 22, 0.4);
            color: #fb923c;
        }
        
        [data-theme="light"] .btn-secondary:hover {
            background: rgba(249, 115, 22, 0.05);
        }
        
        /* Quick Prompts */
        .quick-prompts { 
            display: flex; 
            flex-wrap: wrap; 
            gap: 10px; 
            margin-top: 14px; 
        }
        
        .quick-prompt {
            padding: 8px 16px;
            background: var(--bg-input);
            border: 1px solid var(--border);
            border-radius: 20px;
            color: var(--text-secondary);
            font-size: 13px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        [data-theme="light"] .quick-prompt {
            background: #ffffff;
            border: 1px solid rgba(0, 0, 0, 0.08);
        }
        
        .quick-prompt:hover { 
            background: linear-gradient(135deg, rgba(249, 115, 22, 0.15) 0%, rgba(236, 72, 153, 0.1) 100%);
            border-color: #f97316;
            color: #fb923c;
            transform: translateY(-2px);
        }
        
        /* Upload Area */
        .upload-area {
            border: 2px dashed var(--border);
            border-radius: 16px;
            padding: 48px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            background: var(--bg-input);
        }
        
        .upload-area:hover {
            border-color: #f97316;
            background: linear-gradient(135deg, rgba(249, 115, 22, 0.08) 0%, rgba(236, 72, 153, 0.05) 100%);
        }
        
        .upload-area.has-file {
            border-style: solid;
            border-color: var(--success);
            background: rgba(16, 185, 129, 0.05);
        }
        
        [data-theme="light"] .upload-area.has-file {
            background: rgba(34, 197, 94, 0.08);
        }
        
        /* Multi-image preview grid */
        .image-preview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
            gap: 12px;
            margin-top: 16px;
        }
        
        .preview-item {
            position: relative;
            aspect-ratio: 1;
            border-radius: 12px;
            overflow: hidden;
            border: 2px solid var(--border);
            transition: all 0.3s ease;
        }
        
        .preview-item:hover {
            border-color: var(--primary);
            transform: scale(1.05);
        }
        
        .preview-item img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .preview-item .remove-btn {
            position: absolute;
            top: 4px;
            right: 4px;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: rgba(239, 68, 68, 0.9);
            border: none;
            color: white;
            font-size: 14px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.2s ease;
            padding: 0;
        }
        
        .preview-item:hover .remove-btn {
            opacity: 1;
        }
        
        .preview-item .remove-btn:hover {
            background: rgba(239, 68, 68, 1);
            transform: scale(1.1);
        }
        
        .preview-item .image-index {
            position: absolute;
            bottom: 4px;
            left: 4px;
            background: rgba(0, 0, 0, 0.6);
            color: white;
            font-size: 11px;
            padding: 2px 6px;
            border-radius: 4px;
        }
        
        .upload-actions {
            display: flex;
            gap: 10px;
        }
        
        .upload-area input[type="file"] { display: none; }
        
        .upload-icon {
            width: 72px;
            height: 72px;
            background: linear-gradient(135deg, #f97316 0%, #ec4899 50%, #06b6d4 100%);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            margin: 0 auto 16px;
            box-shadow: 0 0 30px rgba(249, 115, 22, 0.4), 0 0 50px rgba(6, 182, 212, 0.2);
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-8px); }
        }
        
        .upload-text { color: var(--text-secondary); }
        .upload-text h4 { color: var(--text-primary); margin-bottom: 6px; font-weight: 500; }
        .upload-text p { font-size: 13px; }
        
        .upload-preview {
            max-width: 280px;
            max-height: 280px;
            border-radius: 12px;
            box-shadow: var(--shadow);
        }
        
        /* Strength Slider */
        .strength-slider {
            width: 100%;
            margin-top: 12px;
            -webkit-appearance: none;
            height: 6px;
            border-radius: 3px;
            background: var(--bg-input);
            outline: none;
        }
        
        .strength-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 22px;
            height: 22px;
            border-radius: 50%;
            background: linear-gradient(135deg, #f97316 0%, #ec4899 50%, #8b5cf6 100%);
            cursor: pointer;
            box-shadow: 0 2px 15px rgba(249, 115, 22, 0.5);
            border: 2px solid #fff;
        }
        
        .strength-labels {
            display: flex;
            justify-content: space-between;
            color: var(--text-muted);
            font-size: 12px;
            margin-top: 8px;
        }
        
        /* Result */
        .result { 
            text-align: center;
            animation: fadeIn 0.5s ease-out;
        }
        
        .result img { 
            max-width: 100%; 
            border-radius: 16px; 
            margin-bottom: 20px;
            box-shadow: var(--shadow);
        }
        
        /* Loading */
        .loading {
            display: none;
            text-align: center;
            padding: 48px;
        }
        
        .loading.active { display: block; }
        
        .spinner {
            width: 60px;
            height: 60px;
            border: 4px solid rgba(249, 115, 22, 0.15);
            border-top-color: #f97316;
            border-right-color: #ec4899;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
            box-shadow: 0 0 20px rgba(249, 115, 22, 0.3);
        }
        
        @keyframes spin { to { transform: rotate(360deg); } }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: var(--bg-input);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 20px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #f97316 0%, #ec4899 50%, #06b6d4 100%);
            border-radius: 4px;
            transition: width 0.5s ease;
            box-shadow: 0 0 15px rgba(249, 115, 22, 0.6);
        }
        
        .status-text { 
            color: var(--text-secondary); 
            margin-top: 12px;
            font-size: 14px;
        }
        
        /* Error */
        .error {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #fca5a5;
            padding: 16px 20px;
            border-radius: 12px;
            margin-top: 20px;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        [data-theme="light"] .error {
            background: rgba(239, 68, 68, 0.08);
            border: 1px solid rgba(239, 68, 68, 0.2);
            color: #dc2626;
        }
        
        /* Info Box */
        .model-info {
            background: linear-gradient(135deg, rgba(249, 115, 22, 0.1) 0%, rgba(236, 72, 153, 0.08) 50%, rgba(6, 182, 212, 0.05) 100%);
            border: 1px solid rgba(249, 115, 22, 0.2);
            padding: 20px;
            border-radius: 14px;
            margin-top: 24px;
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.8;
        }
        
        .model-info strong {
            background: linear-gradient(135deg, #f97316 0%, #ec4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
        }
        
        /* History */
        .history { 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); 
            gap: 20px; 
            margin-top: 24px; 
        }
        
        .history-item {
            background: var(--bg-input);
            border: 1px solid var(--border);
            border-radius: 14px;
            overflow: hidden;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        [data-theme="light"] .history-item {
            background: #ffffff;
            border: 1px solid rgba(0, 0, 0, 0.08);
        }
        
        .history-item:hover { 
            transform: translateY(-4px);
            border-color: #f97316;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3), 0 0 20px rgba(249, 115, 22, 0.15);
        }
        
        [data-theme="light"] .history-item:hover {
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1), 0 0 20px rgba(249, 115, 22, 0.1);
        }
        
        .history-item img { 
            width: 100%; 
            height: 160px; 
            object-fit: cover;
            transition: transform 0.3s ease;
        }
        
        .history-item:hover img {
            transform: scale(1.05);
        }
        
        .history-item .prompt { 
            padding: 12px 16px; 
            font-size: 13px; 
            color: var(--text-secondary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        /* Panel */
        .panel { display: none; }
        .panel.active { display: block; animation: fadeIn 0.4s ease-out; }
        
        /* Model Hint */
        #modelHint {
            display: block;
            margin-top: 8px;
            color: #fb923c;
            font-size: 12px;
            font-weight: 500;
        }
        
        /* Theme Toggle */
        .theme-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: linear-gradient(135deg, #fbbf24 0%, #f97316 100%);
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            box-shadow: 0 4px 20px rgba(251, 191, 36, 0.4);
            transition: all 0.3s ease;
            z-index: 1000;
        }
        
        .theme-toggle:hover {
            transform: scale(1.1) rotate(15deg);
            box-shadow: 0 6px 30px rgba(251, 191, 36, 0.6);
        }
        
        [data-theme="light"] .theme-toggle {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
        }
        
        [data-theme="light"] .theme-toggle:hover {
            box-shadow: 0 6px 30px rgba(99, 102, 241, 0.6);
        }
        
        /* Responsive */
        @media (max-width: 640px) {
            .row { flex-direction: column; gap: 16px; }
            h1 { font-size: 24px; }
            .card { padding: 20px; }
            .mode-tabs { flex-direction: column; }
        }
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
            <p id="passwordError" style="color: #f43f5e; margin-top: 16px; font-size: 14px; display: none;">密码错误，请重试</p>
        </div>
    </div>

    <button class="theme-toggle" id="themeToggle" onclick="toggleTheme()" title="切换主题">☀️</button>
    <div class="container" id="mainContainer" style="display: none;">
        <div class="header">
            <div class="logo">
                <div class="logo-icon">✨</div>
                <h1>AI 图像生成器</h1>
            </div>
            <p class="subtitle">基于 APIMart 的强大 AI 图像生成服务</p>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="switchTab('generate')">🎨 生成图片</button>
            <button class="tab" onclick="switchTab('history')">📷 历史记录</button>
            <button class="tab" onclick="switchTab('config')">⚙️ API设置</button>
        </div>
        
        <div id="generate-panel" class="panel active">
            <div class="card">
                <div class="mode-tabs">
                    <button class="mode-tab active" onclick="switchMode('text')" id="tab-text">文生图</button>
                    <button class="mode-tab" onclick="switchMode('image')" id="tab-image">图生图</button>
                    <button class="mode-tab" onclick="switchMode('video-text')" id="tab-video-text">文生视频</button>
                    <button class="mode-tab" onclick="switchMode('video-image')" id="tab-video-image">图生视频</button>
                    <button class="mode-tab" onclick="switchMode('video-keyframes')" id="tab-video-keyframes">首尾帧视频</button>
                    <button class="mode-tab" onclick="switchMode('video-video')" id="tab-video-video">视频生视频</button>
                </div>
                
                <div id="text-mode-panel">
                    <div class="form-group">
                        <label>描述你想要的内容</label>
                        <textarea id="prompt" placeholder="例如：反骨西游海报，孙悟空金甲红袍，手持金箍棒，动漫风格..."></textarea>
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
                                <div class="upload-icon">[上传]</div>
                                <h4>点击上传图片</h4>
                                <p>或拖拽到此处，支持多图上传 (最多5张)</p>
                            </div>
                        </div>
                        <input type="file" id="imageInput" accept="image/*" multiple onchange="handleImageUpload(event)">
                        
                        <!-- 多图预览区域 -->
                        <div class="image-preview-grid" id="imagePreviewGrid" style="display: none;">
                            <!-- 动态生成的预览图将放在这里 -->
                        </div>
                        
                        <div class="upload-actions" id="uploadActions" style="display: none; margin-top: 12px;">
                            <button type="button" class="btn-secondary" onclick="clearAllImages()" style="width: auto; padding: 8px 16px; font-size: 13px;">
                                清空所有
                            </button>
                            <button type="button" class="btn-secondary" onclick="document.getElementById('imageInput').click()" style="width: auto; padding: 8px 16px; font-size: 13px;">
                                继续添加
                            </button>
                        </div>
                    </div>
                    
                    <div class="form-group" id="imagePromptGroup">
                        <label>图片修改描述</label>
                        <textarea id="imagePrompt" placeholder="描述你想如何修改这些图片，例如：将所有角色融合成一张海报、转换为动漫风格、增加金色光芒效果..."></textarea>
                    </div>
                    
                    <div class="form-group" id="imageUrlGroup" style="display: none;">
                        <label>参考图片URL</label>
                        <input type="text" id="imageUrl" placeholder="输入真实可访问的图片URL，例如：https://images.unsplash.com/photo-1574158622682-e40e69881006?w=800" style="width: 100%; padding: 14px 16px; border: 1px solid var(--border); border-radius: 12px; background: var(--bg-input); color: var(--text-primary); font-size: 15px; box-sizing: border-box;">
                        <small style="color: var(--text-muted); font-size: 12px; margin-top: 6px; display: block;">图生视频需要真实可公网访问的图片URL，示例URL无法使用</small>
                    </div>
                    
                    <div class="form-group" id="strengthGroup">
                        <label>参考强度</label>
                        <input type="range" id="strength" class="strength-slider" min="0.1" max="1.0" step="0.1" value="0.7" oninput="updateStrengthLabel(this.value)">
                        <div class="strength-labels">
                            <span>保留原图</span>
                            <span id="strengthValue">0.7</span>
                            <span>完全重绘</span>
                        </div>
                    </div>
                </div>
                
                <div id="video-upload-panel" style="display: none;">
                    <div class="form-group">
                        <label>参考视频URL</label>
                        <input type="text" id="videoUrl" placeholder="输入可公网访问的视频URL，例如：https://example.com/video.mp4" style="width: 100%; padding: 14px 16px; border: 1px solid var(--border); border-radius: 12px; background: var(--bg-input); color: var(--text-primary); font-size: 15px; box-sizing: border-box;">
                        <small style="color: var(--text-muted); font-size: 12px; margin-top: 6px; display: block;">视频生视频需要可公网访问的视频URL，不支持本地文件上传</small>
                    </div>
                    
                    <div class="form-group">
                        <label>视频风格描述（可选）</label>
                        <textarea id="videoPrompt" placeholder="描述你想要的视频风格或效果，例如：转换为赛博朋克风格、添加梦幻光效、变成水墨画风格..."></textarea>
                    </div>
                </div>
                
                <!-- 首尾帧视频面板 -->
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
                
                <!-- 视频参数 - 仅视频模式显示 -->
                <div class="row" id="video-params" style="display: none;">
                    <div class="col">
                        <div class="form-group">
                            <label>视频质量</label>
                            <select id="videoResolution">
                                <option value="480p">480P (标清)</option>
                                <option value="720p" selected>720P (高清)</option>
                                <option value="1080p">1080P (全高清)</option>
                            </select>
                        </div>
                    </div>
                    <div class="col">
                        <div class="form-group">
                            <label>视频时长 (5-15秒)</label>
                            <input type="number" id="videoDuration" min="5" max="15" value="5" placeholder="5">
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
                            <label>模型</label>
                            <select id="model" onchange="handleModelChange()">
                                <option value="image2.0" selected>image2.0 (推荐)</option>
                                <option value="flux-2-pro">flux-2-pro</option>
                                <option value="gpt-image-2">gpt-image-2</option>
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
                                <option value="1024x1024">正方形 1024×1024</option>
                                <option value="1024x1536">竖版 1024×1536</option>
                                <option value="1536x1024" selected>横版 1536×1024</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <button class="btn-primary" id="generateBtn" onclick="generateImage()">
                    生成图片
                </button>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p id="loadingText">正在提交任务...</p>
                    <div class="progress-bar"><div class="progress-fill" id="progressFill" style="width: 0%"></div></div>
                    <p class="status-text" id="statusText">进度: 0%</p>
                </div>
            </div>
            
            <div class="card result" id="result" style="display: none;">
                <img id="resultImage" src="" alt="生成结果">
                <video id="resultVideo" src="" controls crossorigin="anonymous" playsinline style="display: none; width: 100%; border-radius: 12px; margin-bottom: 16px;"></video>
                <button class="btn-primary" onclick="downloadResult()">下载</button>
            </div>
            
            <div class="error" id="error" style="display: none;"></div>
            
            <div class="model-info">
                <strong>使用提示</strong><br>
                • <b>文生图</b>：输入文字描述，AI 从零生成图片<br>
                • <b>图生图</b>：上传参考图 + 描述，AI 基于原图进行修改<br>
                • <b>文生视频</b>：输入描述生成视频，默认5秒，支持4-15秒<br>
                • <b>图生视频</b>：上传图片生成动态视频<br>
                • <b>视频生视频</b>：输入可公网访问的视频URL进行风格转换<br>
                • <b>image2.0</b>：文生图默认推荐模型<br>
                • <b>seedance2.0-fast</b>：视频生成默认模型，速度快<br>
                • <b>有声视频</b>：勾选后可生成带音频的视频<br>
                • 图片/视频链接有效期 24 小时，请及时下载保存
            </div>
        </div>
        
        <div id="history-panel" class="panel">
            <div class="card">
                <h3 style="color: var(--primary-light); margin-bottom: 20px; font-weight: 600;">历史记录</h3>
                <div class="history" id="history"></div>
            </div>
        </div>
        
        <div id="config-panel" class="panel">
            <div class="card">
                <h3 style="color: var(--primary-light); margin-bottom: 24px; font-weight: 600;">API 设置</h3>
                <div class="form-group">
                    <label>APIMart API Key</label>
                    <input type="password" id="apiKey" placeholder="sk-...">
                    <small style="color: var(--text-muted); display: block; margin-top: 8px;">
                        从 <a href="https://apimart.ai" target="_blank" style="color: var(--primary-light);">apimart.ai</a> 获取你的 API Key
                    </small>
                </div>
                <button class="btn-primary" onclick="saveConfig()">保存配置</button>
            </div>
        </div>
    </div>
    
    <script>
        let currentImageUrl = '';
        let currentVideoUrl = '';
        let currentTaskId = '';
        let currentMode = 'text';
        let uploadedImages = []; // 存储多图 {name, base64, preview}
        let uploadedVideo = null; // 存储上传的视频 base64
        const MAX_IMAGES = 5;
        const ACCESS_PASSWORD = "athena80127678!";
        
        // Password protection
        function checkPassword() {
            const input = document.getElementById('passwordInput').value;
            const error = document.getElementById('passwordError');
            
            if (input === ACCESS_PASSWORD) {
                document.getElementById('passwordOverlay').style.display = 'none';
                document.getElementById('mainContainer').style.display = 'block';
                localStorage.setItem('authenticated', 'true');
            } else {
                error.style.display = 'block';
                document.getElementById('passwordInput').value = '';
            }
        }
        
        // Check if already authenticated
        function initAuth() {
            if (localStorage.getItem('authenticated') === 'true') {
                document.getElementById('passwordOverlay').style.display = 'none';
                document.getElementById('mainContainer').style.display = 'block';
            }
        }
        
        // Allow Enter key to submit password
        document.addEventListener('DOMContentLoaded', () => {
            const passwordInput = document.getElementById('passwordInput');
            if (passwordInput) {
                passwordInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') checkPassword();
                });
            }
            initAuth();
        });
        
        // Theme management
        function initTheme() {
            const savedTheme = localStorage.getItem('theme') || 'dark';
            document.documentElement.setAttribute('data-theme', savedTheme);
            updateThemeIcon(savedTheme);
        }
        
        function toggleTheme() {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        }
        
        function updateThemeIcon(theme) {
            const btn = document.getElementById('themeToggle');
            btn.textContent = theme === 'dark' ? '☀️' : '🌙';
            btn.title = theme === 'dark' ? '切换到白天模式' : '切换到夜间模式';
        }
        
        document.addEventListener('DOMContentLoaded', () => {
            initTheme();
            loadConfig();
            loadHistory();
            
            const uploadArea = document.getElementById('uploadArea');
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.style.borderColor = 'var(--primary)';
            });
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.style.borderColor = 'var(--border)';
            });
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.style.borderColor = 'var(--border)';
                const files = e.dataTransfer.files;
                if (files.length > 0) handleFiles(files);
            });
        });
        
        function loadConfig() {
            const apiKey = localStorage.getItem('apimart_api_key');
            if (apiKey) document.getElementById('apiKey').value = apiKey;
            // 检查服务器是否有默认 API Key
            fetch('/api/config')
                .then(r => r.json())
                .then(data => {
                    if (data.hasDefaultKey && !apiKey) {
                        document.getElementById('apiKey').value = '(使用服务器默认 Key)';
                        document.getElementById('apiKey').type = 'text';
                        document.getElementById('apiKey').disabled = true;
                    }
                })
                .catch(() => {});
        }
        
        function saveConfig() {
            const apiKey = document.getElementById('apiKey').value.trim();
            if (!apiKey) { alert('请输入 API Key'); return; }
            localStorage.setItem('apimart_api_key', apiKey);
            alert('API Key 已保存！');
        }
        
        function setPrompt(text) {
            const prompts = {
                '孙悟空': '孙悟空角色设定图，金甲红袍，头戴紫金冠，手持如意金箍棒，动漫风格，精细画质',
                '杨戬': '杨戬角色设定图，银甲战袍，第三只眼，天眼开阔，手持三尖两刃刀，动漫风格',
                '哪吒': '哪吒角色设定图，混天绫环绕，乾坤圈在手，脚踩风火轮，动漫少年形象',
                '反骨西游海报': '反骨西游团队海报，悟空、杨戬、哪吒并肩站立，反抗天庭，炫酷动漫风格',
                '天庭场景': '天庭场景，云雾缭绕，金碧辉煌的建筑，宏伟壮观，东方奇幻风格'
            };
            const targetId = currentMode === 'text' ? 'prompt' : 'imagePrompt';
            document.getElementById(targetId).value = prompts[text] || text;
        }
        
        // 首尾帧图片管理
        let firstFrameData = null;
        let lastFrameData = null;
        
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
        
        function clearFirstFrame() {
            firstFrameData = null;
            document.getElementById('firstFramePreview').style.display = 'none';
            document.getElementById('firstFrameUploadArea').style.display = 'block';
            document.getElementById('firstFrameInput').value = '';
        }
        
        function clearLastFrame() {
            lastFrameData = null;
            document.getElementById('lastFramePreview').style.display = 'none';
            document.getElementById('lastFrameUploadArea').style.display = 'block';
            document.getElementById('lastFrameInput').value = '';
        }
        
        function switchTab(tab) {
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            document.getElementById(`${tab}-panel`).classList.add('active');
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            const tabIndex = { 'generate': 0, 'history': 1, 'config': 2 };
            document.querySelectorAll('.tab')[tabIndex[tab]].classList.add('active');
        }
        
        function switchMode(mode) {
            currentMode = mode;
            document.querySelectorAll('.mode-tab').forEach(t => t.classList.remove('active'));
            document.getElementById(`tab-${mode}`).classList.add('active');
            
            const modelSelect = document.getElementById('model');
            const modelHint = document.getElementById('modelHint');
            const sizeSelect = document.getElementById('size');
            const sizeLabel = document.getElementById('sizeLabel');
            const videoParams = document.getElementById('video-params');
            const generateBtn = document.getElementById('generateBtn');
            
            // 重置面板显示
            document.getElementById('text-mode-panel').style.display = 'none';
            document.getElementById('image-mode-panel').style.display = 'none';
            document.getElementById('video-upload-panel').style.display = 'none';
            
            if (mode === 'text') {
                document.getElementById('text-mode-panel').style.display = 'block';
                modelSelect.disabled = false;
                modelHint.style.display = 'none';
                sizeLabel.textContent = '图片尺寸';
                sizeSelect.style.display = 'block';
                videoParams.style.display = 'none';
                generateBtn.textContent = '生成图片';
                setupImageSizes();
                // 设置文生图默认模型
                modelSelect.value = 'image2.0';
            } else if (mode === 'image') {
                document.getElementById('image-mode-panel').style.display = 'block';
                // 图生图时显示所有元素
                const imagePromptGroup = document.getElementById('imagePromptGroup');
                if (imagePromptGroup) imagePromptGroup.style.display = 'block';
                const uploadArea = document.getElementById('uploadArea');
                if (uploadArea) uploadArea.style.display = 'block';
                const imagePreviewGrid = document.getElementById('imagePreviewGrid');
                if (imagePreviewGrid && uploadedImages.length > 0) imagePreviewGrid.style.display = 'grid';
                const uploadActions = document.getElementById('uploadActions');
                if (uploadActions && uploadedImages.length > 0) uploadActions.style.display = 'block';
                const strengthGroup = document.getElementById('strengthGroup');
                if (strengthGroup) strengthGroup.style.display = 'block';
                const imageUrlGroup = document.getElementById('imageUrlGroup');
                if (imageUrlGroup) imageUrlGroup.style.display = 'none';
                modelSelect.disabled = true;
                modelHint.style.display = 'block';
                sizeLabel.textContent = '图片尺寸';
                sizeSelect.style.display = 'block';
                videoParams.style.display = 'none';
                generateBtn.textContent = '生成图片';
                setupImageSizes();
            } else if (mode.startsWith('video')) {
                // 视频模式
                document.getElementById('text-mode-panel').style.display = 'block';
                if (mode === 'video-image') {
                    document.getElementById('image-mode-panel').style.display = 'block';
                    // 图生视频时隐藏"图片修改描述"、参考强度，显示上传区域
                    const imagePromptGroup = document.getElementById('imagePromptGroup');
                    if (imagePromptGroup) imagePromptGroup.style.display = 'none';
                    const uploadArea = document.getElementById('uploadArea');
                    if (uploadArea) uploadArea.style.display = 'block';
                    const imagePreviewGrid = document.getElementById('imagePreviewGrid');
                    if (imagePreviewGrid && uploadedImages.length > 0) imagePreviewGrid.style.display = 'grid';
                    const uploadActions = document.getElementById('uploadActions');
                    if (uploadActions && uploadedImages.length > 0) uploadActions.style.display = 'block';
                    const strengthGroup = document.getElementById('strengthGroup');
                    if (strengthGroup) strengthGroup.style.display = 'none';
                    const imageUrlGroup = document.getElementById('imageUrlGroup');
                    if (imageUrlGroup) imageUrlGroup.style.display = 'none';
                    document.getElementById('keyframes-panel').style.display = 'none';
                } else if (mode === 'video-keyframes') {
                    document.getElementById('keyframes-panel').style.display = 'block';
                    document.getElementById('image-mode-panel').style.display = 'none';
                    document.getElementById('video-upload-panel').style.display = 'none';
                } else if (mode === 'video-video') {
                    document.getElementById('video-upload-panel').style.display = 'block';
                    document.getElementById('keyframes-panel').style.display = 'none';
                }
                modelSelect.disabled = false;
                modelHint.style.display = 'none';
                sizeLabel.textContent = '视频比例';
                sizeSelect.style.display = 'block';
                videoParams.style.display = 'flex';
                generateBtn.textContent = '生成视频';
                setupVideoSizes();
                // 设置视频默认模型
                modelSelect.value = 'doubao-seedance-2.0';
            }
        }
        
        function setupImageSizes() {
            const sizeSelect = document.getElementById('size');
            const model = document.getElementById('model').value;
            
            // 根据模型使用不同的尺寸格式
            if (model === 'gpt-image-2') {
                // GPT-Image-2 使用比例格式
                sizeSelect.innerHTML = `
                    <option value="1:1" selected>正方形 1:1</option>
                    <option value="9:16">竖版 9:16</option>
                    <option value="16:9">横版 16:9</option>
                    <option value="4:3">横版 4:3</option>
                    <option value="3:4">竖版 3:4</option>
                `;
            } else {
                // Flux 和其他模型使用像素尺寸
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
                <option value="9:16" selected>竖屏 (9:16)</option>
                <option value="16:9">横屏 (16:9)</option>
                <option value="1:1">方形 (1:1)</option>
                <option value="4:3">传统比例 (4:3)</option>
                <option value="3:4">竖向传统 (3:4)</option>
                <option value="21:9">超宽屏 (21:9)</option>
            `;
        }
        
        function updateStrengthLabel(val) {
            document.getElementById('strengthValue').textContent = val;
        }
        
        function handleImageUpload(event) {
            const files = event.target.files;
            if (files.length > 0) handleFiles(files);
        }
        
        function handleVideoUpload(event) {
            const file = event.target.files[0];
            if (!file) return;
            
            if (!file.type.startsWith('video/')) {
                alert('请上传视频文件');
                return;
            }
            
            if (file.size > 50 * 1024 * 1024) {
                alert('视频文件不能超过 50MB');
                return;
            }
            
            const reader = new FileReader();
            reader.onload = (e) => {
                uploadedVideo = e.target.result.split(',')[1];
                document.getElementById('previewVideo').src = e.target.result;
                document.getElementById('videoPreview').style.display = 'block';
                document.getElementById('videoUploadArea').style.display = 'none';
            };
            reader.readAsDataURL(file);
        }
        
        function clearVideo() {
            uploadedVideo = null;
            document.getElementById('previewVideo').src = '';
            document.getElementById('videoPreview').style.display = 'none';
            document.getElementById('videoUploadArea').style.display = 'block';
            document.getElementById('videoInput').value = '';
        }
        
        function handleFiles(files) {
            const remainingSlots = MAX_IMAGES - uploadedImages.length;
            if (remainingSlots <= 0) {
                alert(`最多只能上传 ${MAX_IMAGES} 张图片`);
                return;
            }
            
            const filesToProcess = Math.min(files.length, remainingSlots);
            let processed = 0;
            
            for (let i = 0; i < filesToProcess; i++) {
                const file = files[i];
                if (!file.type.startsWith('image/')) {
                    alert(`${file.name} 不是图片文件，已跳过`);
                    continue;
                }
                
                const reader = new FileReader();
                reader.onload = (e) => {
                    uploadedImages.push({
                        name: file.name,
                        base64: e.target.result.split(',')[1],
                        preview: e.target.result
                    });
                    processed++;
                    if (processed === filesToProcess || processed === files.length) {
                        updateImagePreview();
                    }
                };
                reader.readAsDataURL(file);
            }
            
            if (files.length > remainingSlots) {
                alert(`已添加 ${filesToProcess} 张图片，超出 ${MAX_IMAGES} 张限制的部分已忽略`);
            }
        }
        
        function updateImagePreview() {
            const grid = document.getElementById('imagePreviewGrid');
            const uploadArea = document.getElementById('uploadArea');
            const uploadActions = document.getElementById('uploadActions');
            const imageCount = document.getElementById('imageCount');
            
            // 更新计数
            imageCount.textContent = `(${uploadedImages.length}/${MAX_IMAGES})`;
            
            if (uploadedImages.length === 0) {
                grid.style.display = 'none';
                uploadActions.style.display = 'none';
                uploadArea.style.display = 'block';
                uploadArea.classList.remove('has-file');;
                return;
            }
            
            // 隐藏上传区域，显示预览和操作按钮
            uploadArea.style.display = 'none';
            grid.style.display = 'grid';
            uploadActions.style.display = 'flex';
            
            // 清空并重建预览
            grid.innerHTML = '';
            uploadedImages.forEach((img, index) => {
                const item = document.createElement('div');
                item.className = 'preview-item';
                item.innerHTML = `
                    <img src="${img.preview}" alt="${img.name}">
                    <span class="image-index">#${index + 1}</span>
                    <button class="remove-btn" onclick="removeImage(${index})" title="删除">×</button>
                `;
                grid.appendChild(item);
            });
        }
        
        function removeImage(index) {
            uploadedImages.splice(index, 1);
            updateImagePreview();
        }
        
        function clearAllImages() {
            if (uploadedImages.length === 0) return;
            if (confirm(`确定要清空所有 ${uploadedImages.length} 张图片吗？`)) {
                uploadedImages = [];
                updateImagePreview();
            }
        }
        
        async function generateImage() {
            let apiKey = localStorage.getItem('apimart_api_key') || '';
            const apiKeyInput = document.getElementById('apiKey');
            // 如果输入框没被禁用（用户自己输入的Key），优先使用输入框的值
            if (!apiKeyInput.disabled && apiKeyInput.value.trim()) {
                apiKey = apiKeyInput.value.trim();
            }
            // 如果输入框被禁用（使用服务器默认Key），发送特殊标记
            if (apiKeyInput.disabled) {
                apiKey = '__SERVER_DEFAULT__';
            }
            // 如果没有用户Key且没有服务器默认Key，提示配置
            if (!apiKey) {
                showError('请先在"API设置"中配置你的 APIMart API Key');
                switchTab('config');
                return;
            }
            
            const model = document.getElementById('model').value;
            const size = document.getElementById('size').value;
            
            // 判断是否为视频模式
            const isVideoMode = currentMode.startsWith('video');
            
            let prompt, imageData, strength;
            
            if (currentMode === 'text' || isVideoMode) {
                prompt = document.getElementById('prompt').value.trim();
                if (!prompt) { showError(isVideoMode ? '请输入视频描述' : '请输入图片描述'); return; }
            }
            
            if (currentMode === 'image' || currentMode === 'video-image') {
                const imagePrompt = document.getElementById('imagePrompt').value.trim();
                // 图生视频时，优先使用 imagePrompt（图片修改描述）
                // 如果 imagePrompt 为空，使用 prompt（描述你想要的内容）
                prompt = imagePrompt || prompt;
                
                if (currentMode === 'video-image') {
                    // 图生视频使用上传的图片（base64）
                    if (uploadedImages.length === 0) { 
                        showError('请上传参考图片'); 
                        return; 
                    }
                    imageData = uploadedImages.map(img => img.base64);
                } else {
                    // 图生图使用上传的图片
                    if (uploadedImages.length === 0) { 
                        showError('请至少上传一张参考图片'); 
                        return; 
                    }
                    imageData = uploadedImages.map(img => img.base64);
                    strength = document.getElementById('strength').value;
                }
            } else if (currentMode === 'video-keyframes') {
                // 首尾帧视频
                if (!firstFrameData) {
                    showError('请上传首帧图片');
                    return;
                }
                if (!lastFrameData) {
                    showError('请上传尾帧图片');
                    return;
                }
            }
            
            document.getElementById('loading').classList.add('active');
            document.getElementById('result').style.display = 'none';
            document.getElementById('error').style.display = 'none';
            document.getElementById('generateBtn').disabled = true;
            document.getElementById('progressFill').style.width = '0%';
            document.getElementById('statusText').textContent = '进度: 0%';
            document.getElementById('loadingText').textContent = isVideoMode ? '正在提交视频任务...' : '正在提交任务...';
            
            try {
                // 视频模式使用视频 API
                if (isVideoMode) {
                    if (currentMode === 'video-keyframes') {
                        await generateKeyframesVideo(apiKey, model, size, prompt);
                    } else {
                        await generateVideo(apiKey, model, size, prompt, imageData);
                    }
                } else {
                    await generateImageInternal(apiKey, model, size, prompt, imageData, strength);
                }
            } catch (error) {
                showError(error.message);
            } finally {
                document.getElementById('loading').classList.remove('active');
                document.getElementById('generateBtn').disabled = false;
            }
        }
        
        async function generateImageInternal(apiKey, model, size, prompt, imageData, strength) {
            const body = { apiKey, prompt, size };
            if (currentMode === 'image') {
                body.mode = 'image';
                if (Array.isArray(imageData) && imageData.length > 1) {
                    body.images = imageData;
                } else {
                    body.image = Array.isArray(imageData) ? imageData[0] : imageData;
                }
                body.strength = parseFloat(strength);
                body.model = 'gpt-image-2';
            } else {
                body.model = model;
            }
            
            const submitResp = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            
            const submitData = await submitResp.json();
            
            if (!submitResp.ok || submitData.error) {
                throw new Error(submitData.error || `提交失败: ${submitResp.status}`);
            }
            
            currentTaskId = submitData.taskId;
            document.getElementById('loadingText').textContent = '任务已提交，正在生成...';
            
            const result = await pollTaskStatus(currentTaskId, apiKey);
            
            currentImageUrl = result.images[0].url[0];
            document.getElementById('resultImage').src = currentImageUrl;
            document.getElementById('result').style.display = 'block';
            addToHistory(prompt, currentImageUrl, size, model, currentMode);
        }
        
        async function generateVideo(apiKey, model, size, prompt, imageData) {
            // 获取视频参数
            const videoDuration = parseInt(document.getElementById('videoDuration').value);
            const videoResolution = document.getElementById('videoResolution').value;
            const generateAudio = document.getElementById('generateAudio').checked;
            
            // 验证时长范围 (5-15秒)
            if (videoDuration < 5 || videoDuration > 15) {
                throw new Error('视频时长必须在 5-15 秒之间');
            }
            
            const body = {
                apiKey,
                model,
                prompt,
                size,
                duration: videoDuration,
                resolution: videoResolution,
                generate_audio: generateAudio
            };
            
            // 设置视频生成模式
            if (currentMode === 'video-text') {
                body.mode = 'text';
            } else if (currentMode === 'video-image') {
                body.mode = 'image';
                if (imageData && imageData.length > 0) {
                    body.images = imageData;
                    console.log('[DEBUG] Sending imageData:', imageData);
                }
            } else if (currentMode === 'video-video') {
                body.mode = 'video';
                // 视频生视频需要提供可公网访问的视频URL
                const videoUrl = document.getElementById('videoUrl')?.value?.trim();
                if (videoUrl) {
                    body.video_urls = [videoUrl];
                } else {
                    throw new Error('请输入可公网访问的视频URL');
                }
            }
            
            const submitResp = await fetch('/api/video/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            
            const submitData = await submitResp.json();
            
            if (!submitResp.ok || submitData.error) {
                throw new Error(submitData.error || `提交失败: ${submitResp.status}`);
            }
            
            currentTaskId = submitData.taskId;
            document.getElementById('loadingText').textContent = '视频任务已提交，正在生成（可能需要几分钟）...';
            
            const result = await pollVideoTaskStatus(currentTaskId, apiKey);
            
            // 处理不同格式的返回结果
            let videoUrl = null;
            if (result.video && result.video.url) {
                videoUrl = result.video.url;
            } else if (result.videos && result.videos.length > 0 && result.videos[0].url) {
                videoUrl = result.videos[0].url;
            } else if (result.url) {
                videoUrl = result.url;
            }
            
            if (!videoUrl) {
                console.error('Unknown result format:', result);
                throw new Error('无法获取视频URL，返回格式异常');
            }
            
            currentVideoUrl = videoUrl;
            // 使用代理绕过 CORS
            const proxyUrl = `/api/proxy/video?url=${encodeURIComponent(videoUrl)}`;
            document.getElementById('resultVideo').src = proxyUrl;
            document.getElementById('resultVideo').style.display = 'block';
            document.getElementById('resultImage').style.display = 'none';
            document.getElementById('result').style.display = 'block';
            addToHistory(prompt, currentVideoUrl, size, model, currentMode);
        }
        
        async function generateKeyframesVideo(apiKey, model, size, prompt) {
            // 获取视频参数
            const videoDuration = parseInt(document.getElementById('videoDuration').value);
            const videoResolution = document.getElementById('videoResolution').value;
            const generateAudio = document.getElementById('generateAudio').checked;
            
            // 验证时长范围 (5-15秒)
            if (videoDuration < 5 || videoDuration > 15) {
                throw new Error('视频时长必须在 5-15 秒之间');
            }
            
            const body = {
                apiKey,
                model,
                prompt,
                size,
                duration: videoDuration,
                resolution: videoResolution,
                generate_audio: generateAudio,
                mode: 'keyframes',
                first_frame: firstFrameData,
                last_frame: lastFrameData
            };
            
            const submitResp = await fetch('/api/video/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            
            const submitData = await submitResp.json();
            
            if (!submitResp.ok || submitData.error) {
                throw new Error(submitData.error || `提交失败: ${submitResp.status}`);
            }
            
            currentTaskId = submitData.taskId;
            document.getElementById('loadingText').textContent = '首尾帧视频任务已提交，正在生成（可能需要几分钟）...';
            
            const result = await pollVideoTaskStatus(currentTaskId, apiKey);
            
            // 处理不同格式的返回结果
            let videoUrl = null;
            if (result.video && result.video.url) {
                videoUrl = result.video.url;
            } else if (result.videos && result.videos.length > 0 && result.videos[0].url) {
                videoUrl = result.videos[0].url;
            } else if (result.url) {
                videoUrl = result.url;
            }
            
            if (!videoUrl) {
                console.error('Unknown result format:', result);
                throw new Error('无法获取视频URL，返回格式异常');
            }
            
            currentVideoUrl = videoUrl;
            // 使用代理绕过 CORS
            const proxyUrl = `/api/proxy/video?url=${encodeURIComponent(videoUrl)}`;
            document.getElementById('resultVideo').src = proxyUrl;
            document.getElementById('resultVideo').style.display = 'block';
            document.getElementById('resultImage').style.display = 'none';
            document.getElementById('result').style.display = 'block';
            addToHistory(prompt, currentVideoUrl, size, model, currentMode);
        }
        
        async function pollVideoTaskStatus(taskId, apiKey) {
            const maxAttempts = 180; // 视频需要更长时间，最多等待 6 分钟
            const interval = 2000;
            
            for (let i = 0; i < maxAttempts; i++) {
                const resp = await fetch('/api/video/task', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ apiKey, taskId })
                });
                
                const data = await resp.json();
                
                if (data.error) throw new Error(data.error);
                
                const task = data.task;
                const status = task.status;
                const progress = task.progress || 0;
                
                document.getElementById('progressFill').style.width = `${progress}%`;
                document.getElementById('statusText').textContent = `进度: ${progress}%`;
                
                if (status === 'completed') {
                    return task.result;
                } else if (status === 'failed') {
                    throw new Error(task.error || '视频生成失败');
                }
                
                await new Promise(r => setTimeout(r, interval));
            }
            
            throw new Error('视频生成超时，请稍后查看历史记录');
        }
        
        async function pollTaskStatus(taskId, apiKey) {
            const maxAttempts = 60;
            const interval = 2000;
            
            for (let i = 0; i < maxAttempts; i++) {
                const resp = await fetch('/api/task', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ apiKey, taskId })
                });
                
                const data = await resp.json();
                
                if (data.error) throw new Error(data.error);
                
                const task = data.task;
                const progress = task.progress || 0;
                document.getElementById('progressFill').style.width = `${progress}%`;
                document.getElementById('statusText').textContent = `进度: ${progress}% - ${task.status}`;
                
                if (task.status === 'completed') return task.result;
                else if (task.status === 'failed') throw new Error(task.error || '任务生成失败');
                
                await new Promise(r => setTimeout(r, interval));
            }
            
            throw new Error('任务超时');
        }
        
        function showError(message) {
            document.getElementById('error').textContent = '⚠️ ' + message;
            document.getElementById('error').style.display = 'flex';
        }
        
        function downloadResult() {
            const isVideo = document.getElementById('resultVideo').style.display !== 'none';
            const url = isVideo ? currentVideoUrl : currentImageUrl;
            if (!url) return;
            const link = document.createElement('a');
            link.href = url;
            link.download = isVideo ? `ai-video-${Date.now()}.mp4` : `ai-image-${Date.now()}.png`;
            link.target = '_blank';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
        
        function addToHistory(prompt, url, size, model, mode) {
            let history = JSON.parse(localStorage.getItem('image_history') || '[]');
            const modeLabels = {
                'text': '文生图',
                'image': '图生图',
                'video-text': '文生视频',
                'video-image': '图生视频',
                'video-video': '视频生视频'
            };
            const modeLabel = modeLabels[mode] || mode;
            const isVideo = mode.startsWith('video');
            history.unshift({ prompt, url, size, model, mode: modeLabel, isVideo, time: new Date().toLocaleString('zh-CN') });
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
            
            container.innerHTML = history.map((item, index) => `
                <div class="history-item" onclick="viewHistory(${index})">
                    ${item.isVideo ? 
                        `<video src="/api/proxy/video?url=${encodeURIComponent(item.url)}" muted crossorigin="anonymous" playsinline style="width:100%;height:120px;object-fit:cover;border-radius:8px;"></video>` :
                        `<img src="${item.url}" alt="历史图片" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22100%22 height=%22100%22><rect fill=%22%231e293b%22 width=%22100%22 height=%22100%22/><text fill=%22%2364748b%22 x=%2250%22 y=%2250%22 text-anchor=%22middle%22>已过期</text></svg>'">`
                    }
                    <div class="prompt">${item.mode} | ${item.model}</div>
                </div>
            `).join('');
        }
        
        function viewHistory(index) {
            const history = JSON.parse(localStorage.getItem('image_history') || '[]');
            const item = history[index];
            if (item) {
                if (item.isVideo) {
                    currentVideoUrl = item.url;
                    document.getElementById('resultVideo').src = item.url;
                    document.getElementById('resultVideo').style.display = 'block';
                    document.getElementById('resultImage').style.display = 'none';
                } else {
                    currentImageUrl = item.url;
                    document.getElementById('resultImage').src = item.url;
                    document.getElementById('resultImage').style.display = 'block';
                    document.getElementById('resultVideo').style.display = 'none';
                }
                document.getElementById('prompt').value = item.prompt;
                document.getElementById('size').value = item.size;
                document.getElementById('model').value = item.model;
                document.getElementById('result').style.display = 'block';
                switchTab('generate');
            }
        }
        
        function handleModelChange() {
            // 如果当前是图片模式，根据选择的模型更新尺寸选项
            if (currentMode === 'text' || currentMode === 'image') {
                setupImageSizes();
            }
        }
    </script>
</body>
</html>
'''

class APIHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode('utf-8'))
        elif self.path == '/api/config':
            # 告诉前端是否有默认 API Key
            has_default_key = bool(os.environ.get('APIMART_API_KEY', ''))
            self._send_json(200, {'hasDefaultKey': has_default_key})
        elif self.path.startswith('/api/proxy/video'):
            # 视频代理 - 绕过 CORS
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
        else:
            self.send_response(404)
            self.end_headers()
    
    def _send_json(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _handle_generate(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = json.loads(self.rfile.read(content_length))
            
            api_key = post_data.get('apiKey', '')
            # 处理服务器默认Key的特殊标记
            if api_key == '__SERVER_DEFAULT__':
                api_key = os.environ.get('APIMART_API_KEY', '')
            # 如果仍然为空，尝试从环境变量获取
            if not api_key:
                api_key = os.environ.get('APIMART_API_KEY', '')
            
            model = post_data.get('model', 'image2.0')
            prompt = post_data.get('prompt')
            size = post_data.get('size', '1024x1024')
            mode = post_data.get('mode', 'text')
            
            if not api_key:
                return self._send_json(400, {'error': 'API Key is required'})
            
            request_data = {'model': model, 'prompt': prompt, 'size': size, 'n': 1}
            
            if mode == 'image':
                # 支持多图上传
                images_base64 = post_data.get('images')  # 多图数组
                image_base64 = post_data.get('image')    # 单图兼容
                
                image_urls = []
                if images_base64 and isinstance(images_base64, list):
                    # 多图模式
                    image_urls = [f"data:image/png;base64,{img}" for img in images_base64]
                elif image_base64:
                    # 单图兼容模式
                    image_urls = [f"data:image/png;base64,{image_base64}"]
                else:
                    return self._send_json(400, {'error': 'Image data is required'})
                
                # 图生图强制使用 gpt-image-2，尺寸使用比例格式
                request_data = {
                    'model': 'gpt-image-2',
                    'prompt': prompt,
                    'size': size,  # 比例格式如 1:1, 16:9 等
                    'n': 1,
                    'image_urls': image_urls
                }
            
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
    
    def _handle_task_query(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = json.loads(self.rfile.read(content_length))
            
            api_key = post_data.get('apiKey') or os.environ.get('APIMART_API_KEY', '')
            task_id = post_data.get('taskId')
            
            if not api_key or not task_id:
                return self._send_json(400, {'error': 'API Key and Task ID are required'})
            
            resp = requests_session.get(
                f"{API_BASE}/tasks/{task_id}",
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=30
            )
            
            data = resp.json()
            
            if resp.status_code != 200 or data.get('code') != 200:
                error_msg = data.get('message', f'API Error: {resp.status_code}')
                return self._send_json(500, {'error': error_msg})
            
            self._send_json(200, {'task': data['data']})
            
        except Exception as e:
            self._send_json(500, {'error': str(e)})
    
    def _handle_video_generate(self):
        """处理视频生成请求"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = json.loads(self.rfile.read(content_length))
            
            # 调试日志
            print(f"[DEBUG] Received video request: {json.dumps(post_data, ensure_ascii=False)}")
            
            api_key = post_data.get('apiKey', '')
            # 处理服务器默认Key的特殊标记
            if api_key == '__SERVER_DEFAULT__':
                api_key = os.environ.get('APIMART_API_KEY', '')
            # 如果仍然为空，尝试从环境变量获取
            if not api_key:
                api_key = os.environ.get('APIMART_API_KEY', '')
            # 如果仍然为空，使用硬编码的测试Key（仅用于测试）
            if not api_key:
                api_key = 'sk-K6j8S971PxjDspBGX9igHzxCh6Z9d6fbH266Sj3jTp3rBBwC'
            
            model = post_data.get('model', 'doubao-seedance-2.0')
            prompt = post_data.get('prompt', '') or ''
            mode = post_data.get('mode', 'text')  # text, image, video
            size = post_data.get('size', '16:9')
            duration = post_data.get('duration', 5)
            resolution = post_data.get('resolution', '720p')
            generate_audio = post_data.get('generate_audio', False)
            # 处理前端发送的字符串布尔值
            if isinstance(generate_audio, str):
                generate_audio = generate_audio.lower() == 'true'
            
            # 确保 duration 是整数
            try:
                duration = int(duration)
            except (ValueError, TypeError):
                duration = 5
            
            if not api_key:
                print("[ERROR] API Key is missing")
                return self._send_json(400, {'error': 'API Key is required. Please set your APIMart API Key in the settings.'})
            
            # prompt 对所有视频模式都是必需的
            if not prompt:
                return self._send_json(400, {'error': 'Prompt is required for video generation'})
            
            # 验证时长范围 (5-15秒)
            if duration < 5 or duration > 15:
                return self._send_json(400, {'error': f'视频时长必须在 5-15 秒之间，当前: {duration}'})
            
            # 构建请求数据 - 与测试文件保持一致
            request_data = {
                'model': model,
                'prompt': prompt,
                'resolution': resolution,
                'size': size,
                'duration': duration,
                'generate_audio': bool(generate_audio)
            }
            
            # 调试日志
            print(f"[DEBUG] Video request: {json.dumps(request_data, ensure_ascii=False)}")
            print(f"[DEBUG] API_KEY present: {bool(api_key)}")
            print(f"[DEBUG] Mode: {mode}, Duration type: {type(duration)}, Value: {duration}")
            
            # 图生视频 - 使用 image_urls 数组
            if mode == 'image':
                images = post_data.get('images', [])
                print(f"[DEBUG] Received images: {images}")
                print(f"[DEBUG] images type: {type(images)}")
                if images and len(images) > 0:
                    # 检查第一个元素是否是URL（以http开头）
                    first_img = images[0] if isinstance(images, list) else images
                    print(f"[DEBUG] First image: {first_img}")
                    print(f"[DEBUG] First image type: {type(first_img)}")
                    if isinstance(first_img, str) and first_img.startswith('http'):
                        # 使用 image_url 数组（支持 https URL）
                        request_data['image_url'] = images if isinstance(images, list) else [images]
                        print(f"[DEBUG] Using image_url with URLs: {request_data['image_url']}")
                    else:
                        # 上传 base64 图片到 Cloudinary 获取 URL
                        try:
                            print(f"[DEBUG] Uploading image to Cloudinary...")
                            # 清理 base64 数据（移除可能的 data:image 前缀）
                            clean_base64 = first_img
                            if ',' in clean_base64:
                                clean_base64 = clean_base64.split(',')[1]
                            # 解码 base64
                            image_data = base64.b64decode(clean_base64)
                            # 上传到 Cloudinary
                            upload_result = cloudinary.uploader.upload(
                                io.BytesIO(image_data),
                                folder="apimart_video"
                            )
                            image_url = upload_result.get('secure_url')
                            request_data['image_url'] = [image_url]
                            print(f"[DEBUG] Uploaded to Cloudinary: {image_url}")
                        except Exception as e:
                            print(f"[ERROR] Cloudinary upload failed: {e}")
                            import traceback
                            traceback.print_exc()
                            return self._send_json(500, {'error': f'图片上传失败: {str(e)}'})
                else:
                    return self._send_json(400, {'error': '请提供图片用于图生视频'})
            
            # 视频生视频
            elif mode == 'video':
                video_urls = post_data.get('video_urls', [])
                if video_urls and len(video_urls) > 0:
                    request_data['video_urls'] = video_urls
                else:
                    return self._send_json(400, {'error': '请提供视频URL用于视频生视频'})
            
            # 首尾帧视频
            elif mode == 'keyframes':
                first_frame = post_data.get('first_frame', '')
                last_frame = post_data.get('last_frame', '')
                
                if not first_frame or not last_frame:
                    return self._send_json(400, {'error': '请提供首帧和尾帧图片'})
                
                try:
                    print(f"[DEBUG] Uploading keyframes to Cloudinary...")
                    # 上传首帧
                    clean_first = first_frame.split(',')[1] if ',' in first_frame else first_frame
                    first_data = base64.b64decode(clean_first)
                    first_result = cloudinary.uploader.upload(
                        io.BytesIO(first_data),
                        folder="apimart_keyframes"
                    )
                    first_url = first_result.get('secure_url')
                    
                    # 上传尾帧
                    clean_last = last_frame.split(',')[1] if ',' in last_frame else last_frame
                    last_data = base64.b64decode(clean_last)
                    last_result = cloudinary.uploader.upload(
                        io.BytesIO(last_data),
                        folder="apimart_keyframes"
                    )
                    last_url = last_result.get('secure_url')
                    
                    # 使用 image_with_roles 参数
                    request_data['image_with_roles'] = [
                        {'url': first_url, 'role': 'first_frame'},
                        {'url': last_url, 'role': 'last_frame'}
                    ]
                    print(f"[DEBUG] Keyframes uploaded: first={first_url}, last={last_url}")
                except Exception as e:
                    print(f"[ERROR] Keyframes upload failed: {e}")
                    import traceback
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
            
            print(f"[DEBUG] Video API response: status={resp.status_code}")
            print(f"[DEBUG] Video API response body: {json.dumps(data, ensure_ascii=False)}")
            
            if resp.status_code != 200 or data.get('code') != 200:
                error_msg = data.get('message', f'API Error: {resp.status_code}')
                print(f"[ERROR] Video API error: {error_msg}")
                # 如果是 API 返回的 400 错误，转发给前端
                if resp.status_code == 400:
                    return self._send_json(400, {'error': error_msg})
                return self._send_json(500, {'error': error_msg})
            
            task_id = data['data'][0]['task_id']
            self._send_json(200, {'taskId': task_id})
            
        except Exception as e:
            print(f"[ERROR] Video generate exception: {e}")
            self._send_json(500, {'error': str(e)})
    
    def _handle_video_proxy(self):
        """视频代理 - 绕过 CORS 限制"""
        try:
            from urllib.parse import parse_qs, urlparse
            query = urlparse(self.path).query
            params = parse_qs(query)
            video_url = params.get('url', [''])[0]
            
            if not video_url:
                self.send_response(400)
                self.end_headers()
                return
            
            # 下载视频并转发
            resp = requests_session.get(video_url, timeout=60, stream=True)
            
            self.send_response(resp.status_code)
            self.send_header('Content-Type', resp.headers.get('Content-Type', 'video/mp4'))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'public, max-age=3600')
            self.end_headers()
            
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    self.wfile.write(chunk)
                    
        except Exception as e:
            print(f"[ERROR] Video proxy error: {e}")
            self.send_response(500)
            self.end_headers()
    
    def _handle_video_task_query(self):
        """查询视频生成任务状态"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = json.loads(self.rfile.read(content_length))
            
            api_key = post_data.get('apiKey') or os.environ.get('APIMART_API_KEY', '')
            task_id = post_data.get('taskId')
            
            if not api_key or not task_id:
                return self._send_json(400, {'error': 'API Key and Task ID are required'})
            
            resp = requests_session.get(
                f"{API_BASE}/tasks/{task_id}",
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=30
            )
            
            data = resp.json()
            
            if resp.status_code != 200 or data.get('code') != 200:
                error_msg = data.get('message', f'API Error: {resp.status_code}')
                return self._send_json(500, {'error': error_msg})
            
            self._send_json(200, {'task': data['data']})
            
        except Exception as e:
            self._send_json(500, {'error': str(e)})
    
    def log_message(self, format, *args):
        print(f"[Server] {format % args}")

def run_server(port=None):
    # 云平台使用环境变量 PORT (Render/Railway 等)
    port = int(os.environ.get('PORT', port or 8080))
    # 云平台需要绑定 0.0.0.0，本地开发绑定 127.0.0.1
    is_cloud = os.environ.get('PORT') or os.environ.get('RENDER') or os.environ.get('RAILWAY_SERVICE_ID')
    host = '0.0.0.0' if is_cloud else '127.0.0.1'
    
    server = HTTPServer((host, port), APIHandler)
    
    print("=" * 60)
    print("APIMart Image Generator")
    print("=" * 60)
    print(f"\nServer running at: http://{host}:{port}")
    print("\nPress Ctrl+C to stop")
    print("=" * 60 + "\n")
    
    # 本地开发时自动打开浏览器
    if host == '127.0.0.1':
        def open_browser():
            import time
            time.sleep(1)
            webbrowser.open(f'http://127.0.0.1:{port}')
        threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n[Stop] 服务器已停止")

if __name__ == '__main__':
    run_server()
