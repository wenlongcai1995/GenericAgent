# R7 TCM 项目预研就绪（等待用户确认启动）

## 日期
2026-04-29，用户离线期间完成

## 核心产出

### 1. 代码探索
- **目录**: `~/work/tcm/tcm_mvp_ts_exec_v2/`
- **源码**: 11 个 C 文件（case_table/manager/worker/hw/retention/pattern/platform/logger/suite_menu/shared_ctrl）
- **架构**: Manager-Worker 模式 + shared_ctrl 双 TCM 映射 + 1 字 retention
- **风险**: macOS 无 GNU ld（V2 收尾受限）、retention 仅 1 字、无日志输出靠 exit code

### 2. 测试用例全景（97条）
| Suite | 条数 | 级别 | 依赖 |
|-------|:----:|:----:|:----:|
| TS005 | 16 | E0 | 无（Phase 1-2 先行）|
| TS006-007 | 12 | E1 | 依赖 multi-pair |
| TS010-013 | 57 | E1 | 依赖 multi-pair |
| TS008-009,014 | 12 | E2 | 依赖全部 E1 |

### 3. ARM GCC 依赖消除
- **发现**: Phase 1-3 均为 Host 模式（macOS 原生 cc），**不需要 ARM GCC**
- **ARM GCC 安装**: `brew install arm-none-eabi-gcc`（Phase 4.3 时 2min 搞定）
- **计划已更新**: `plan.md` 中修正了 Step 1.2 的依赖说明

### 4. 记忆维护
- L1 审计完成（32 行，质量良好，无修改必要）

## 待用户决策
1. 确认启动 Phase 1（E0 16 条 single-pair 用例）
2. 用户说"开始"即可零延迟启动