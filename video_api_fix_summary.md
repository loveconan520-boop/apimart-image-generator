# APIMart 视频生成 API 修正总结

## 问题诊断

根据官方文档 https://docs.apimart.ai/cn/api-reference/videos/doubao-seedance-2-0/generation

## 修正内容

### 1. 图生视频 - 已修正 ✅
- **问题**：之前使用Base64编码的图片
- **修正**：改为使用公网可访问的图片URL (`image_urls` 数组)
- **前端**：新增 `video-image-panel` 面板，包含图片URL输入框
- **后端**：接收 `image_urls` 参数并直接转发给API

### 2. 视频生视频 - 已修正 ✅
- **问题**：之前使用Base64编码的视频文件上传
- **修正**：改为使用公网可访问的视频URL (`video_urls` 数组)
- **前端**：将文件上传改为URL输入框 (`videoUrl`)
- **后端**：接收 `video_urls` 参数并直接转发给API

### 3. 有声视频 - 已添加 ✅
- **新增**：`generate_audio` 复选框，控制是否生成配套音频
- **前端**：添加复选框UI
- **后端**：接收 `generate_audio` 布尔值并传递给API

### 4. 画面比例 - 已更新 ✅
- **新增**：`adaptive` (自适应) 选项

## API参数格式验证

测试脚本验证三种模式均返回402（余额不足），证明参数格式正确：

### 文生视频
```json
{
  "model": "doubao-seedance-2.0",
  "prompt": "一只小猫对着镜头打哈欠",
  "resolution": "720p",
  "size": "16:9",
  "duration": 5,
  "generate_audio": false
}
```

### 图生视频
```json
{
  "model": "doubao-seedance-2.0",
  "prompt": "小猫站起来走向镜头",
  "image_urls": ["https://example.com/cat.jpg"],
  "resolution": "720p",
  "size": "16:9",
  "duration": 5,
  "generate_audio": false
}
```

### 视频生视频
```json
{
  "model": "doubao-seedance-2.0",
  "prompt": "将视频风格转换为动漫风格",
  "video_urls": ["https://example.com/video.mp4"],
  "resolution": "720p",
  "size": "16:9",
  "duration": 5,
  "generate_audio": false
}
```

## 使用说明

1. **文生视频**：输入文字描述，选择模型和参数，点击生成
2. **图生视频**：输入公网可访问的图片URL（如 https://example.com/image.jpg）
3. **视频生视频**：输入公网可访问的视频URL（如 https://example.com/video.mp4）
4. **有声视频**：勾选"生成配套音频"选项

## 注意事项

- 图片/视频URL必须是公网可访问的，不能使用本地文件或Base64
- 参考视频分辨率需要在480P~720P之间
- 参考视频不可出现真人
- 账户需要有足够余额才能生成视频
