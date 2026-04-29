# R27 Shell 历史行为模式分析

> 来源：`~/.zsh_history` (467条记录，15KB)
> 分析日期：2026-04-30 00:00+

## 用户画像

**核心身份：** AI/ML 开发者 + 全栈工程师，macOS (Apple Silicon)

## 命令频率 Top 15

| 排名 | 命令 | 次数 | 解读 |
|:---:|:----:|:---:|:----:|
| 1 | ls | 84 | 高频文件浏览 |
| 2 | cd | 54 | 活跃目录切换 |
| 3 | python | 40 | **主要编程语言** |
| 4 | vim | 38 | **主力编辑器** |
| 5 | git | 31 | 标准版本控制 |
| 6 | brew | 19 | macOS 包管理 |
| 7 | ollama | 18 | **本地 LLM 重度用户** |
| 8 | pip | 14 | Python 包管理 |
| 9 | source | 13 | 频繁加载 shell 配置 |
| 10 | echo | 8 | 调试/检查 |
| 11 | sh | 7 | 脚本执行 |
| 12 | docker / npm | 各7 | 容器 / JS 生态 |
| 13 | mkdir | 6 | 组织项目 |
| 14 | gh | 4 | GitHub CLI |
| 15 | cliproxyapi | 4 | 网络代理工具 |

## 关键洞察

### 1. Python 为中心的技术栈
- PyTorch + Metal (Apple Silicon GPU) → ML 工作流
- `python launch.pyw` / `python fsapp.py` → 自有项目
- pip 频繁安装包 → 多项目/快速迭代

### 2. 本地 AI 能力
- **ollama serve + ollama list** → 本地运行 LLM（如 qwen3-vl）
- **cliproxyapi** → 代理配置，可能用于 AI API 调用
- 与 vision_api.py 的 Ollama 默认配置一致

### 3. 开发习惯
- vim 作为主力编辑器（38次），快速编辑
- git status（8次）> git add/commit → "检查 > 提交" 谨慎风格
- 频繁 source ~/.zshrc（13次）→ 经常改配置

### 4. 涉及项目
- tennis-training → 姿态估计/运动分析
- GenericAgent → 当前项目
- cliproxyapi 配置 → 代理工具管理

### 5. 工具生态
- 未使用 tmux/screen → 单窗口工作流
- 少量 JS/Node (npm 7, npx 2) → 非主力
- Docker 活跃 (docker info, docker) → 容器化部署

## 可优化方向
1. **ls 滥用**（84次）：可用 alias `ll` 或 exa/lsd 替代
2. **cd 频繁**（54次）：建议 `zoxide` / `autojump` 提升导航效率（已有 `j` 命令痕迹）