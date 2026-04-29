#!/usr/bin/env python3
"""
macOS 屏幕截取 + OCR / Vision 分析管道 (v3.0 - Quartz窗口枚举)
============================================================
v3.0 使用 Quartz 直接枚举真实应用窗口，替代 pygetwindow

新增: --list-apps 列出真实应用窗口 | --app 按应用名截取
保留: --window (pygetwindow旧模式) | --bbox 坐标模式 | --scan 全屏扫描

依赖:
  - PyObjC (Quartz): macOS原生窗口枚举
  - PIL.ImageGrab: 截图
  - memory.ocr_utils: OCR
  - memory.vision_api: Vision

使用方式:
  python screen_capture_pipeline.py --list-apps              # 列出所有应用窗口
  python screen_capture_pipeline.py --app "Cursor"           # 截取Cursor窗口
  python screen_capture_pipeline.py --app "Chrome" --ocr     # 窗口截图+OCR
  python screen_capture_pipeline.py --app "Safari" --vision "描述页面"
  python screen_capture_pipeline.py --window "终端"          # pygetwindow旧模式
  python screen_capture_pipeline.py --bbox 100,200,800,600   # 原坐标模式
  python screen_capture_pipeline.py --scan                   # 全屏扫描(谨慎)

遵守 vision_sop:
  1. 先枚举窗口 → 再截图(绝不全屏)
  2. 能用OCR不用Vision
  3. 截图前自动激活窗口
"""

import sys, os, time, json, argparse, subprocess
from collections import defaultdict

_GA_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _GA_ROOT not in sys.path: sys.path.insert(0, _GA_ROOT)

def _import_modules():
    global ocr_utils, ask_vision, ImageGrab, Image
    from memory import ocr_utils as _ocr
    from memory.vision_api import ask_vision as _vis
    from PIL import ImageGrab, Image
    ocr_utils = _ocr
    ask_vision = _vis
    ImageGrab = ImageGrab
    Image = Image

def _get_dpi_scale():
    """
    检测DPI缩放系数 (逻辑→物理坐标转换)
    使用 AppKit backingScaleFactor (macOS Retina 标准方法)
    """
    try:
        from AppKit import NSScreen
        screen = NSScreen.mainScreen()
        return float(screen.backingScaleFactor())
    except Exception:
        # 回退: 用 PIL 探测
        full = ImageGrab.grab()
        phys_w, _ = full.size
        return phys_w / 1920.0


# ═══════════════════════════════════════════
#  Quartz 窗口枚举 (核心)
# ═══════════════════════════════════════════

def list_app_windows():
    """
    使用 Quartz 枚举所有真实应用窗口 (layer=0, 非系统, 尺寸合理)
    返回 [(owner_name, title, window_id, x, y, w, h), ...]
    按面积降序排列。
    """
    from Quartz import CGWindowListCopyWindowInfo
    from Quartz import kCGWindowListOptionAll, kCGNullWindowID

    wins = CGWindowListCopyWindowInfo(kCGWindowListOptionAll, kCGNullWindowID)
    system_owners = {'Window Server', 'loginwindow', 'Dock', 'SystemUIServer'}

    apps = []
    for w in wins:
        layer = w.get('kCGWindowLayer', 999)
        bounds = w.get('kCGWindowBounds', {})
        owner = w.get('kCGWindowOwnerName', '?') or '?'
        name = w.get('kCGWindowName', '') or ''
        w_id = w.get('kCGWindowNumber', 0)
        x = bounds.get('X', 0)
        y = bounds.get('Y', 0)
        wd = bounds.get('Width', 0)
        ht = bounds.get('Height', 0)

        if layer == 0 and wd > 200 and ht > 100 and owner not in system_owners:
            apps.append((owner, name, w_id, int(x), int(y), int(wd), int(ht)))

    apps.sort(key=lambda a: a[5]*a[6], reverse=True)
    return apps


def list_apps_grouped():
    """
    按应用名分组，每组只返回面积最大的窗口。
    返回 [(owner_name, num_windows, main_x, main_y, main_w, main_h), ...]
    """
    apps = list_app_windows()
    groups = defaultdict(list)
    for owner, name, wid, x, y, w, h in apps:
        groups[owner].append((x, y, w, h, wid, name))

    result = []
    for owner, windows in groups.items():
        windows.sort(key=lambda a: a[2]*a[3], reverse=True)
        x, y, w, h, wid, name = windows[0]
        result.append((owner, len(windows), x, y, w, h))

    result.sort(key=lambda r: r[4]*r[5], reverse=True)
    return result


