# R95: temp/ ↔ memory/ 模块同步报告

## 发现
memory/ 与 temp/ 有5个同名.py模块，其中 **silent_fetch.py 版本漂移**：

| 模块 | memory/ | temp/ | 状态 |
|------|---------|-------|------|
| auto_proxy_switch.py | 13593B | 13593B | ✅ 一致 |
| gh_ops.py | 6138B | 6138B | ✅ 一致 |
| proxy_api_control.py | 9151B | 9151B | ✅ 一致 |
| silent_fetch.py | 7314B | 5638B | ❌ 不同→已同步 |
| silent_search.py | 4091B | 4091B | ✅ 一致 |

## silent_fetch.py 差异分析
- memory/ 版本更新（214行，约+40行）
- 新增 `_generate_summary()` 辅助函数
- `silent_fetch()` 新增 `summarize=False` 和 `max_summary_length=150` 可选参数
- 返回dict新增 `summary` 字段
- 兼容性：✅ 新版是旧版严格超集（所有旧参数在新版中保留）

## 已执行
- `cp memory/silent_fetch.py → temp/silent_fetch.py`
- 同步后MD5一致

## 结论
temp/ 是历史遗留的晋升前副本，差异为 memory/ 获得新功能后未同步 temp/。
建议在memory_cleanup_sop中增加清理机制，或移除temp/中已晋升的模块。
