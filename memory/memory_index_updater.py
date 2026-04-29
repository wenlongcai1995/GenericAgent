#!/usr/bin/env python3
"""
memory_index_updater.py - 自动维护 memory/ 目录 → L1(global_mem_insight.txt) 索引

功能:
  1. 扫描 memory/ 下所有 .md / .py 文件作为 L3 候选
  2. 读取当前 L1 的 L3 行
  3. 比较差异，显示缺失/多余的文件
  4. 安全 patL1 更新 L3 行（保留描述注释）

用法:
  python memory/memory_index_updater.py          # 只显示 diff，不修改
  python memory/memory_index_updater.py --apply   # 修改 L1

遵守 L0(META-SOP) 规则：
  - 只 patch L3 行，不动其他内容
  - 可逆操作：旧 L3 内容备份在 stdout
"""

import os
import re
import sys

MEMORY_DIR = os.path.dirname(os.path.abspath(__file__))
L1_PATH = os.path.join(MEMORY_DIR, "global_mem_insight.txt")

# 排除列表（不属于 L3 的顶层文件/目录）
EXCLUDED = {
    "global_mem_insight.txt",      # L1 本身
    "global_mem.txt",              # L2
    "memory_management_sop.md",    # L0（META-SOP）
    "memory_index_updater.py",     # 本工具自身
    "__init__.py",
    ".DS_Store",
    "__pycache__",                 # 缓存目录
    "L4_raw_sessions",             # L4 历史会话层
    "autonomous_operation_sop",    # L3 SOP目录（含helper.py）
    "file_access_stats.json",      # 自动生成的访问统计缓存
}

# 已知描述映射（新增文件无描述时仅列名，反直觉才加括号注释）
KNOWN_DESCRIPTIONS = {
    "adb_ui.py": "截图/UI树/点击",
    "autonomous_operation_sop.md": "自主任务SOP",
    "file_ops.py": "批量重命名/分类/格式转换",
    "file_ops_sop.md": "文件操作SOP",
    "gh_ops_sop.md": "GitHub CLI操作SOP",
    "github_contribution_sop.md": "GitHub绿点策略",
    "inference.py": "统一推理接口(text/vision),ollama自动检测,回退llm_client+vision_api",
    "keychain.py": "密钥管理",
    "ljqCtrl.py": "键盘鼠标模拟(底层)",
    "ljqCtrl_sop.md": "键盘鼠标SOP",
    "llm_client.py": "通用文本推理(ollama qwen3:8b)",
    "memory_cleanup_sop.md": "记忆清理SOP",
    "ocr_utils.py": "OCR工具",
    "plan_sop.md": "复杂任务规划SOP",
    "procmem_scanner.py": "进程内存扫描,仅Windows",
    "procmem_scanner_sop.md": "进程内存扫描SOP",
    "scheduled_task_sop.md": "定时任务SOP",
    "search_fetch_sop.md": "搜索+提取组合流SOP",
    "silent_fetch.py": "静默网页正文提取",
    "silent_search.py": "静默HTTP搜索",
    "skill_search_utils.py": "105K技能卡语义检索(便捷包装)",
    "subagent.md": "子智能体协调",
    "tmwebdriver_sop.md": "浏览器特殊操作SOP",
    "ui_detect.py": "UI控件检测",
    "verify_sop.md": "通用验证SOP",
    "vision_api.py": "视觉API(ollama qwen3-vl)",
    "vision_api.template.py": "视觉API模板",
    "vision_sop.md": "视觉操作SOP",
    "web_setup_sop.md": "浏览器WebDriver安装SOP",
    "xiaohongshu_profile_edit_sop.md": "小红书资料修改(app独占)",
    "xiaohongshu_schedule_publish_sop.md": "小红书定时发布",
}

# 外部工具路径映射（不在memory/下，但应出现在L3索引中）
# key=显示名, value=(路径, 描述)
EXTERNAL_TOOLS = {
    "gh_ops.py": ("temp/gh_ops.py", "封装gh CLI,issue/PR/release操作"),
}


def scan_memory_files():
    """扫描 memory/ 目录，返回 L3 候选列表（只包含 .md/.py 文件，排除目录和特殊文件）"""
    candidates = []
    for entry in sorted(os.listdir(MEMORY_DIR)):
        if entry in EXCLUDED:
            continue
        if entry.startswith('.'):
            continue
        full_path = os.path.join(MEMORY_DIR, entry)
        # 只处理文件，跳过目录
        if not os.path.isfile(full_path):
            continue
        if entry.endswith('.md') or entry.endswith('.py'):
            candidates.append(entry)
    return candidates


