# 🤝 贡献指南

感谢你考虑为 **WorkBuddy × ChatCut MCP** 做贡献！无论是修 bug、补文档还是加新能力，都欢迎。

## 🧰 本地开发

```bash
git clone https://github.com/chonpszhou/workbuddy-chatcut-mcp.git
cd workbuddy-chatcut-mcp
python3 -m venv .venv && source .venv/bin/activate  # 可选
```

本项目仅用 Python 标准库，无需 `pip install`。

## ✅ 提交前检查

- [ ] 未提交任何密钥：`credentials.json`、`mcp.json`、含 `Bearer ` / `refresh_token` / `client_secret` 的内容
- [ ] 已通过 `python3 -m py_compile chatcut_auth.py chatcut_refresh.py open_projects.py`
- [ ] 更新了相关文档（README / SECURITY / SKILL）
- [ ] 新增能力已在 `SKILL.md` 说明

> 仓库已配置 [Gitleaks](https://github.com/gitleaks/gitleaks) CI，push / PR 会自动扫描密钥；疑似泄露会被直接卡住，合并前拦截。

## 🔀 PR 流程

1. Fork 并创建特性分支：`git checkout -b feat/your-feature`
2. 提交：`git commit -m "feat: ..."`
3. 推送并发起 PR，在 PR 模板中勾选安全自查清单
4. 等待 CI（Secret Scan）通过 + 维护者 review

## 📝 提交信息约定

- `feat:` 新功能 · `fix:` 修复 · `docs:` 文档 · `ci:` 流水线 · `refactor:` 重构 · `test:` 测试

## 🔒 安全红线

**绝不要**在任何提交中包含真实 token / `refresh_token` / `client_secret`。一旦泄露，请立即按 [SECURITY.md](./SECURITY.md) 处理（吊销 + 改写历史）。

## 💬 讨论

有想法或疑问？欢迎开 [Issue](https://github.com/chonpszhou/workbuddy-chatcut-mcp/issues) 交流。
