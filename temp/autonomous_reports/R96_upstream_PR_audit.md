# R96: GitHub上游PR审计与本地补丁同步

## 背景
扫描 lsdefine/GenericAgent 仓库状态：10 open issues, 5 open PRs。
选择2个明确Bug修复PR，核验本地是否已应用。

## 发现

### PR #224: HTTPS for skill_search API
- **分支**: fix/skill-search-https
- **本地状态**: ❌ 仍用 `http://www.fudankw.cn:58787`
- **修复**: 改 engine.py 1行 + SKILL.md 1行文档
- **已应用**: ✅

### PR #227: ljqCtrl.py 重复字典键
- **分支**: fix/ljqctrl-duplicate-key
- **本地状态**: ❌ VK_CODE 中 `` ` `` 键出现两次 (`0xC0`)，第二项覆盖第一项
- **修复**: 删除重复的 `'`': 0xC0` 条目
- **已应用**: ✅

## 验证
- engine.py: `DEFAULT_API_URL = "https://www.fudankw.cn:58787"` ✅
- SKILL.md: API地址改为 https ✅
- ljqCtrl.py: 无重复键，唯一 `` ` `` 键保留 ✅

## 未处理
其他3个PR (#225 #226 #212) 涉及功能增强/CI，非纯bug修复，待用户审查。
10个open issues 待用户上线后处理。
