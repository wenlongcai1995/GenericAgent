# R19: 真实UI窗口截取+OCR+Vision分析管道打通

**日期**: 2026-04-25 | **类型**: 能力树扩展 | **优先级**: [9/10]

## 背景
macOS 15 (Sequoia) 环境下打通「Quartz窗口枚举 → 区域截图 → OCR文字提取 → Vision视觉分析」全链路。

## 核心组件状态

| 组件 | 文件 | 状态 | 备注 |
|------|------|------|------|
| 窗口枚举 | `screen_capture_pipeline.py --list-apps` | ✅ | Quartz API列出21个app窗口，物理坐标精确 |
| 窗口截图 | `screen_capture_pipeline.py --app` | ✅ | 全屏+PIL crop绕过macOS 15 `screencapture -R`损坏 |
| OCR提取 | `ocr_utils.ocr_image()` | ✅ | Cursor菜单栏识别出"Edit/Python/View" (16字符) |
| Vision分析 | `vision_api.ask_vision()` | ✅ | ollama qwen3-vl:8b 回复正常，描述桌面壁纸"雪山景观" |

## 关键发现

1. **macOS 15 截图坑已踩平**: `screencapture -R`完全损坏→`_grab_region()`做全屏+PIL crop 已验证通过
2. **覆盖窗口捕获是特性**: Quartz枚举所有窗口(含被覆盖的)，截图捕获的是该坐标处*实际可见*内容。`--app`截到的是视觉层叠顺序中该位置的内容，不一定是目标窗口
3. **OCR中文可能不完整**: 合成图片中文"测试中文"漏识别，真实英文UI文字识别正常。需指定`lang='chi_sim+eng'`
4. **Vision自动缩放**: 3840×2160→1600×900 (base64 347KB)，响应约30s
5. **OCR vs Vision互补**: OCR快(2s)但有限；Vision慢(30s)但能理解场景。应优先OCR，不足再用Vision

## 管道调用示例

```bash
# 一键：枚举→截图→OCR
python screen_capture_pipeline.py --app "Cursor"

# 截图→Vision分析
python -c "from vision_api import ask_vision; print(ask_vision('/tmp/test.png'))"
```

## 记忆更新建议
- L1 `global_mem_insight.txt` 已包含 `macOS用temp/screen_capture_pipeline.py(区域截图+OCR+Vision)` ✅
- L3 `vision_sop.md` 已补充macOS 15 `screencapture -R`损坏说明 ✅
- 无新的L2/L3需要追加

## 下一步建议
1. 用 `ljqCtrl_sop` 激活特定窗口到前台后再截图解决覆盖问题
2. 测试更小模型加速Vision（如qwen3-vl:4b）
3. 探索OCR中文识别准确率（`chi_sim`语言包是否下载完整）