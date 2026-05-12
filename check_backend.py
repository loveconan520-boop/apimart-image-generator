import sys
sys.path.insert(0, 'C:\\Users\\zjj\\.qclaw\\workspace\\apimart-image-generator-v2')

# 读取 app.py 内容
with open('C:\\Users\\zjj\\.qclaw\\workspace\\apimart-image-generator-v2\\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 检查后端 API
checks = [
    ('_handle_video_generate method', '_handle_video_generate' in content),
    ('_handle_video_task_query method', '_handle_video_task_query' in content),
    ('/api/video/generate route', "self.path == '/api/video/generate'" in content),
    ('/api/video/task route', "self.path == '/api/video/task'" in content),
    ('videos/generations endpoint', 'videos/generations' in content),
]

print("Backend API Check:")
print("-" * 40)
for name, found in checks:
    status = 'OK' if found else 'MISSING'
    print(f'{status} {name}')
