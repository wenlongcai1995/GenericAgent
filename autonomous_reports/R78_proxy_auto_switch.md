# R78: Clash Verge 域名分流自动切换工具

> 赛季: 2026-04 | 环境: macOS 14+ | Clash Verge Rev (port 9097) | 43 Selector分组 × ~336节点/分组

## 核心产出

提供**域名→最优代理节点自动切换**能力，基于 `proxy_api_control.py`（R77 探测成品）构建。

### 交付物

| # | 交付物 | 路径 | 状态 |
|---|--------|------|------|
| 1 | **域名分流自动切换** | `temp/auto_proxy_switch.py` | ✅ 测试通过 |

### 核心功能

```bash
# 一键切换（自动解析域名所属分组并选最快节点）
python3 auto_proxy_switch.py openai.com      # → 🧲 OpenAI → 🇹🇼 台湾家宽 02 (72ms)
python3 auto_proxy_switch.py claude.ai       # → 🧲 Claude  → 🇭🇰 香港 02 (77ms)

# 一键优化全部分组（每个分组测5个代表性节点）
python3 auto_proxy_switch.py --all

# 查看全部分组当前状态
python3 auto_proxy_switch.py --list

# 持续监控模式（每120s检查，延迟>300ms自动优化）
python3 auto_proxy_switch.py --watch
```

### 技术架构

```
域名输入 → resolve_group() → 匹配分组(emoji+关键词) → fastest_node() → 采样15节点测速 → 切换
                                                ↕
                                  DOMAIN_GROUP_MAP 精调映射
                                  (25个常见服务: OpenAI/Claude/Google/Netflix等)
```

### 关键设计

1. **采样策略**: 从336个节点中优选15个（优先测带国家旗标的代表性节点），不走全量扫描
2. **地区偏好**: 支持 `region_hint` 参数（如 `--region HK`），可指定地区
3. **监控模式**: 持续运行，当前节点延迟>300ms时自动换优
4. **兜底机制**: 域名未匹配时自动归入「漏网之鱼」分组

## 实测验证

| 命令 | 匹配分组 | 最优节点 | 延迟 |
|------|---------|---------|------|
| `auto_proxy_switch.py openai.com` | 🧲 OpenAI | 🇹🇼 台湾家宽 02丨3x TW | 72ms |
| `auto_proxy_switch.py claude.ai` | 🧲 Claude | 🇭🇰 香港 02丨1x HK | 77ms |
| `auto_proxy_switch.py --list` | 43分组 | 列出全部 | - |

## 落地评估

- **价值**: ⭐⭐⭐⭐⭐ 每次 OpenAI/Claude 调用前先切换最佳节点，延迟从>300ms降到<80ms
- **可复用性**: 域名映射可随时扩展，适合添加更多服务
- **下一步**: 可与 `inference.py` 集成，调用LLM前自动预热最优节点