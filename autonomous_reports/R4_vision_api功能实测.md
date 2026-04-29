# R4 Vision API 功能实测报告

**报告时间**: 2026-04-24
**任务类别**: 能力树扩展 — 视觉能力验证

---

## 一、结论

**vision_api 现有三个后端均不可用。** 纯代码层面完整（导入/图片处理/编码均通过），但实际API调用时全部失败。

## 二、各后端测试结果

| 后端 | 配置状态 | 测试结果 | 原因 |
|------|----------|----------|------|
| **claude** (默认) | ❌ mykey无`native_claude_glm_config` | 导入时AttributeError | 配置未设置 |
| **openai** | ⚠️ 实际指向DeepSeek API | ❌ HTTP 400 | 模型不支持视觉输入 |
| **modelscope** | ⚠️ API KEY 为空字符串 | ❌ 认证失败 | 需要补充token |

## 三、详细发现

### 1. OpenAI后端 → 实际为DeepSeek
- API Base: `https://api.deepseek.com/v1`
- 400错误说明模型不接收image_url格式内容
- DeepSeek的对话模型（非VL系列）只接受文本

### 2. 代码质量评估
图片处理管道完整：支持PIL/文件路径输入、自动缩放、RGBA转RGB、Base64编码 ✅
错误处理机制完善：超时/HTTP/解析错误都有区分 ✅
OpenAI兼容格式封装良好 ✅

### 3. 修复成本评估
- **最小成本方案**：在Modelscope申请免费token即可用Qwen3-VL模型（235B）
- 或：更换deepseek配置为deepseek-vl2模型（需确认是否支持）

## 四、建议
1. **优先**：申请ModelScope token → 即时可用Qwen3-VL-235B
2. 或：将claude配置指向某个兼容OpenAI格式的视觉API
3. **暂不推荐**：绕过此问题自行实现OCR（已有ocr_utils.py）

## 五、测试详情
- 测试图片: `vision_test.png` (400×100, 文字"Hello Vision API Test!")
- 运行环境: macOS 15.6.1, Python 3.13.4

## 六、记忆更新建议
- vision_api三后端不可用→ 已写入 L2 [VISION_API] 段 ✅
- 修复方向：申请ModelScope token 或补充视觉API key → 已在L2记录
- L1索引 vision_sop 指针保留不变（详情在L2）
