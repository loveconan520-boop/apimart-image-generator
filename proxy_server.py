#!/usr/bin/env python3
"""
APIMart API 代理服务器 v3
使用 requests 库，更可靠的 header 传递
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import requests

API_BASE = "https://api.apimart.ai/v1"

class CORSRequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        if self.path in ('/', '/health'):
            self._send_json(200, {'status': 'ok', 'message': 'APIMart Proxy v3 Running'})
        elif self.path.startswith('/api/tasks/'):
            self._proxy_task_query()
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/images/generations':
            self._proxy_image_generation()
        else:
            self.send_response(404)
            self.end_headers()
    
    def _send_json(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _proxy_image_generation(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # 获取 Authorization header
            auth_header = self.headers.get('Authorization', '')
            
            # 转发请求
            resp = requests.post(
                f"{API_BASE}/images/generations",
                json=request_data,
                headers={'Authorization': auth_header, 'Content-Type': 'application/json'},
                timeout=30
            )
            
            self._send_json(resp.status_code, resp.json())
            
        except requests.exceptions.RequestException as e:
            self._send_json(502, {'code': 502, 'message': f'API Request Failed: {str(e)}'})
        except json.JSONDecodeError:
            self._send_json(500, {'code': 500, 'message': 'Invalid JSON response from API'})
        except Exception as e:
            self._send_json(500, {'code': 500, 'message': f'Proxy Error: {str(e)}'})
    
    def _proxy_task_query(self):
        try:
            task_id = self.path.split('/api/tasks/')[1]
            auth_header = self.headers.get('Authorization', '')
            
            resp = requests.get(
                f"{API_BASE}/tasks/{task_id}",
                headers={'Authorization': auth_header},
                timeout=30
            )
            
            self._send_json(resp.status_code, resp.json())
            
        except requests.exceptions.RequestException as e:
            self._send_json(502, {'code': 502, 'message': f'API Request Failed: {str(e)}'})
        except Exception as e:
            self._send_json(500, {'code': 500, 'message': f'Proxy Error: {str(e)}'})
    
    def log_message(self, format, *args):
        print(f"[Proxy] {self.address_string()} - {format % args}")

def run_proxy_server(port=3000):
    try:
        server = HTTPServer(('127.0.0.1', port), CORSRequestHandler)
        bind_addr = '127.0.0.1'
    except:
        server = HTTPServer(('0.0.0.0', port), CORSRequestHandler)
        bind_addr = '0.0.0.0'
    
    print("=" * 50)
    print("[OK] APIMart Proxy Server v3 Started")
    print(f"[Bind] {bind_addr}:{port}")
    print(f"[URL] http://127.0.0.1:{port}")
    print(f"[API] http://127.0.0.1:{port}/api/images/generations")
    print(f"[API] http://127.0.0.1:{port}/api/tasks/<task_id>")
    print("\n[提示] 保持此窗口运行，按 Ctrl+C 停止")
    print("=" * 50)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n[Stop] 代理服务器已停止")

if __name__ == '__main__':
    run_proxy_server()
