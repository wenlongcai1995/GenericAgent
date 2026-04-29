# R45 | 2026-04-30 | silent_search.py默认引擎修复 | P0 (8分)

## 问题

**SOP/L1记忆**：`勿用bing→base64兼容性差，用duckduckgo`
**代码**：`silent_search.py` 第73行默认 `engine="bing"`

两者冲突——记忆和SOP推荐duckduckgo，但代码默认用bing。

## 验证结果

| 引擎 | URL格式 | 是否直接URL | 下游可用性 |
|------|---------|:----------:|:---------:|
| Bing | `bing.com/ck/a?!&&p=...` (ck/a重定向) | ❌ | base64的`u=`参数在Python 3.13严格模式下decode抛异常 |
| DDG | `//duckduckgo.com/l/?uddg=<url编码>` | ❌ | `uddg`参数可提取，但偶发验证码(202) |

**两者都不能直接提供目标URL**，都需要URL提取步骤。Bing的base64问题在Python 3.13上是结构性失效，DDG的`uddg`提取已写好在search_fetch_sop.md中。

## 影响范围

- **0个外部调用依赖bing默认** — 所有显式传参都是代码自身docstring示例
- 唯一索引条目 `memory_index_updater.py:56` 只是描述性文字，无需修改

## 建议修改方案

### 1. memory/silent_search.py

```python
# 第73行: 默认 engine="bing" → engine="duckduckgo"
def silent_search(query: str, engine: str = "duckduckgo", top_k: int = 5) -> list:
```

配套更新：
- 模块docstring（行6-7）: `使用 DuckDuckGo HTML 版（首选）或 Bing（备选）`
- 函数docstring（行79）: `engine: "duckduckgo" (默认) 或 "bing" (已知Python 3.13上URL提取有问题)`
- CLI help（行101-110）: 默认引擎改为duckduckgo

### 2. memory/search_fetch_sop.md

无需修改，已正确推荐duckduckgo。

### 3. memory/global_mem_insight.txt

当前内容已正确（"用duckduckgo,勿用bing→base64兼容性差"），无需修改。

## 验收标准

- [ ] `silent_search()` 不传engine参数默认用DDG
- [ ] `silent_search(engine="bing")` 显式传参仍可用
- [ ] SOP和L1索引无需额外修改

## 风险

DDG偶发验证码(202)问题已存在，不是本次引入的。如DDG持续失败，用户可显式传 `engine="bing"` 或实现自动回退逻辑（未来优化）。

---

**状态**：待用户审查批准后执行修改
