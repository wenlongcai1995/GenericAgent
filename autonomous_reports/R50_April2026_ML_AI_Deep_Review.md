# R50: 2026年4月ML/AI深度回顾报告
> 赛季背景：2026年4月 · 第11期自主行动 · P0 产出

## 概述

2026年4月是AI史上最具戏剧性转折的一个月——不是某个单一模型主导，而是**格局重置**：OpenAI-Microsoft联盟重构、Anthropic转型基础设施平台、开源模型能力追上闭源、政府干预从「讨论」变为「行动」。本报告基于4个独立信源的正文提取，提炼出3个深度洞察。

---

## 洞察一：OpenAI-Microsoft联盟重构——AI商业格局的「柏林墙倒塌」

### 发生了什么
2026年4月27日，OpenAI与Microsoft宣布了自2023年以来最重要的合作关系重置 (aicritique.org)。核心变化：
- **Azure不再独占**OpenAI产品的分发权
- **Microsoft保留**2032年前OpenAI IP的非独占许可 + 20%收入抽成（有上限） 
- **OpenAI获得自由**：可以在AWS、Google Cloud等多云分发

### 为什么重要
次日（4月28日）OpenAI立即将GPT-5.5、Codex和Bedrock Managed Agents带到AWS (aicritique.org)。更惊人的商业细节流出：
- **Amazon向OpenAI投资$500亿**
- **OpenAI承诺8年内在AWS上消费$1000亿**，使用2GW Trainium算力

这意味着**AI基础设施已变成多云公用事业**，不再由单一云厂商垄断 (aicritique.org)。

### 数据溯源
| 事实 | 来源 |
|------|------|
| OpenAI-Microsoft | aicritique.org「AI Developments April 2026」(Apr 29) |
| AWS投资细节 | aicritique.org + Reuters via aicritique.org |
| 微软20%抽成 | Reuters via aicritique.org |
| GPT-5.5性能 | kersai.com「AI in April 2026」(Apr 16) — GDPval 83% |

---

## 洞察二：Claude Mythos 5——「太强所以不发布」的10万亿参数里程碑

### 发生了什么
Anthropic在4月初确认了**Claude Mythos 5**的存在——**首个跨越10万亿参数阈值**的AI模型 (whatllm.org)，但以空前条件发布：
- **不公开提供**，不通过标准API
- 仅有**50家组织**通过Project Glasswing获得防御性安全访问
- 定价 $25/百万输入token, $125/百万输出token
- 触发了Anthropic内部 **ASL-4安全协议**（接近真实危险能力阈值）

### 为什么重要
这标志着AI行业出现**能力-访问裂谷**：
- 最强模型（10T参数量）被锁定在「安全防火墙」后
- 同一天，Zhipu AI以**MIT开源协议**发布了GLM-5.1（744B MoE），在SWE-Bench Pro上击败了GPT-5.4
- 成本对比：Claude Mythos $125/百万输出 vs GLM-5.1 **免费**

WhatLLM评论：「这不是基准竞赛或价格战，而是AI哲学的分裂——能力增长快于社会可接受的部署方式。」(whatllm.org, Apr 8)

### 数据溯源
| 事实 | 来源 |
|------|------|
| Claude Mythos 5 10T参数 MoE | whatllm.org (Apr 8) + kersai.com (Apr 16) |
| 活跃参数800B-1.2T | kersai.com |
| 训练数据15.5T tokens | kersai.com |
| 定价详情 | whatllm.org |
| ASL-4安全协议 | kersai.com |
| GLM-5.1 MIT开源击败GPT-5.4 | whatllm.org |

---

## 洞察三：开源AI的「中国时刻」——GLM-5全栈硬件独立 & 开源生态结构性超越

### 发生了什么
2026年4月开源AI生态发生结构性转变。digitalapplied.com (Apr 3) 指出三个关键变化：
1. **MoE成为默认架构**：5/6主流开源模型使用MoE，活跃参数5.1B-40B，**单GPU可运行**
2. **许可真正自由化**：Apache 2.0和MIT覆盖大多数开源模型，消除企业采用的法律模糊
3. **中国实验室在特定基准上领先**

最重磅的是 **GLM-5由Zhipu AI发布，完全在华为芯片上训练，零NVIDIA依赖** (digitalapplied.com)。这是硬件独立性的里程碑——在美国出口管制下，中国AI完成了从「廉价模型」到「主权技术栈」的转变。

### 开源模型全景（2026年4月）
| 模型 | 组织 | 总参数量 | 活跃参数 | 上下文 | 许可 |
|------|------|---------|---------|-------|------|
| GLM-5 | Zhipu AI | 744B | 40B | 200K | MIT |
| Llama 4 Maverick | Meta | 400B | 17B | 1M | Community |
| Mistral Small 4 | Mistral | 119B | 6.5B | 256K | Apache 2.0 |
| gpt-oss-120b | OpenAI | 117B | 5.1B | 128K | Apache 2.0 |
| Gemma 4 | Google | 31B→2B | dense/MoE | 128K-256K | Apache 2.0 |
| Qwen 3.6 Plus | Alibaba | TBD | TBD | 1M | Apache 2.0 |

### 为什么重要
- 开源与闭源的差距缩小到「很多生产负载中，开源是更好的默认选项」(digitalapplied.com)
- GLM-5的硬件独立验证了**中国AI供应链在出口管制下的韧性**
- Kersai (Apr 16) 补充：Q1 2026全球创业融资$297B，其中**AI占$242B（81%）**——资本仍在大规模涌入

### 数据源差异标注
- **aicritique.org (Apr 29) vs whatllm.org (Apr 8)**：前者对Claude Mythos的评价更积极（「momentum shift」），后者更批判（「won't ship its best」）
- **数字差异**：aicritique说$600B hyperscaler年支出，kersai说$297B Q1融资——两者口径不同（年度capex vs 季度venture），不矛盾

---

## 策略建议

1. **多云AI策略成为必需品**：OpenAI现在多平台分发，工具选型不应再绑定单一云（如Azure Exclusive）
2. **优先评估开源模型**：GLM-5（MIT）、Gemma 4（Apache 2.0）、Mistral Small 4的生产就绪度——对隐私敏感或成本敏感场景，开源已足够
3. **关注Huawei Ascend生态**：如果出口管制加强或NVIDIA供应受限，了解华为芯片的AI兼容性将成为战略能力
4. **Agentic AI动手评估**：GPT-5.5的agentic coding能力、Codex 4M周活用户——agent执行能力已从demo进入生产

## 记忆更新建议
- 将以下事实更新到global_mem：April 2026的关键事件（OpenAI-Microsoft reset, Claude Mythos 5, GLM-5独立硬件）
- 标注GLM-5作为国产AI硬件的里程碑
- AI行业格局已从「benchmark竞赛」转向「distribution + compute + control」竞争

---

### 数据来源
1. **aicritique.org** — "AI Developments in April 2026" (2026-04-29, by ChatGPT) — 最全面的大局分析，涵盖6大维度
2. **whatllm.org** — "New AI Models April 2026: Anthropic Won't Ship Its Best. Open Source Will." (2026-04-08, Dylan Bristot) — 聚焦开源vs闭源交锋
3. **kersai.com** — "AI in April 2026: Biggest Breakthroughs, Models & Industry Shifts" (2026-04-16) — 数据最详实，含融资/参数/基准
4. **digitalapplied.com** — "Open-Source AI Landscape April 2026: Complete Guide" (2026-04-03) — 结构化开源模型对比