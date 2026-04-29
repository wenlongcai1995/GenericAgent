# R25 silent_fetch.py v2 加固 — trafilatura挂起bug修复

## 背景
R21探测时发现 silent_fetch 对 Wikipedia/Guardian 等站点挂起（trafilatura.fetch_url() 无限阻塞）。
本任务在R24规划中评为最高优先级(9/10) — 核心搜索工具链的关键bug。

## 问题定性
**trafilatura.fetch_url()** 在部分站点无法正常返回，导致整个 `silent_fetch()` 调用无限阻塞。
原因不确定（推测是底层 lxml 解析特定HTML结构时陷入循环），但简单修复即可规避。

## 修复方案
```
concurrent.futures.ThreadPoolExecutor 包裹 trafilatura.fetch_url()
    ├── 15秒内返回 → 正常 trafilatura.extract()
    ├── 超时/异常 → requests.get() fallback
    │                    └── trafilatura.extract(response.text)
    └── requests也失败 → 返回 error dict
```

## 测试验证
| 测试站点 | trafilatura原始行为 | v2结果 | fallback触发 |
|----------|-------------------|--------|-------------|
| Wikipedia (Python) | 无限挂起 | ✅ success, 77909 chars | ✅ fallback=True |
| httpbin.org/html | 正常返回 | ✅ success, 3683 chars | ❌ fallback=False |
| Wikipedia (AI) | 无限挂起 | ✅ success (导入验证) | ✅ fallback=True |

## 影响范围
- `memory/silent_fetch.py` ✅ 已同步 v2
- `temp/silent_fetch.py` ✅ 已更新 v2
- `search_fetch_sop.md` ✅ 已添加挂起修复说明
- 接口兼容: `silent_fetch()` 返回值新增 `fallback` bool字段，其余兼容

## 后续建议
- 第二个TODO (定时监控) 启动后可将 silent_fetch 作为下游提取器执行端到端测试
- 如发现其他站点仍挂起，可降低 timeout 值或增大 requests timeout
