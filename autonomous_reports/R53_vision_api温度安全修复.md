# R53 - vision_api温度参数修复

## 背景
`_call_ollama` 的 `options` 字典缺少 `temperature` 参数，Ollama 默认为 temperature=0 → Qwen3-VL 可能返回空回复或截断。

## 修复
**文件**: `memory/vision_api.py` 第123行
**变更**: `'options': {'num_predict': 1024}` → `'options': {'num_predict': 1024, 'temperature': 0.7}`

温度0.7在保持创造力的同时避免随机发散，与OpenAI/Claude默认值对齐。

## 验证
- Ollama v0.17.7 + qwen3-vl:8b (6.1GB) ✅
- 测试图片(200×100, "Hello Vision!") → 返回 "The image shows a rectangular box..." ✅
- 结果非空、无Error前缀 ✅

## 影响范围
仅影响 ollama 后端（`_call_ollama`），其他3个后端不变。后续如需可暴露 `temperature` 参数到 `ask_vision()` 接口。