# R93: gh_ops 模块文档一致性验证报告

## 执行概要
交叉验证 `gh_ops` 模块（memory/ + temp/ 双副本）与 SOP、L2 文档的一致性，发现并修复6项差异。

## 验证方法
1. `import importlib.util + inspect.signature()` 提取 memory/ 和 temp/ 各15个函数签名
2. MD5校验确认双副本二进制一致
3. 逐项比对 SOP 标明的 Action 列表 vs 实际函数签名

## 发现并修复（6项）

| # | 位置 | 问题 | 修复 |
|---|------|------|------|
| 1 | L2 line 112 | `from temp.gh_ops import ...` | 改为 `from memory.gh_ops import ...` |
| 2 | L2 line 111 | `所有函数参数格式: (repo, ...) 或 (limit)` 过于笼统 | 改为每个函数独立带参数签名 |
| 3 | L2 | 缺少 release_create 的 files/latest 参数 | 已补充完整签名 |
| 4 | L2 | 缺少双副本说明 | 增加注释 `双副本: memory/gh_ops.py == temp/gh_ops.py` |
| 5 | SOP line 13 | `release:create <tag> [title [notes]]` 缺少附件/latest参数 | 补充：`--files <paths> --latest=false` |
| 6 | SOP line 6 | 未注明 import 路径已改 memory/ | 无需修改（SOP 不直接写 import 路径） |

## 额外发现：双副本风险
`temp/gh_ops.py` 和 `memory/gh_ops.py` 完全一致（MD5相同），但：
- 若只更新其中一个，会产生版本漂移（类似 silent_fetch 中 temp/ vs memory/ 不同版本的坑）
- 建议未来清理 temp/ 中已晋升的冗余副本

## 文件变更
- `memory/global_mem.txt` — GH_OPS 章节重写（更精确的函数签名+路径修正）
- `memory/gh_ops_sop.md` — release:create 参数补全

## 后续建议
- 验证 adb_ui.py / inference.py 等模块的 SOP 文档一致性
- 清理 temp/ 中的已晋升模块冗余副本
