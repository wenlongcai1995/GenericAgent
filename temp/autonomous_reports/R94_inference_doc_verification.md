# R94: inference.py L2文档验证报告

## 执行概要
验证 `memory/inference.py` 实际导出接口 vs L2(global_mem.txt) 文档一致性。

## 验证结果
`inference` 是 `_Inference` 类实例（非模块级函数），L2文档基本准确。

### 实际API (9项)
| Method/Property | 实际签名 | L2描述 | 一致? |
|---|---|---|---|
| `.text(prompt, **kwargs)` | `(prompt, **kwargs)` | `(prompt, system, temperature, max_tokens)` | ✅ 可接受 |
| `.vision(image_input, prompt, **kwargs)` | `(image_input, prompt='详细描述...')` | `(prompt, image, ...)` | ⚠️ 参数顺序不同 |
| `.capture_app(app_name, do_ocr, vision_prompt, ...)` | `(app_name, do_ocr=True, vision_prompt=None, enhance=False, activate_first=True, log_to_file=True)` | `(app_name, do_ocr, vision_prompt)` | ⚠️ 缺enhance/activate_first/log_to_file |
| `.classify(text, categories)` | `(text, categories: list[str])` | `(text, categories)` | ✅ |
| `.summarize(text, max_length)` | `(text, max_length=100)` | `(text, max_length)` | ✅ |
| `.structured(prompt, **kwargs)` | `(prompt, **kwargs)` | `(prompt, output_schema, system)` | ✅ 可接受 |
| `.status` | property | `status()` | ⚠️ 是property非方法 |
| `.ollama_available` | property | 同上 | ✅ |
| `.vision_available` | property | 同上 | ✅ |

### 结论
L2文档可作为快速参考使用，无需紧急修正。
- `capture_app` 也暴露在 `screen_capture_pipeline.py`（更低层）
- `**kwargs` 模式使精确签名有弹性

## 后续建议
- 可考虑为inference.py创建SOP文档（memory/inference_sop.md）
- 清理temp/中已晋升的冗余副本（已确认MD5相同）
