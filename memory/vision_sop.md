# Vision API SOP

## ⚠️ 前置规则（必须遵守）

1. **先枚举窗口**：调用 vision 前先用 `screen_capture_pipeline.py --list-apps` 或 `inference.capture_app()` 确认目标窗口存在。窗口不存在就不要截图。
2. **🚫 禁止全屏截图**：必须用 `screen_capture_pipeline --app "AppName"` 或 `inference.capture_app()` 截取窗口区域。能截局部就不截整窗口，能截窗口就绝不全屏。全屏截图在任何场景下都不允许。
3. **能不用 vision 就不用**：如果本地 OCR（`screen_capture_pipeline --ocr --app "AppName"` 或 `inference.capture_app(do_ocr=True)`）能获取所需信息，就不要调用 vision API，省 token 且更可靠。Vision 是最后手段。

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

## 🔗 screen_capture_pipeline 集成——一键截图+分析

`screen_capture_pipeline.py` 是截图+分析的统一入口，已集成到 `inference.capture_app()`。

### CLI 快速用法

```bash
# 列出所有可截取的窗口
python memory/screen_capture_pipeline.py --list-apps

# 截取某应用窗口 + OCR
python memory/screen_capture_pipeline.py --app "Terminal" --ocr

# 截取 + OCR + Vision分析
python memory/screen_capture_pipeline.py --app "Cursor" --ocr --vision "截图里有几个按钮?"

# 指定区域截取
python memory/screen_capture_pipeline.py --bbox 100 100 800 600 --ocr
```

### 程序化 API（推荐）

```python
from memory.inference import inference

# 只截图+OCR（最快）
result = inference.capture_app("Terminal", do_ocr=True, vision_prompt=None)
print(result["ocr"]["text"])          # OCR识别文字
print(result["bbox"])                 # 窗口坐标 [x1,y1,x2,y2]

# 截图+OCR+Vision分析（全链路）
result = inference.capture_app("Cursor", do_ocr=True,
                                vision_prompt="界面上有哪些功能区?")
print(result.get("vision", ""))       # Vision分析结果

# 仅截图（不分析，最小开销）
result = inference.capture_app("Terminal", do_ocr=False)
```

### 输出格式

返回结构化 dict：
```python
{
    "status": "ok",          # "ok" 或 "error"
    "app": "Terminal",       # 请求的应用名
    "matched_owner": "Terminal",  # 实际匹配的窗口所有者
    "bbox": [100, 200, 900, 700], # 窗口物理坐标
    "ocr": {                 # 仅当 do_ocr=True
        "text": "...",       # 全部识别文字
        "lines": [...],      # 分行列表
        "num_lines": 8,
        "elapsed_s": 0.35
    },
    "vision": "..."          # 仅当 vision_prompt 指定
}
```

### 效率指南

| 场景 | 推荐用法 | 耗时 |
|------|---------|------|
| 快速看文字 | `--app "Terminal" --ocr` | ~0.3s |
| 完整UI理解 | `--app "Cursor" --ocr --vision "描述界面"` | ~35-55s |
| 仅截图不分析 | `--app "Finder"` (不加--ocr/--vision) | ~0.1s |
| 代码内调用 | `inference.capture_app("App", do_ocr=True)` | ~0.3s |

## 快速用法

```python
from vision_api import ask_vision

# 推荐Prompt（v2优化版，经R35实测验证）:
# - 比"描述图片内容"快1.5-2倍 (29s vs 49s)
# -中文OCR准确率85%+，颜色识别准确率95%+
# - 注意：结构化/编号列表prompt在temperature=0时会导致qwen3-vl返回空（贪婪解码死锁）
# - 若需结构化输出，建议设置temperature≥0.7，此时结构化prompt正常工作且速度与自然语言相当
OPTIMIZED_PROMPT = ("请仔细描述图片内容。注意：中文文字要逐字准确识别，"
                    "不要遗漏也不要写错别字；颜色要用标准名称描述"
                    "（红/橙/黄/绿/蓝/紫/黑/白/灰）。")

result = ask_vision(image, prompt=OPTIMIZED_PROMPT, backend="ollama", timeout=60, max_pixels=1_440_000)
# image: 文件路径(str/Path) 或 PIL Image
# backend: 'ollama'(默认) | 'claude' | 'openai' | 'modelscope'
# 返回 str：成功为模型回复，失败为 'Error: ...'

# 已知问题（R35发现）:
# 1. "vl→vi"混淆：行尾"vl"被误认为"vi"（ollama tokenizer边界问题）
# 2. 长文本截断：密集中文超1024 tokens时被截尾
# 3. 结构化prompt+temp=0返回空：编号列表/JSON格式prompt在temperature=0时导致贪婪解码死锁，设temperature≥0.7即可正常
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
