# R25 | 自动化memory索引维护工具 | 2026-04-29

## 概述
创建 `memory/memory_index_updater.py`，自动扫描 memory/ 目录下 .md/.py SOP 文件变更，同步更新 L1(global_mem_insight.txt) 的 L3 索引行。

## 动机
L1 的 L3 索引此前纯手动维护 → 新增/删除 SOP 文件时易遗漏。

## 方案
- 扫描 memory/ 下所有 .md/.py 文件（排除全局文件/缓存/目录）
- 与当前 L1 的 L3 行逐项 diff
- `--apply` 参数安全替换 L3 行，保留其他内容
- 内建 KNOWN_DESCRIPTIONS 映射表自动补描述
- 幂等设计：无变更时跳过写入

## 执行结果
- [x] 脚本创建 + 测试
- [x] 首次 apply：L3 从 19 项 → 25 项
- [x] 幂等验证通过
- [x] 修复续行格式解析 bug
- [x] Git 提交

## 变更文件
| 文件 | 操作 |
|------|------|
| memory/memory_index_updater.py | 新建 |
| memory/global_mem_insight.txt | 更新 L3 行 |
