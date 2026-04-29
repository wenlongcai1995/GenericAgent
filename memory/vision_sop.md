# Vision API SOP

## ⚠️ 前置规则（必须遵守）

1. **先枚举窗口**：调用 vision 前必须先用 `pygetwindow` 枚举窗口标题，确认目标窗口存在且已激活到前台。窗口不存在就不要截图。
2. **🚫 禁止全屏截图**：必须先利用ljqCtrl截取窗口区域。能截局部（如标题栏）就不截整窗口，能截窗口就绝不全屏。全屏截图在任何场景下都不允许。
3. **能不用 vision 就不用**：如果窗口标题/本地 OCR（`ocr_utils.py`）能获取所需信息，就不要调用 vision API，省 token 且更可靠。Vision 是最后手段。

## 🐛 macOS 15+ 大坑：screencapture -R 损坏

**macOS 15 (Sequoia) 上 `screencapture -R x,y,w,h` 已完全失效**（安全回归），即使 `-R 0,0,100,100` 也报错。但 `screencapture -x`（全屏）正常。

**影响范围**：
- PIL `ImageGrab.grab(bbox=...)` 内部调用 `screencapture -R` → 会失败
- `screen_capture_pipeline.py` 已内置修复：`_grab_region()` 做全屏 + PIL crop
- 任何新建截图代码必须：先全屏截图 → 再 `PIL.Image.crop(bbox)`，禁止直接传 bbox

**验证命令**：
```bash
screencapture -x /tmp/test.png                          # ✅ 正常
screencapture -R 0,0,100,100 -x /tmp/test.png           # ❌ 失败(所有macOS 15+)
```

## 快速用法

```python
from vision_api import ask_vision
result = ask_vision(image, prompt="描述图片内容", backend="ollama", timeout=60, max_pixels=1_440_000)
# image: 文件路径(str/Path) 或 PIL Image
# backend: 'ollama'(默认) | 'claude' | 'openai' | 'modelscope'
# 返回 str：成功为模型回复，失败为 'Error: ...'
```

## 补充：Ollama 本地视觉模型（完全免费）

如果以上后端均不可用，可使用本地 Ollama 的 qwen3-vl 模型：

```bash
# 安装运行
ollama pull qwen3-vl:8b       # 首次拉取模型
ollama serve                  # 启动服务（默认 11434 端口）
```

`vision_api.py` 已内置 ollama 后端，设置 `DEFAULT_BACKEND = 'ollama'` 即可。依赖：Ollama ≥0.17.7，内存≥12GB，模型约6.1GB。⚠️ 实测响应速度约35-55秒/次（简单场景~35s，复杂UI/文字~55s），旧版记录的15-25s已过时。

## ⚠️ Ollama 代理陷阱（高频坑）

**现象**：Ollama调用返回超时/连接失败，但`ollama serve`正常运行。
**原因**：系统HTTP_PROXY/HTTPS_PROXY环境变量（如Clash代理7897端口）导致127.0.0.1请求被转发到代理，而非直连Ollama服务。
**修复**：设置`no_proxy=127.0.0.1,localhost`，或在`_call_ollama()`中为requests加`proxies={'http': None, 'https': None}`。
**验证**：`curl -x "" http://127.0.0.1:11434/api/tags` 应即时返回模型列表。

## 如果没有 `vision_api.py`，初次构建vision能力

1. 复制 `memory/vision_api.template.py` → `memory/vision_api.py`
2. 只改头部"用户配置区"：去 `mykey.py` 里扫描变量名（⚠️ 只看名字，禁止输出 apikey 值），尝试找能用配置名填入 `CLAUDE_CONFIG_KEY` / `OPENAI_CONFIG_KEY`，`DEFAULT_BACKEND` 选后端，并测试
3. 保底：没有可用 config 时去 `https://modelscope.cn/my/myaccesstoken` 申请 token 填入 `MODELSCOPE_API_KEY`
