## 变更说明
<!-- 简要描述本次 PR 的目的与内容 -->

## 变更类型
- [ ] 新功能（feature）
- [ ] Bug 修复（fix）
- [ ] 文档更新（docs）
- [ ] 安全/密钥相关（security）

## 安全自查（必填）
- [ ] 未提交任何真实 token / refresh_token / client_secret（参见 SECURITY.md）
- [ ] 已执行 `grep -RniE "Bearer |refresh_token|client_secret|access_token" .` 确认无真实密钥泄露
- [ ] `credentials.json` 与真实 `mcp.json` 已被 `.gitignore` 忽略，不会进入本仓库

## 测试方式
<!-- 说明如何验证本次变更，例如：运行 python3 chatcut_auth.py 完成授权、执行 open_projects.py 列出项目等 -->
