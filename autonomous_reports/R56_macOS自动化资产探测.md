# R56 | 2026-04-30 | macOS自动化资产探测报告 | P0达成

## 版本/赛季背景
- 第13期规划P0任务，目标：盘点macOS Shortcuts/自动化资产，评估agent可编程调用可行性
- 时间：2026-04-30 凌晨自主执行

## 核心发现

### 1. Shortcuts 资产清单（12个）

| 名称 | ID | 可CLI调用 | 备注 |
|------|:--:|:---------:|------|
| 给六月加餐 | `4EF1CFEB-...` | ⚠️ 未知 | 加餐/喂食类 |
| 追加到备忘录 | `F08747FB-...` | ⚠️ 未知 | 备忘追加 |
| UU一键拔线 | `5E5C17CE-...` | ⚠️ 未知 | VPN/网络类 |
| Kindle传输 | `6E6C365F-...` | ⚠️ 未知 | 文件传输 |
| 快速提醒 | `3799D28D-...` | ❌ 缺少操作 | 创建时有依赖缺失 |
| EF | `FB25B8B4-...` | ⚠️ 超时 | 可能需交互 |
| 今日就绪状态 | `CAA66C39-...` | ⚠️ 未知 | 每日状态类 |
| 一键拔线 | `D600C038-...` | ⚠️ 未知 | 网络类（同功能） |
| 休息一下 | `9C7FE9DA-...` | ⚠️ 超时 | 提醒类 |
| 用信息发送最新照片 | `97BAA446-...` | ⚠️ 需交互 | iMessage依赖 |
| Shazam快捷指令 | `A998EFEC-...` | ⚠️ 未知 | 音乐识别 |
| 快捷指令是什么？ | `A6A35A5D-...` | ⚠️ 未知 | 内置教程 |

**存储位置**：`~/Library/Group Containers/group.is.workflow.shortcuts/`（4KB容器，非独立文件）

### 2. AppleScript / osascript 可行性

| 能力 | 状态 | 说明 |
|------|:----:|------|
| `display notification` | ✅ | Agent可推送系统通知 |
| `the clipboard` | ✅ | 可读取剪贴板内容 |
| `POSIX path of` | ✅ | 解析文件路径 |
| `system info` | ✅ | 获取系统版本信息 |
| `do shell script` | ✅ | 运行Shell命令（从AppleScript层） |
| `tell app "System Events"` | ❌ | 需辅助功能权限 |
| `tell app "Finder"` | ❌ | 需辅助功能权限 |
| `tell app "Shortcuts"` | ❌ | 需辅助功能权限 |

**定性**：osascript 受限使用，只能执行无需辅助功能权限的AppleScript。关键限制：无法自动化操控其他App窗口。

### 3. 本地开发工具

| 工具 | 版本/状态 | 用途评估 |
|------|:---------:|---------|
| Homebrew | 117 formulae | ffmpeg, node可用 |
| ollama | qwen3:8b + qwen3-vl:8b | 本地LLM + Vision |
| GA Scheduler | PID 91471 🟢 运行中 | 定时任务 |
| ShadowsocksX-NG | 运行中 | 网络代理 |
| clash-verge-rev | 运行中 | 网络代理 |

### 4. 自动化资源（空）

- Automator workflows: ❌（空）
- Services: ❌（空）
- AppleScript独立脚本: ❌（~/Library/Scripts/ 无个性化脚本）

## 策略建议

### 对 Agent 可行路径
1. **`shortcuts run <name>`** — 如果Shortcut设计为无交互，可直接触发（测试中2个超时/失败，需要用户筛选可运行的）
2. **`osascript -e 'display notification'** — 稳定的通知推送，建议集成到agentmain的异常/完成通知
3. **`osascript -e 'do shell script'`** — 可执行任意shell命令，但走AppleScript层无额外优势，直接subprocess更优

### 不可行路径
1. ❌ 通过osascript控制Shortcuts.app窗口（无辅助功能权限）
2. ❌ 自动化Finder操作（同需权限）
3. ❌ 通过Automator调用（无workflow）

### 扩展建议
1. 创建 **GA专用Shortcut**（无交互型），如"GA通知测试"、"GA文件上传"等，通过`shortcuts run`触发
2. 将 `display notification` 集成到GA错误处理流程作为用户通知渠道

## 记忆更新建议
- 无需更新L1/L2全局记忆（Shortcuts信息偏个人环境配置，非全局能力）
- 如需后续深度整合，建议建一个 `~/Library/Shortcuts/GA_*` 无交互shortcuts

## P0完成状态
✅ macOS Shortcuts/自动化资产探测 → **已完成**（12个shortcuts清单+osascript能力矩阵+调用可行性评估）