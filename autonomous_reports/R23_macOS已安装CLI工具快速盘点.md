# macOS已安装CLI工具快速盘点

## 赛季背景
2026-04-29 | 发现 | Apple Silicon Mac mini, macOS 15 (Sequoia)
目的：盘点现有CLI工具生态，判断是否值得深度挖掘

## 数据来源
| 数据源 | 工具数 | 说明 |
|--------|--------|------|
| brew list --formula | 117 | 其中48个是库依赖，69个有bin可执行 |
| /opt/homebrew/bin | 409 | 含brew formula + symlinks |
| /usr/local/bin | 9 | Docker, ollama等 |
| /usr/bin | 915 | 系统原生工具 |
| ~/.local/bin | 0 | pip安装的CLI未建立bin链接 |
| ~/.cargo/bin | 0 | Rust工具链未安装 |
| ~/go/bin | 0 | Go工具链未安装 |
| npm global | 2 | claude-code, npm |

## 核心发现

### ✅ 已安装的关键工具
| 类别 | 工具 | 版本/路径 |
|------|------|----------|
| **AI/LLM** | ollama | /usr/local/bin (本地LLM运行) |
| | claude-code | npm global (Anthropic CLI) |
| | tesseract | v5 (OCR引擎) |
| **开发** | python3 | .venv/GA专用 |
| | node | brew (JavaScript运行时) |
| | cmake, gh, pyenv | brew (构建/GitHub CLI/Python版本管理) |
| **媒体** | ffmpeg | brew (视频处理) |
| | opencv-python | pip 4.13.0 (计算机视觉) |
| | pillow | pip 12.2.0 (图像处理) |
| **网络** | cliproxyapi | brew (Clash代理API) |
| | jq | /usr/bin (JSON处理) |
| **数据** | sqlite3 | /usr/bin + brew (数据库) |

### ❌ 值得注意的缺失
| 工具 | 用途 | 建议 |
|------|------|------|
| ripgrep (rg) | 极速文件搜索 | 适合GA代码搜索，替代grep |
| fd | 更快的find | 文件查找 |
| bat | 语法高亮cat | 代码阅读 |
| fzf | 模糊搜索 | 命令行效率 |
| yt-dlp | 视频下载 | 内容获取管道 |
| tmux | 终端复用 | 长期任务管理 |

### 📊 pip自动化相关包
- opencv-python 4.13.0 + pytesseract + pillow → 视觉管道完整
- requests + beautifulsoup4 → 网页抓取完整
- streamlit 1.56.0 → 可快速搭建GUI展示

### 📌 亮点发现
1. **cliproxyapi** (Clash代理API库) 存在 → 暗示有代理环境，网络抓取/搜索可能需要考虑代理
2. **claude-code** (Anthropic CLI) 已安装 → 用户熟悉Claude生态
3. **opencv + tesseract + pillow** 全齐 → 视觉处理能力强，无需额外安装

## 结论：不值得深挖 ❌
- 环境工具栈清晰：**brew包 + pip包为主**，无特殊/隐藏工具
- 117 brew formula中48个(41%)是ffmpeg的库依赖，真正的用户工具较少
- 无Rust/Go本地开发链 → 说明不涉及底层/编译型项目
- 建议未来遇到需求时按需安装，无需预铺

## 记忆更新建议
- 无，工具环境较干净，不构成特殊知识
