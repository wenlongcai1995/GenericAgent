# silent_fetch 复杂页面提取测试报告

## 赛季背景
2026-04-29 | 能力树扩展 | 验证 silent_fetch (trafilatura) 对3种复杂页面类型的提取能力

## 测试方法
对3种内容类型各找到真实工作URL，通过 silent_fetch 提取正文，评估：
1. 提取完备度（字符量、关键内容保留）
2. 结构保留度（代码块、列表、章节）
3. 已知问题/局限性

---

## 1. 代码重页面 (Code-heavy)

| 项目 | 值 |
|------|-----|
| URL | realpython.com/async-io-python/ |
| 标题 | "Python's asyncio: A Hands-On Walkthrough – Real Python" |
| 作者 | Leodanis Pozo Ramos (Real Python) |
| 提取字符 | **45,518 chars** |
| 函数定义 | 45个 (def, async def) |
| async/await | async×111, await×40 |
| import/class | import×20, class×3, print×44 |

**定性**: ✅ 优秀。代码内容完整提取，函数定义全部保留。
**缺点**: trafilatura将代码块拉平为纯文本（无代码围栏标记），但语义结构完整可读。

---

## 2. 长文章 (Long-form Analysis)

| 项目 | 值 |
|------|-----|
| URL | aiworldjournal.com/the-state-of-ai-in-2026-a-comprehensive-report/ |
| 作者 | Sydney Armani |
| 日期 | 2026 |
| 提取字符 | **10,384 chars** |
| 章节数 | 13个（AI Maturity, Economic Impact, Workforce, Regulation等） |
| 预估阅读时间 | ~25 分钟 |

**定性**: ✅ 良好。长文内容完整，13个章节均已提取。
**⚠️ 关键问题**: 段落结构丢失。trafilatura将所有段落合并为**1个文本块**（10384字全部在一个段落中）。标题/分段标记消失。

---

## 3. 列表页 (List/Ranking)

| 项目 | 值 |
|------|-----|
| URL | index.dev/blog/popular-programming-language |
| 标题 | "20 Most Popular Programming Languages in 2026" |
| 提取字符 | **27,904 chars** |
| 编号项 | 27个（含概览列表+每个语言的详细分析） |

**定性**: ✅ 优秀。编号结构保留清晰，排名+描述完整可读。
前5结果: Python (Top1), C++, Java, JavaScript, SQL...——均为2026年时序数据，可做多源交叉验证。

---

## 已知问题汇总

### P1: trafilatura.fetch_url() 挂起/失败
| 站点 | 症状 | 根因推测 |
|------|------|----------|
| Wikipedia | 无限挂起（需timeout终止） | fetch_url底层连接池/重定向问题 |
| The Guardian | 超时 | 同上 |
| WIRED | 仅提取1676字（非全量） | 反爬检测或DOM结构复杂 |
| 正常站点 | ✅ 正常（realpython, aiworldjournal, index.dev等） |

**解决方案**: silent_fetch.py 应添加复合fallback机制：
```
trafilatura.fetch_url(url)  →  成功? 返回
    超时/失败?             →  requests.get(headers) → trafilatura.extract(html)
        也失败?             → 返回错误信息
```

### P2: 结构丢失
- 标题/段落标记全部拉平
- 代码格式丢失（但语义保留）
- 部分页面title/author/date metadata为空

### P3: 无法处理JS渲染
- SPA/动态加载内容不可见
- 推荐保留tmwebdriver SOP方案作为补充

---

## 策略建议

### 对 search_fetch_sop 组合流
- 自动搜索+提取的流程**基本可用**（10次中有8次成功提取）
- 使用 requests fallback 后预计可提升至95%+成功率
- 对于 Wikipedia/Guardian 等站点，可自动降级到 requests+extract

### 对 future autonomous tasks
- **代码页**: 适合API文档、教程抓取（45k+字符），但需额外处理代码格式
- **长文章**: 适合知识提取（文章总结、关键点提取），段落结构问题可通过LLM后处理修复
- **列表页**: 最适合自动提取（列表结构保留好），适合竞品对比/排名监控

---

## 数据来源差异标注
- 本报告所有数据来自实际工具执行结果，非模型知识推断
- realpython.com: 代码密集型，trafilatura提取优秀
- aiworldjournal.com: 长文型，段落结构丢失
- index.dev: 列表型，结构保留好
- 非所有站点均支持：Wikipedia/Guardian需fallback

---

## 记忆更新建议
1. **silent_fetch.py** → 添加 requests fallback（复合提取）
2. **search_fetch_sop.md** → 追加 trafilatura 局限性说明
