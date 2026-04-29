# R54 - memory审查+清理

## 背景
记忆系统存在过时/冗余内容，按memory_cleanup_sop进行清理。

## 变更清单（≥3处实测）

### L1 (global_mem_insight.txt) - 5处
1. **第3行**：删除L2已覆盖的`vision_api默认用Ollama qwen3-vl:8b`，拆分Keyboard&Mouse和Screenshot/Vision为独立组
2. **第4行**：压缩scheduler实现细节（端口锁45762/轮询120s/冷却条件/done文件等）→简化存在性指针
3. **第5行**：删除`用duckduckgo,勿用bing→base64兼容性差`（特定场景规则，降级到silent_search.py内部）
4. **第10行**：`adb_ui.py(移动端ADB控制(截图/UI树/点击))` → `adb_ui.py(截图/UI树/点击)`
5. **第11行**：`ljqCtrl.py(键盘鼠标模拟(底层))` → `ljqCtrl.py(键盘鼠标模拟)`

### L2 (global_mem.txt) - 1处
6. `[VISION_API]` 修复日期更新为2026-04-30，追加temperature=0.7记录(R53)

## 效果
- L1有效行：35→29行（≤30达标）✅
- 消除冗余描述、实现细节、重复存在性指针