def build_l3_line(candidates):
    """从候选列表构建新的 L3 行（含短描述）"""
    items = []
    for c in candidates:
        desc = KNOWN_DESCRIPTIONS.get(c, "")
        if desc:
            items.append(f"{c}({desc})")
        else:
            items.append(c)
    return " | ".join(items)


def parse_current_l3(content):
    """从 L1 内容中提取当前 L3 行的起止行号"""
    lines = content.split('\n')
    l3_start = None
    l3_end = None
    for i, line in enumerate(lines):
        if line.startswith('L3:'):
            l3_start = i
            l3_end = i
            for j in range(i + 1, len(lines)):
                stripped = lines[j].lstrip()
                if stripped.startswith('|') or stripped.startswith('L3:'):
                    l3_end = j
                else:
                    break
            break
    return l3_start, l3_end


def extract_l3_items(text):
    """从 L3 行文本提取当前条目列表"""
    # 去除 "L3: " 前缀
    t = re.sub(r'^L3:\s*', '', text)
    # 合并跨行
    t = t.replace('\n', ' ')
    # 分割 |
    items = [x.strip() for x in t.split('|') if x.strip()]
    return items


def diff_l3(current_items, new_items):
    """比较差异"""
    current_set = set()
    new_set = set()
    
    # 将带描述的 item 转为纯文件名比较
    def name_only(item):
        return item.split('(')[0].strip()
    
    for item in current_items:
        current_set.add(name_only(item))
    for item in new_items:
        new_set.add(name_only(item))
    
    missing = new_set - current_set
    extra = current_set - new_set
    
    return missing, extra


def patch_l1(content, new_l3_line, l3_start, l3_end):
    """安全替换 L3 行"""
    lines = content.split('\n')
    
    # 新 L3 行文本（支持续行，每行≤120字符提高可读性）
    max_line_len = 120
    prefix = "L3: "
    if len(new_l3_line) <= max_line_len - len(prefix):
        new_lines = [f"{prefix}{new_l3_line}"]
    else:
        # 分割成多行
        parts = new_l3_line.split(" | ")
        new_lines = []
        current_line = prefix
        for part in parts:
            sep = " | " if current_line != prefix else ""
            candidate = f"{current_line}{sep}{part}"
            if len(candidate) > max_line_len and current_line != prefix:
                new_lines.append(current_line)
                current_line = f"  | {part}"
            else:
                current_line = candidate
        if current_line:
            new_lines.append(current_line)
    
    # 替换
    new_lines_flat = '\n'.join(new_lines)
    old_lines_flat = '\n'.join(lines[l3_start:l3_end + 1])
    
    new_content = content.replace(old_lines_flat, new_lines_flat, 1)
    
    return new_content, old_lines_flat, new_lines_flat


def main():
    apply = "--apply" in sys.argv
    
    # 1. 扫描文件
    candidates = scan_memory_files()
    
    # 2. 读取当前 L1
    with open(L1_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 3. 解析当前 L3
    l3_start, l3_end = parse_current_l3(content)
    if l3_start is None:
        print("❌ 未在 L1 中找到 L3 行")
        sys.exit(1)
    
    current_items = extract_l3_items('\n'.join(content.split('\n')[l3_start:l3_end + 1]))
    new_items = build_l3_line(candidates)
    new_item_list = new_items.split(" | ")
    
    # 追加外部工具（不在memory/下，但应出现在L3索引中）
    for name, (path, desc) in EXTERNAL_TOOLS.items():
        new_item_list.append(f"{name}({path},{desc})")
    new_items = " | ".join(new_item_list)  # 重新构建含外部工具的完整L3行
    
    # 4. 比较差异
    missing, extra = diff_l3(current_items, new_item_list)
    
    print(f"📊 扫描结果: memory/ 下 {len(candidates)} 个 L3 候选")
    print(f"📋 当前 L1 中: {len(current_items)} 项")
    print(f"📋 应更新为:   {len(new_item_list)} 项\n")
    
    if not missing and not extra:
        print("✅ L1 L3 索引已是最新，无需修改")
        return
    
    if missing:
        print(f"🟢 新增文件 ({len(missing)}):")
        for m in sorted(missing):
            print(f"   + {m}")
    
    if extra:
        print(f"🔴 已移除文件 ({len(extra)}):")
        for e in sorted(extra):
            print(f"   - {e}")
    
    if not apply:
        print("\n💡 使用 --apply 参数应用更新")
        return
    
    # 5. 应用 patch
    new_content, old_text, new_text = patch_l1(content, new_items, l3_start, l3_end)
    
    print(f"\n🔄 应用更新:")
    print(f"   旧: {old_text[:80]}...")
    print(f"   新: {new_text[:80]}...")
    
    with open(L1_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"\n✅ L1 已更新！建议执行 git diff 验证变更")


if __name__ == "__main__":
    main()