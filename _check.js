
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
            const input = document.getElementById('passwordInput');
            const error = document.getElementById('passwordError');
            if (!input || !error) { alert('页面元素未加载，请刷新重试'); return; }
            try {
                const resp = await fetch('/api/auth', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ password: input.value })
                });
                const data = await resp.json();
                if (data.success) {
                    document.getElementById('passwordOverlay').style.display = 'none';
                    document.getElementById('mainContainer').style.display = 'block';
                    sessionStorage.setItem('authenticated', 'true');
                } else {
                    error.style.display = 'block';
                    input.value = '';
                }
            } catch (e) {
                error.textContent = '验证失败: ' + e.message;
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

        // 回车提交密码 + 按钮点击（优先绑定，防止后续代码报错阻断）
        (function() {
            const passwordInput = document.getElementById('passwordInput');
            const loginBtn = document.getElementById('loginBtn');
            if (passwordInput) {
                passwordInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') checkPassword();
                });
            }
            if (loginBtn) {
                loginBtn.addEventListener('click', checkPassword);
            }
        })();

        // 其他初始化（独立try-catch，不影响密码功能）
        (function() {
            try { initAuth(); } catch(e) { console.error('initAuth error:', e); }
            try { switchMode('text'); } catch(e) { console.error('switchMode error:', e); }
            try { loadHistory(); } catch(e) { console.error('loadHistory error:', e); }
            try { loadApiKey(); } catch(e) { console.error('loadApiKey error:', e); }
        })();

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
                        '<img src="' + item.url + '" alt="历史图片" onerror="this.style.display=&quot;none&quot;">'
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
    