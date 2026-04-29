# R77: macOS代理快捷切换 — 一键开关系统代理

> 赛季: 2026-04 | 环境: macOS 14+ | Clash Verge Rev (port 7897) | Shortcuts CLI 可用

## 核心产出

为用户提供 **一键切换系统代理** 的能力，无需打开Clash/终端，支持多种触发方式：

### 交付物清单

| # | 交付物 | 路径 | 状态 |
|---|--------|------|------|
| 1 | **Shell脚本** | `temp/toggle_proxy.sh` | ✅ 测试通过 |
| 2 | **Automator Quick Action** | `~/Library/Services/Toggle Proxy.workflow` | ✅ 已创建 |
| 3 | **Shortcuts集成指南** | 见下方 | ✅ 文档化 |
| 4 | **键盘快捷键绑定指南** | 见下方 | ✅ 文档化 |

### 脚本核心逻辑

```bash
# 用法：
./toggle_proxy.sh         # 切换（开↔关）
./toggle_proxy.sh on      # 强制开
./toggle_proxy.sh off     # 强制关
./toggle_proxy.sh status  # 查看状态
```

通过 `networksetup` 控制 Wi-Fi 接口的 HTTP/HTTPS/SOCKS 代理，三键同步开/关。

## 环境探测发现

### 代理现状

| 项目 | 值 |
|------|-----|
| 代理服务器 | **Clash Verge Rev** (PID 32990, `verge-mih`进程) |
| 代理端口 | 127.0.0.1:7897 (HTTP/HTTPS/SOCKS统一) |
| 系统代理 | 当前 **开启** |
| 其他代理 | 无ClashX/Surge/V2rayU等 |

### macOS Shortcuts CLI 能力评估

| 能力 | 可用性 |
|------|--------|
| `shortcuts run` 运行已有Shortcut | ✅ |
| `shortcuts list` 列出Shortcuts | ✅ |
| `shortcuts view` 查看Shortcut | ✅ |
| `shortcuts sign` 签名Shortcut文件 | ✅ |
| **`shortcuts create` 创建新Shortcut** | ❌ **不支持命令行创建** |
| **AppleScript访问Shortcuts** | ❌ 超时/不可用 |
| **Shortcuts数据库文件** | ❌ 库为空（Shortcuts未初始化？） |

### Shortcuts CLI 核心限制

> **无法通过CLI或代码创建Shortcut** — `shortcuts` 仅支持运行/查看/签名已有Shortcut，不支持创建。

## 方案设计

由于Shortcuts无法程序化创建，采用 **分级方案**：

### 方案A: Shell脚本（核心，已实现 ✅）
- `temp/toggle_proxy.sh` — 支持status/on/off/toggle四种模式
- 可直接在Terminal中运行
- 完整错误处理

### 方案B: Automator Quick Action（已实现 ✅）
- `~/Library/Services/Toggle Proxy.workflow` — macOS服务
- 可在任意应用中通过菜单或键盘快捷键触发

### 方案C: 通过Shortcuts App手动创建（指南）
若用户想集成到Shortcuts：
1. 打开 **Shortcuts** App
2. 点 `+` 创建新Shortcut
3. 搜索添加 `Run Shell Script` action
4. 填入: `bash ~/program/GenericAgent/temp/toggle_proxy.sh`
5. 保存为 "Toggle Proxy"

### 方案D: 绑定键盘快捷键
1. 系统设置 → 键盘 → 键盘快捷键 → 服务 → 勾选 "Toggle Proxy"
2. 双击设置快捷键（如 `⌃⌥P`）
3. 任意应用中使用快捷键切换代理

## 实际测试结果

```
$ ./toggle_proxy.sh status
📊 代理状态: on
Enabled: Yes → Server: 127.0.0.1 → Port: 7897

$ ./toggle_proxy.sh off
🚫 关闭系统代理 → ✅

$ ./toggle_proxy.sh on  
🌐 开启系统代理 → 127.0.0.1:7897 → ✅
```

## 记忆更新建议

**无需更新L1/L2** — 此工具为临时工具脚本，位于 `temp/` 目录，不属于核心能力记忆。若用户长期使用并希望保留，可考虑：
1. 将脚本移到 `~/bin/` 并加入PATH
2. 添加到L2作为一个快捷入口提示

## R77完成状态

- [x] 环境探测 (代理状态/Shortcuts CLI/网络服务)
- [x] Shell脚本实现并测试
- [x] Automator Quick Action创建
- [x] 集成指南文档化
- [x] 报告输出
