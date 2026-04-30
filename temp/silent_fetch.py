"""
Silent Fetch — 静默网页内容提取器

纯 HTTP 请求，不打开浏览器标签页。
基于 trafilatura 提取干净正文，自动去除导航/广告/侧边栏。

v2 改进: 对 trafilatura.fetch_url() 挂起问题加固
- concurrent.futures 包裹 fetch_url 强制超时
- 挂起/超时后自动回退到 requests.get() + trafilatura.extract()

用法:
    from silent_fetch import silent_fetch
    content = silent_fetch("https://example.com/article")
    
    或命令行:
    python silent_fetch.py "https://example.com/article" --format text
"""

import concurrent.futures
import json
import sys
from typing import Optional

import requests
import trafilatura

# 默认 User-Agent，防止部分站点拒绝
_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def _fetch_with_timeout(url: str, timeout: int = 15) -> Optional[str]:
    """用 concurrent.futures 包裹 trafilatura.fetch_url，防止无限挂起。"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(trafilatura.fetch_url, url)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            return None  # 挂起未返回，触发 fallback
        except Exception:
            return None


def _fallback_requests(url: str, timeout: int = 15) -> Optional[str]:
    """requests.get() fallback，用于 trafilatura.fetch_url 挂起/失败时。"""
    try:
        resp = requests.get(url, timeout=timeout, headers=_DEFAULT_HEADERS)
        resp.raise_for_status()
        return resp.text
    except Exception:
        return None


def _generate_summary(text: str, max_length: int = 150) -> str | None:
    """用本地LLM生成文本摘要（通过统一推理接口inference.summarize）。失败时返回None。"""
    if not text or len(text) < 200:
        return None
    try:
        import sys as _sys
        _ga_root = _sys.path[0] if _sys.path[0] else '.'
        if 'GenericAgent' not in _ga_root:
            _ga_root = '/Users/raymond/program/GenericAgent'
        if _ga_root not in _sys.path:
            _sys.path.insert(0, _ga_root)
        from memory.inference import inference as _inference
        return _inference.summarize(text, max_length=max_length)
    except Exception:
        return None


def silent_fetch(
    url: str,
    output_format: str = "text",
    timeout: int = 20,
    summarize: bool = False,
    max_summary_length: int = 150,
) -> dict:
    """
    静默提取网页正文内容，可选AI摘要。

    参数:
        url: 网页 URL
        output_format: "text" (默认), "markdown", "json"
        timeout: 请求超时秒数 (整个操作)
        summarize: 是否用本地LLM生成摘要（需ollama运行qwen3:8b）
        max_summary_length: 摘要最大字数（仅summarize=True时有效）

    返回:
        {
            "title": str or None,
            "author": str or None,
            "date": str or None,
            "text": str,  # 干净正文
            "summary": str or None,  # AI摘要（仅summarize=True时）
            "url": str,
            "success": bool,
            "error": str or None,
            "fallback": bool  # 是否使用了 requests fallback
        }
    """
    # 尝试 trafilatura.fetch_url (有超时保护)
    downloaded = _fetch_with_timeout(url, timeout=timeout)
    fallback_used = False

    if downloaded is None:
        # 挂起/超时 → fallback 到 requests.get()
        raw_html = _fallback_requests(url, timeout=timeout)
        if raw_html is None:
            return {
                "title": None, "author": None, "date": None,
                "text": "", "url": url, "success": False,
                "error": "无法获取页面内容（trafilatura挂起 + requests fallback失败）",
                "fallback": True,
                "summary": None
            }
        fallback_used = True
        # 用 trafilatura.extract 处理 requests 拿到的 HTML
        result = trafilatura.extract(
            raw_html,
            output_format='json' if output_format == 'json' else 'txt',
            include_links=(output_format == 'markdown'),
            include_images=False,
            with_metadata=True,
            url=url
        )
    else:
        # trafilatura.fetch_url 成功
        result = trafilatura.extract(
            downloaded,
            output_format='json' if output_format == 'json' else 'txt',
            include_links=(output_format == 'markdown'),
            include_images=False,
            with_metadata=True,
            url=url
        )

    if not result:
        return {
            "title": None, "author": None, "date": None,
            "text": "", "url": url, "success": False,
            "error": "提取正文失败（页面可能无实质内容）",
            "fallback": fallback_used,
            "summary": None
        }

    if output_format == 'json' and isinstance(result, str):
        try:
            data = json.loads(result)
            summary_text = None
            if summarize:
                summary_text = _generate_summary(data.get("text", ""), max_summary_length)
            return {
                "title": data.get("title"),
                "author": data.get("author"),
                "date": data.get("date"),
                "text": data.get("text", ""),
                "summary": summary_text,
                "url": url,
                "success": True,
                "error": None,
                "fallback": fallback_used
            }
        except json.JSONDecodeError:
            pass

    # text/markdown 格式
    summary_text = None
    if summarize and result:
        summary_text = _generate_summary(result, max_summary_length)
    return {
        "title": None,
        "author": None,
        "date": None,
        "text": result,
        "summary": summary_text,
        "url": url,
        "success": True,
        "error": None,
        "fallback": fallback_used
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="静默网页内容提取")
    parser.add_argument("url", help="网页 URL")
    parser.add_argument("--format", "-f", default="text",
                        choices=["text", "markdown", "json"])
    parser.add_argument("--summarize", "-s", action="store_true",
                        help="用本地LLM生成内容摘要")
    args = parser.parse_args()

    result = silent_fetch(args.url, args.format, summarize=args.summarize)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result["success"]:
            if result["title"]:
                print(f"# {result['title']}\n")
            if result["author"]:
                print(f"作者: {result['author']}")
            if result["date"]:
                print(f"日期: {result['date']}\n")
            if result["summary"]:
                print(f"📝 AI摘要: {result['summary']}\n")
            print(result["text"])
        else:
            print(f"❌ {result['error']}", file=sys.stderr)
            sys.exit(1)