def find_app_window(match, app_windows=None):
    """按应用名子串查找窗口，返回(owner_name, name, wid, x, y, w, h)或None"""
    if app_windows is None:
        app_windows = list_app_windows()

    # 精确匹配 owner name
    for owner, name, wid, x, y, w, h in app_windows:
        if owner.lower() == match.lower():
            return (owner, name, wid, x, y, w, h)

    # 子串匹配 owner name
    matches = [(o, n, wid, x, y, w, h) for o, n, wid, x, y, w, h in app_windows
               if match.lower() in o.lower()]
    if matches:
        return matches[0]  # 面积最大的
    return None


# ═══════════════════════════════════════════
#  窗口激活
# ═══════════════════════════════════════════

def activate_app(app_name):
    """通过AppleScript激活应用"""
    try:
        script = f'tell application "{app_name}" to activate'
        subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=5)
        time.sleep(0.3)
        return True
    except:
        try:
            script = f'''
            tell application "System Events"
                set frontmost of first process whose name contains "{app_name}" to true
            end tell
            '''
            subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=5)
            time.sleep(0.3)
            return True
        except:
            return False


# ═══════════════════════════════════════════
#  截图
# ═══════════════════════════════════════════

def _grab_region(bbox):
    """
    截取指定区域 (物理像素坐标)。
    macOS 15+ 上 screencapture -R 已损坏，改用全屏截图 + PIL 裁剪。
    """
    from PIL import ImageGrab
    full = ImageGrab.grab()  # 全屏截图 (不使用有问题的 -R 参数)
    x1, y1, x2, y2 = bbox
    return full.crop((x1, y1, x2, y2))

def capture_app_window(app_name, activate_first=True):
    """
    按应用名截图。
    返回 (PIL Image, bbox_physical, owner_name)
    """
    scale = _get_dpi_scale()
    info = find_app_window(app_name)
    if not info:
        raise ValueError(f"未找到匹配应用: '{app_name}'")

    owner, title, wid, x, y, w, h = info

    if activate_first:
        activate_app(owner)

    # Quartz 返回逻辑坐标，转换为物理坐标
    phys_left = int(x * scale)
    phys_top = int(y * scale)
    phys_right = int((x + w) * scale)
    phys_bottom = int((y + h) * scale)
    bbox = (phys_left, phys_top, phys_right, phys_bottom)

    image = _grab_region(bbox)
    return image, bbox, owner


def capture_region(bbox):
    """截图指定区域。bbox: (x1, y1, x2, y2) 物理像素坐标"""
    x1, y1, x2, y2 = bbox
    w, h = x2 - x1, y2 - y1
    if w <= 0 or h <= 0:
        raise ValueError(f"无效bbox: {bbox}")
    return _grab_region(bbox)


# ═══════════════════════════════════════════
#  分析
# ═══════════════════════════════════════════

def analyze_ocr(image, enhance=False):
    return ocr_utils.ocr_image(image, enhance=enhance)


def analyze_vision(image, prompt="详细描述这张图片的内容", timeout=120):
    return ask_vision(image, prompt=prompt, timeout=timeout)


def scan_screen_for_text(grid_cols=8, grid_rows=6):
    """扫描全屏找文字区域（谨慎使用）"""
    full_w, full_h = ImageGrab.grab().size
    cw, ch = full_w // grid_cols, full_h // grid_rows
    found = []
    for r in range(grid_rows):
        for c in range(grid_cols):
            bbox = (c*cw, r*ch, (c+1)*cw, (r+1)*ch)
            img = _grab_region(bbox)
            result = ocr_utils.ocr_image(img, enhance=False)
            text = result.get('text', '').strip()
            if text:
                found.append((bbox, text))
    return found


# ═══════════════════════════════════════════
#  pygetwindow 旧模式 (兼容 --window)
# ═══════════════════════════════════════════

def _list_windows_pygetwindow():
    import pygetwindow as gw
    titles = gw.getAllTitles()
    result = []
    seen = set()
    for i, title in enumerate(titles):
        ts = title.strip()
        if not ts or ts in seen:
            continue
        seen.add(ts)
        try:
            geo = gw.getWindowGeometry(ts)
            if geo and (geo[2] > 50 or geo[3] > 50):
                result.append((i, ts, geo))
        except:
            pass
    return result


def _find_window_pygetwindow(match):
    windows = _list_windows_pygetwindow()
    for idx, title, geo in windows:
        if title.lower() == match.lower():
            return title, geo
    for idx, title, geo in windows:
        if match.lower() in title.lower():
            return title, geo
    return None


def _capture_pygetwindow(title, activate_first=True):
    scale = _get_dpi_scale()
    info = _find_window_pygetwindow(title)
    if not info:
        raise ValueError(f"pygetwindow未找到: '{title}'")
    win_title, geo = info
    if activate_first:
        _activate_pygetwindow(win_title)
    left, top, width, height = geo
    phys_left = int(left * scale)
    phys_top = int(top * scale)
    phys_right = int((left + width) * scale)
    phys_bottom = int((top + height) * scale)
    bbox = (phys_left, phys_top, phys_right, phys_bottom)
    image = _grab_region(bbox)
    return image, bbox, win_title


