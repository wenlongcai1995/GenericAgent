# R34 工具集成探测: claude-code CLI (v2.1.70)

**时间**: 2026-04-30 00:30
**类型**: 工具能力探测
**对应**: TODO-F
**状态**: ⚠️ 已安装但未登录

---

## 🏗️ 安装状态
- **可执行**: `/opt/homebrew/bin/claude`
- **版本**: 2.1.70 (npm: @anthropic-ai/claude-code)
- **目录**: `~/.claude/` (backups/cache/debug/plugins/projects)
- **登录状态**: ❌ Not logged in

---

## 🧩 能力清单

### 核心能力
| 能力 | CLI参数 | 可用性 |
|------|---------|--------|
| 交互式会话 | `claude <prompt>` | ❌ 需登录 |
| 非交互输出 | `-p/--print <prompt>` | ❌ 需登录 |
| 结构化输出 | `--output-format json | stream-json` | ✅ API设计就绪 |
| JSON Schema验证 | `--json-schema <schema>` | ✅ API设计就绪 |
| MCP服务器管理 | `claude mcp add ...` | ✅ 本地可用 |
| 自定义Agent | `--agents <json>` | ✅ API设计就绪 |
| 自定义系统提示 | `--append-system-prompt` | ✅ API设计就绪 |
| 模型选择 | `--model sonnet|opus` | ✅ API设计就绪 |
| 会话恢复 | `-c/--continue, --resume` | ✅ 本地可用 |

### MCP服务器支持
```
claude mcp add --transport http <name> <url>
claude mcp add -e API_KEY=xxx <name> -- npx <mcp-server>
```

---

## 🔗 与GenericAgent集成可行性

### 方案A: subagent模式 (推荐)
```python
# 通过ANTHROPIC_API_KEY环境变量鉴权
import subprocess
result = subprocess.run(
    ["claude", "-p", prompt, "--output-format", "json"],
    env={"ANTHROPIC_API_KEY": "sk-..."},
    capture_output=True, text=True
)
```

### 方案B: MCP服务模式
- Claude Code 可作为 MCP 客户端消费 GenericAgent 的 MCP 服务
- 也可将GenericAgent作为MCP服务器暴露给Claude Code

### 前置条件
1. 执行 `claude /login` 或设置 `ANTHROPIC_API_KEY` 环境变量
2. 测试环境使用 `--dangerously-skip-permissions`

---

## 📋 小结
Claude Code v2.1.70 功能完整且与现代AI工具链深度集成(MCP/JSON Schema/Structured Output)，但**需要用户先登录**后才能作为子智能体集成。建议用户评估后开启登录 + 配置API Key。
