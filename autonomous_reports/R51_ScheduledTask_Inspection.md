# R51: 6个定时任务首轮产出质量巡检报告

> 执行日期：2026-04-30 | P1 产出 | 逐任务检查done内容质量、依赖脚本完好性

## 概述

对 `sche_tasks/` 下 **6个JSON任务 + 4个done报告** 进行全面巡检，覆盖：JSON格式校验、依赖脚本完好性、产出质量审查、调度链路健康度。

---

## 一、Task独立性诊断

| # | 任务名 | 调度时间 | 依赖脚本 | 产出状态 |
|---|--------|---------|---------|---------|
| 1 | daily_ai_monitor | 08:00 daily | silent_search | ⚠️ 上次产出4/25（5天前） |
| 2 | daily_cvpr2026_monitor | 07:00 daily | silent_search + silent_fetch | ❌ 从未产出 |
| 3 | daily_github_monitor | 09:00 daily | silent_search.py | ❌ 从未产出 |
| 4 | daily_slam_3dv_monitor | 07:30 daily | silent_search + silent_fetch | ❌ 从未产出 |
| 5 | llm_apple_monitor | 08:00 daily | silent_search | ❌ 从未产出 |
| 6 | stock_monitor_603501 | 15:30 daily | monitor_603501.py + silent_search.py | ❌ 从未产出 |

## 二、依赖脚本完好性

| 脚本 | 路径 | 大小 | 语法检查 |
|------|------|------|---------|
| silent_search.py | memory/silent_search.py | 4091 bytes | ✅ 通过 |
| silent_fetch.py | memory/silent_fetch.py | 5638 bytes | ✅ 通过 |
| monitor_603501.py | temp/monitor_603501.py | 3576 bytes | ✅ 通过 |

**所有依赖脚本均语法正常**，单个可用性已通过R50/P0验证。

## 三、JSON配置质量

| 任务 | enabled | schedule | repeat | max_delay_hours | prompt质量 |
|------|---------|----------|--------|-----------------|-----------|
| daily_ai_monitor | ✅ true | 08:00 | daily | 6h | ✅ 简洁明确，搜索策略清晰 |
| daily_cvpr2026_monitor | ✅ true | 07:00 | daily | 10h | ✅ 最详细，含产出格式模板 + arXiv提取要求 |
| daily_github_monitor | ✅ true | 09:00 | daily | 8h | ✅ 搜索关键词明确，含star数/热度分析要求 |
| daily_slam_3dv_monitor | ✅ true | 07:30 | daily | 10h | ✅ 策略精细，含DDG fallback + arXiv提取 |
| llm_apple_monitor | ✅ true | 08:00 | daily | 10h | ⚠️ 路径写死（见下文） |
| stock_monitor_603501 | ✅ true | 15:30 | daily | 6h | ✅ 含预警阈值（95/115/7%）|

**llm_apple_monitor路径问题**：prompt中写死了 `输出到 autonomous_reports/LLM_Monitor_YYYY-MM-DD.md`，但scheduler机制是自动注入`[报告路径]`（`sche_tasks/done/YYYY-MM-DD_任务名.md`）。两者冲突，agent会优先使用哪个注入路径？如果不一致可能导致报告写入错误位置。

## 四、done/产出质量审查

### 产出 #1: daily_ai_monitor (2026-04-25)

**评分：6/10** — 仅有搜索列表无深度内容

- ✅ 格式标准、来源清晰
- ✅ 搜索关键词覆盖合理
- ❌ 仅有Bing搜索结果列表（标题+来源），**缺少silent_fetch提取正文**
- ❌ 未提炼"3条今日AI趋势"（prompt明确要求）
- ❌ 搜索质量：部分结果不相关（"Valve Steam Machine"出现在AI搜索中）

**根因**：dry-run阶段的**demo原型**，当时silent_fetch还未整合到搜索流中

### 产出 #2-4: test_scheduler相关 (2026-04-29/30)

**评分：8/10** — 链路验证充分

- ✅ 完整记录了触发条件检查（time_ok/within_window/cooldown_ok）
- ✅ 执行了silent_search并正确提取结果
- ✅ 含测试结论和后续建议
- ✅ 端到端链路全部通过
- ⚠️ test任务的产出不是日常监控内容

## 五、根因分析：为什么5/6任务从未产出

**单一根因：scheduler后台守护进程未启动**

```
├─ 需要: python agentmain.py --reflect reflect/scheduler.py --bg
├─ 现状: 无相关进程
├─ 证据: scheduler.log仅1行（手动测试时写入）
└─ 影响: 所有6个定时任务均无法自动触发
```

依赖脚本（silent_search/silent_fetch/monitor_603501）全部完好，**链路已在R49验证通过**。缺的只是常驻进程。

## 六、分级修复建议

### P0（立即修复）
1. **启动scheduler守护进程** — 这是唯一的堵点
   ```bash
   cd /Users/raymond/program/GenericAgent
   python3 agentmain.py --reflect reflect/scheduler.py --bg
   ```
   需验证进程存活、验证端口锁（45762）、检查日志写入

### P1（建议修复）
2. **llm_apple_monitor.json 路径修正** — 删除prompt中的硬编码路径，让scheduler注入路径
3. **所有任务的done/目录首次预热** — 手动触发一次完成所有任务的首轮产出，积累基准数据

### P2（后续优化）
4. **daily_ai_monitor prompt升级** — 增加silent_fetch步骤，提升深度（参考cvpr2026的详细prompt模板）
5. **基于时间窗口的进度告警** — 如果某个任务连续N天无产出，alert（如：stock_monitor应在15:30后有产出，每天检查）

## 七、行动指导

1. **用户审批后启动scheduler后台进程**（需用户确认，因为涉及长期进程）
2. **手动预热**：可以主动执行一次所有6个任务产生首轮产出（不需要等scheduler），耗时约10-15分钟
3. **下次执行优先级**：若用户同意，本agent可立即启动预热执行

---

### 数据来源
- `sche_tasks/*.json` — 6个任务定义文件
- `sche_tasks/done/*.md` — 4个产出文件
- `sche_tasks/scheduler.log` — 1行日志
- 依赖脚本语法检查：`python3 -c "import py_compile; py_compile.compile(...)"`
- 目录遍历：`code_run` + `os.walk`