def _activate_pygetwindow(title):
    try:
        script = f'tell application "{title}" to activate'
        subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=5)
        time.sleep(0.3)
        return True
    except:
        return False


# ═══════════════════════════════════════════
#  程序API（供其他模块import调用）
# ═══════════════════════════════════════════

def capture_app(app_name: str, activate_first: bool = True) -> tuple:
    """按应用名截图，返回 (PIL Image, bbox, owner_name)
    
    Args:
        app_name: 应用名（如 'Cursor', 'Terminal'）
        activate_first: 是否激活窗口到前台
    
    Returns:
        (image, bbox, owner_name)
    
    Raises:
        ValueError: 未找到应用窗口
    """
    _import_modules()
    return capture_app_window(app_name, activate_first=activate_first)


def capture_and_analyze(app_name: str, do_ocr: bool = True,
                        vision_prompt: str = None,
                        enhance: bool = False,
                        activate_first: bool = True) -> dict:
    """一键截图→分析，返回结构化结果
    
    Args:
        app_name: 应用名
        do_ocr: 是否做OCR
        vision_prompt: 视觉分析提示词（None则跳过）
        enhance: OCR增强
        activate_first: 激活窗口
    
    Returns:
        {
            "status": "ok" | "error",
            "app": app_name,
            "matched_owner": owner,
            "bbox": [x1,y1,x2,y2],
            "ocr": {"text": ..., "lines": [...], "num_lines": N, "elapsed_s": ...},
            "vision": "..."  # 仅当vision_prompt指定时
        }
    """
    _import_modules()
    import time
    
    image, bbox, owner = capture_app_window(app_name, activate_first=activate_first)
    
    result = {
        "status": "ok",
        "app": app_name,
        "matched_owner": owner,
        "bbox": list(bbox),
    }
    
    if do_ocr:
        start = time.time()
        ocr_result = analyze_ocr(image, enhance=enhance)
        result["ocr"] = {
            "text": ocr_result.get("text", ""),
            "lines": ocr_result.get("lines", []),
            "num_lines": len(ocr_result.get("lines", [])),
            "elapsed_s": round(time.time() - start, 2),
        }
    
    if vision_prompt:
        start = time.time()
        vision_result = analyze_vision(image, prompt=vision_prompt)
        result["vision"] = vision_result
        result["vision_elapsed_s"] = round(time.time() - start, 2)
    
    return result


