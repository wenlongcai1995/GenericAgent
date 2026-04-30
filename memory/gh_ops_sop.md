# gh_ops.py SOP

## Location
memory/gh_ops.py (原 temp/gh_ops.py, 已晋升)

## Usage
`python gh_ops.py <repo> <action> [args]`

## Supported Actions
- `repo:list` / `repo:view` — 仓库操作
- `issue:list` / `issue:view <N>` / `issue:create <title> [body] [label]` / `issue:close <N>` / `issue:comment <N> <body>` — ISSUE 全生命周期
- `pr:list` / `pr:view <N>` / `pr:create <title> [body [head [base]]]` / `pr:merge <N> [method]` — PR 操作
- `release:list` / `release:create <tag> [title [notes]]` — Release 操作
  - 可选参数: `--files <paths>` 上传附件, `--latest=false` 不标记为最新

## ⚠️ 关键坑点
- `gh issue create/close`, `gh pr create/merge`, `gh release create` **不支持 `--json`** 标志
  - 只有读操作 (list/view) 支持 `--json`
  - 已封装好：create/close/merge 返回 raw 输出+正则提取关键信息
- 注意检查 repo 是否 enabled issues (`gh repo view --json hasIssuesEnabled`)