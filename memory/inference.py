"""
inference.py - 统一推理接口

统一入口，一个import搞定所有推理：
  from memory.inference import inference
  inference.text("...")      # 文本推理
  inference.vision(img)      # 图像推理
  inference.structured(...)  # 结构化输出
  inference.classify(...)    # 分类
  inference.summarize(...)   # 摘要

自动检测ollama可用性，fallback机制。
向后兼容：llm_client.py / vision_api.py 仍可单独import。
"""

import sys, os
import requests
from typing import Optional

_DIR = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_DIR)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from memory import llm_client
from memory import vision_api
from memory import ocr_utils

# ============ Ollama 可用性检测 ============

OLLAMA_BASE = 'http://localhost:11434'
_ollama_status = None  # 缓存检测结果

def check_ollama() -> dict:
    """检测ollama是否运行及可用模型。结果会被缓存。"""
    global _ollama_status
    if _ollama_status is not None:
        return _ollama_status
    try:
        r = requests.get(f'{OLLAMA_BASE}/api/tags', timeout=3)
        if r.status_code == 200:
            models = [m["name"] for m in r.json().get("models", [])]
            _ollama_status = {
                "running": True,
                "models": models,
                "has_text": any("qwen3" in m for m in models),
                "has_vision": any("vl" in m for m in models),
            }
        else:
            _ollama_status = {"running": False, "models": [], "has_text": False, "has_vision": False}
    except (requests.ConnectionError, requests.Timeout):
        _ollama_status = {"running": False, "models": [], "has_text": False, "has_vision": False}
    return _ollama_status


class _Inference:
    """统一推理入口。单例，全局使用 inference 实例。"""

    @property
    def status(self) -> dict:
        return check_ollama()

    @property
    def ollama_available(self) -> bool:
        return check_ollama()["running"]

    @property
    def vision_available(self) -> bool:
        return check_ollama()["has_vision"]

    def text(self, prompt: str, **kwargs) -> str:
        """文本推理（统一入口）"""
        return llm_client.ask_llm(prompt, **kwargs)

    def structured(self, prompt: str, **kwargs) -> dict:
        """结构化输出推理"""
        return llm_client.ask_llm_structured(prompt, **kwargs)

    def classify(self, text: str, categories: list[str]) -> dict:
        """文本分类快捷方式"""
        return llm_client.classify(text, categories)

    def summarize(self, text: str, max_length: int = 100) -> str:
        """文本摘要快捷方式"""
        return llm_client.summarize(text, max_length)

    def capture_app(self, app_name: str, do_ocr: bool = True,
                     vision_prompt: str = None,
                     enhance: bool = False,
                     activate_first: bool = True) -> dict:
        """一键截图→分析（包装 screen_capture_pipeline.capture_and_analyze）
        
        Args:
            app_name: 应用名（如 'Cursor', 'Terminal'）
            do_ocr: 是否OCR（默认True）
            vision_prompt: 视觉分析提示词（None跳过）
            enhance: OCR增强
            activate_first: 激活窗口到前台
        
        Returns:
            结构化结果 dict，含 status/app/bbox/ocr/vision 等字段
        
        用法:
            result = inference.capture_app("Terminal", do_ocr=True)
            print(result["ocr"]["text"])
            
            result = inference.capture_app("Cursor", vision_prompt="截图里有什么按钮?")
            print(result.get("vision", ""))
        """
        from memory.screen_capture_pipeline import capture_and_analyze
        return capture_and_analyze(
            app_name=app_name,
            do_ocr=do_ocr,
            vision_prompt=vision_prompt,
            enhance=enhance,
            activate_first=activate_first,
        )

    def vision(self, image_input, prompt: str = "详细描述这张图片的内容", **kwargs) -> str:
        """图像推理（统一入口）
        
        尝试 vision_api.ask_vision()，若失败则回退到 OCR（tesseract引擎）。
        回退结果以 "[OCR Fallback]" 前缀标记。
        """
        try:
            return vision_api.ask_vision(image_input, prompt, **kwargs)
        except Exception as e:
            # Vision API 不可用，回退到 OCR
            from PIL import Image
            img = Image.open(image_input) if isinstance(image_input, str) else image_input
            ocr_result = ocr_utils.ocr_image(img, engine='tesseract')
            text = ocr_result.get('text', '').strip()
            if text:
                return f"[OCR Fallback] {text}"
            return f"[OCR Fallback] (未识别到文字)"


# 全局单例
inference = _Inference()

# 快捷引用（保持与原模块API一致）
ask_llm = llm_client.ask_llm
ask_llm_structured = llm_client.ask_llm_structured
ask_vision = vision_api.ask_vision