# ═══════════════════════════════════════════
#  主入口
# ═══════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="macOS屏幕截取+OCR/Vision管道 v3.0 (Quartz窗口)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--bbox', type=str, help='截图区域: x1,y1,x2,y2 (物理坐标)')
    group.add_argument('--scan', action='store_true', help='扫描全屏找文字(谨慎)')
    group.add_argument('--app', type=str, help='按应用名截图(如"Cursor")')
    group.add_argument('--window', type=str, help='pygetwindow旧模式(按窗口标题)')
    group.add_argument('--list-apps', action='store_true', help='列出所有应用窗口')
    group.add_argument('--list-windows', action='store_true', help='pygetwindow列出窗口(旧模式)')

    parser.add_argument('--vision', type=str, default=None, help='Vision prompt')
    parser.add_argument('--ocr', dest='do_ocr', action='store_true', default=True,
                       help='做OCR (默认True)')
    parser.add_argument('--no-ocr', dest='do_ocr', action='store_false', help='跳过OCR')
    parser.add_argument('--enhance', action='store_true', help='OCR增强')
    parser.add_argument('--save', type=str, default=None, help='保存截图')
    parser.add_argument('--json', action='store_true', help='JSON输出')
    parser.add_argument('--no-activate', action='store_true', help='截图前不激活窗口')
    args = parser.parse_args()

    _import_modules()
    image = None
    capture_info = {}

    # ── 列出所有APP窗口(新) ──
    if args.list_apps:
        apps = list_apps_grouped()
        scale = _get_dpi_scale()
        print(f"📋 共有 {len(apps)} 个应用窗口 (DPI scale={scale:.1f})")
        print(f"   {'应用名':<25} {'窗口数':>3} {'逻辑坐标':<28} {'物理坐标':<28}")
        print(f"   {'-'*25} {'-'*3} {'-'*28} {'-'*28}")
        for owner, num, x, y, w, h in apps:
            phys = f"({int(x*scale)},{int(y*scale)},{int((x+w)*scale)},{int((y+h)*scale)})"
            log = f"({x},{y},{w},{h})"
            print(f"   {owner:<25} {num:>3} {log:<28} {phys:<28}")

        # 显示所有原始窗口详情
        all_wins = list_app_windows()
        print(f"\n📋 所有 {len(all_wins)} 个原始窗口:")
        for owner, name, wid, x, y, w, h in all_wins[:30]:
            title_s = name[:30] if name else '(空)'
            print(f"   [{wid:>4}] {owner:20s} title='{title_s:30s}' ({x},{y},{w},{h})")
        if len(all_wins) > 30:
            print(f"   ... 还有 {len(all_wins)-30} 个")
        return 0

    # ── 列出pygetwindow窗口(旧模式) ──
    if args.list_windows:
        windows = _list_windows_pygetwindow()
        scale = _get_dpi_scale()
        print(f"📋 pygetwindow: 共有 {len(windows)} 个窗口 (DPI scale={scale:.1f})")
        for idx, title, geo in windows:
            l, t, w, h = geo
            phys = f"({int(l*scale)},{int(t*scale)},{int((l+w)*scale)},{int((t+h)*scale)})"
            print(f"   [{idx:>2}] {title:<40} ({l:.0f},{t:.0f},{w:.0f},{h:.0f}) {phys}")
        return 0

    # ── 按APP截图(新模式) ──
    if args.app:
        print(f"🔍 查找应用: '{args.app}'")
        try:
            image, bbox, owner = capture_app_window(args.app, activate_first=not args.no_activate)
            print(f"📸 界面截图: {owner} bbox={bbox} (物理像素)")
            capture_info['app'] = args.app
            capture_info['matched_owner'] = owner
            capture_info['bbox'] = list(bbox)
        except ValueError as e:
            print(f"❌ {e}")
            print("提示: 用 --list-apps 查看可用应用")
            return 1

    # ── pygetwindow旧模式 ──
    elif args.window:
        print(f"🔍 pygetwindow查找窗口: '{args.window}'")
        try:
            image, bbox, title = _capture_pygetwindow(args.window, activate_first=not args.no_activate)
            print(f"📸 窗口截图: '{title}' bbox={bbox} (物理像素)")
            capture_info['window'] = args.window
            capture_info['matched_title'] = title
            capture_info['bbox'] = list(bbox)
        except ValueError as e:
            print(f"❌ pygetwindow: {e}")
            print("提示: 建议使用 --app 替代 --window 以获得更好的窗口发现")
            return 1

    # ── 坐标截图 ──
    elif args.bbox:
        coords = [int(x.strip()) for x in args.bbox.split(',')]
        if len(coords) != 4:
            print("Error: bbox需要4个数字: x1,y1,x2,y2")
            return 1
        image = capture_region(tuple(coords))
        capture_info['bbox'] = coords

    # ── 全屏扫描 ──
    elif args.scan:
        print("🔍 扫描全屏找文字...")
        found = scan_screen_for_text()
        if not found:
            msg = "未找到文字区域"
            if args.json:
                print(json.dumps({"status": "no_text", "message": msg}))
            else:
                print(f"  {msg}")
            return 0
        print(f"  找到{len(found)}个文字区域:")
        for i, (bbox, text) in enumerate(found[:5]):
            print(f"  [{i}] bbox={bbox}: {text[:60]}")
        return 0

    # ── 保存截图 ──
    if args.save:
        image.save(args.save)
        print(f"  💾 已保存: {args.save}")

    # ── OCR分析 ──
    if args.do_ocr and image:
        print("  🔤 OCR分析中...")
        start = time.time()
        ocr_result = analyze_ocr(image, enhance=args.enhance)
        elapsed = time.time() - start
        text = ocr_result.get('text', '')
        lines = ocr_result.get('lines', [])

        if args.json:
            output = {
                "status": "ok",
                "capture": capture_info,
                "ocr": {
                    "text": text,
                    "lines": lines,
                    "num_lines": len(lines),
                    "elapsed_s": round(elapsed, 2)
                }
            }
        else:
            print(f"  📝 OCR ({elapsed:.1f}s): {len(text)}字符, {len(lines)}行")
            if text:
                print("  ──文字内容──")
                print(text[:2000])
            else:
                print("  (无文字)")
    else:
        output = {"status": "ok", "capture": capture_info}

    # ── Vision分析(可选) ──
    if args.vision and image:
        print(f"  👁️ Vision分析中 (prompt: {args.vision[:60]}...)")
        start = time.time()
        vision_result = analyze_vision(image, args.vision)
        elapsed = time.time() - start
        if args.json:
            output['vision'] = {
                "prompt": args.vision,
                "result": vision_result,
                "elapsed_s": round(elapsed, 2)
            }
        else:
            print(f"  👁️ Vision ({elapsed:.1f}s):")
            print(vision_result[:3000])

    # ── JSON输出 ──
    if args.json and (args.bbox or args.app or args.window):
        print(json.dumps(output, ensure_ascii=False, indent=2))

    return 0


if __name__ == '__main__':
    sys.exit(main())