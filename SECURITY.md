# 安全规范

本项目让 WorkBuddy 接入 ChatCut 的 MCP Server。接入依赖 OAuth 令牌，**本仓库绝不保存任何密钥**。

## 绝不提交的内容

以下文件 / 字符串**不得**进入 git 或任何公开同步盘：

- `~/.workbuddy/chatcut/credentials.json` —— 含 `client_id` 与**长效** `refresh_token`
- `~/.workbuddy/mcp.json` 中由脚本注入的 `Authorization: Bearer <token>`
- 任何 `__pycache__/`、`*.pyc`

仓库内只会存在 `mcp.json.example`（模板，无 token）。

## 为什么不能提交

- `refresh_token` 是长效凭证，泄露后可长期冒用你的 ChatCut 账号与 credits。
- `access_token` 虽 1 小时过期，但足以在窗口期内操作你的项目与资产。

## 泄露后如何吊销

1. 重新运行 `chatcut_auth.py` 会**重新动态注册**一个新的 `client_id`，使旧的 `client_id` / `refresh_token` 失效。
2. 如 ChatCut 提供「已授权应用 / 会话」管理页，主动吊销旧授权。
3. 立即检查 `~/.workbuddy/chatcut/credentials.json` 与 `~/.workbuddy/mcp.json` 是否已被同步到 iCloud / 备份盘，必要时清理。
4. 若密钥**已推送到 GitHub**：公开仓库历史不可变，须视为已泄露——先执行 1~3 步吊销，再用 `git filter-repo` 或 BFG 改写历史并强制推送；注意改写无法撤销已被第三方爬取的副本，吊销才是根本手段。

## 公共客户端原理

ChatCut 采用 OAuth 2.0 **公共客户端**（`token_endpoint_auth_method: none`，无 `client_secret`）。安全性来自 **PKCE (S256)**：每次授权都生成一次性 `code_verifier`，即使授权码被拦截也无法换票。因此本方案无需、也不持有任何 secret。

## 提交前 checklist

- [ ] `git status` 中**没有** `credentials.json`、真实 `mcp.json`
- [ ] 在仓库内 `git grep -niE "Bearer |refresh_token|client_secret|access_token"` **搜不到**真实值（脚本与文档里的说明文字除外）
- [ ] `git ls-files` 仅含预期文件：README.md / .gitignore / SECURITY.md / LICENSE / mcp.json.example / chatcut_auth.py / chatcut_refresh.py / SKILL.md
- [ ] 本地凭证文件权限为 `600`：
      `chmod 600 ~/.workbuddy/chatcut/credentials.json ~/.workbuddy/mcp.json`
- [ ] 确认提交的是 `mcp.json.example` 而非真实 `mcp.json`
