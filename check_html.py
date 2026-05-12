import sys
sys.path.insert(0, 'C:\\Users\\zjj\\.qclaw\\workspace\\apimart-image-generator-v2')
from app import HTML_CONTENT

# 检查关键元素
checks = [
    ('video-text tab', 'tab-video-text' in HTML_CONTENT),
    ('video-image tab', 'tab-video-image' in HTML_CONTENT),
    ('video-video tab', 'tab-video-video' in HTML_CONTENT),
    ('video-upload-panel', 'video-upload-panel' in HTML_CONTENT),
    ('resultVideo element', 'resultVideo' in HTML_CONTENT),
    ('seedance model', 'doubao-seedance-2.0' in HTML_CONTENT),
    ('video generate API', '/api/video/generate' in HTML_CONTENT),
    ('generateVideo function', 'generateVideo' in HTML_CONTENT),
    ('handleVideoUpload function', 'handleVideoUpload' in HTML_CONTENT),
    ('pollVideoTaskStatus function', 'pollVideoTaskStatus' in HTML_CONTENT),
]

print("HTML Content Check:")
print("-" * 40)
for name, found in checks:
    status = 'OK' if found else 'MISSING'
    print(f'{status} {name}')

# 统计 HTML 大小
print(f"\nHTML size: {len(HTML_CONTENT)} characters")
