# 一键上传脚本 - 把修改后的 app.py 上传到 GitHub
# 使用方法: 把 GITHUB_TOKEN 替换成你的 token，然后运行这个脚本

$GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxx"  # <-- 修改这里

if ($GITHUB_TOKEN -eq "ghp_xxxxxxxxxxxxxxxxxxxx") {
    Write-Host "❌ 请先修改脚本中的 GITHUB_TOKEN!" -ForegroundColor Red
    Write-Host "获取 Token: https://github.com/settings/tokens"
    exit 1
}

$REPO = "loveconan520-boop/apimart-image-generator"
$FILE = "app.py"
$BRANCH = "main"

Write-Host "正在读取文件..." -ForegroundColor Cyan
$content = Get-Content -Raw -Path $FILE -Encoding UTF8
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$base64 = [Convert]::ToBase64String($bytes)

Write-Host "正在获取文件信息..." -ForegroundColor Cyan
$headers = @{
    "Authorization" = "token $GITHUB_TOKEN"
    "Accept" = "application/vnd.github.v3+json"
}

try {
    $info = Invoke-RestMethod -Uri "https://api.github.com/repos/$REPO/contents/$FILE?ref=$BRANCH" -Headers $headers
    $sha = $info.sha
    Write-Host "文件已存在，准备更新 (SHA: $sha)" -ForegroundColor Yellow
} catch {
    $sha = $null
    Write-Host "文件不存在，准备创建" -ForegroundColor Green
}

$body = @{
    message = "fix: use server default API key when localStorage is empty"
    content = $base64
    branch = $BRANCH
} | ConvertTo-Json

if ($sha) {
    $body = @{
        message = "fix: use server default API key when localStorage is empty"
        content = $base64
        sha = $sha
        branch = $BRANCH
    } | ConvertTo-Json
}

Write-Host "正在上传..." -ForegroundColor Cyan
try {
    $result = Invoke-RestMethod -Uri "https://api.github.com/repos/$REPO/contents/$FILE" -Method Put -Headers $headers -Body $body
    Write-Host "✅ 上传成功!" -ForegroundColor Green
    Write-Host "Commit: $($result.commit.sha.Substring(0,7))"
} catch {
    Write-Host "❌ 上传失败: $_" -ForegroundColor Red
}
