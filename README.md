# WorkBuddy × ChatCut MCP 接入

把 [ChatCut](https://chatcut.io)（AI 视频剪辑 SaaS）的整间「剪辑室」以 MCP Server 形式接入 [WorkBuddy](https://workbuddy.ai)，用自然语言直接驱动它剪视频、加字幕、做长短切、生成 B-roll / 口播 / 商业短片，并拿到**可继续手动精修的真实时间线**。

> 本项目提供接入所需的 OAuth 授权脚本、MCP 配置模板与操作手册。**不包含任何密钥**——令牌在你本地授权后生成，绝不进 git。

## ✨ 特性

- 🔌 标准 MCP（Streamable HTTP）接入，WorkBuddy 原生支持
- 🔐 OAuth 2.0 + PKCE（公共客户端，无 client_secret）标准安全形态
- 🪪 一键授权脚本：动态客户端注册 → 浏览器登录 → 自动写回配置
- 🔄 令牌续期脚本：access_token 过期后无感刷新
- 📚 配套 WorkBuddy Skill，开箱即用的剪辑能力说明
- 🖥️ 在 WorkBuddy 内置浏览器直接打开 ChatCut 编辑器（页面无 iframe 限制，配置完即用）

## 🧩 原理

ChatCut 把自己以**托管 MCP Server** 形式开放：

```
https://api.chatcut.io/api/external-mcp/mcp
```

WorkBuddy 支持自定义 MCP 连接器，但**不会自动弹出 OAuth 登录框**。因此本项目用两个小脚本完成接入：

1. `chatcut_auth.py`：动态注册一个 OAuth 公共客户端（PKCE/S256），打开浏览器让你登录授权，拿到令牌后写入 `~/.workbuddy/mcp.json`。
2. `chatcut_refresh.py`：access_token 约 1 小时过期，用它续期。

认证链路经实测可用（动态注册真实返回 `client_id`，`client_secret` 为 null）。

## 📋 前置条件

- 已安装 Python 3.8+（仅用标准库，无需 pip）
- 一个 ChatCut 账号（[chatcut.io](https://chatcut.io)）
- 本地已安装 WorkBuddy，且 `~/.workbuddy/mcp.json` 可写
- 授权脚本会在 `localhost:18930` 监听 OAuth 回调，请确保该端口未被占用

## 🚀 快速开始

```bash
# 1. 克隆本项目
git clone https://github.com/chonpszhou/workbuddy-chatcut-mcp.git
cd workbuddy-chatcut-mcp

# 2. 把 MCP 配置模板放进 WorkBuddy（不含 token，仅 URL + 兼容头）
cp mcp.json.example ~/.workbuddy/mcp.json
#   若你已有 mcp.json，请手动把 chatcut 条目合并进去

# 3. 运行授权脚本，浏览器登录并授权
python3 chatcut_auth.py

# 4. 在 WorkBuddy 连接器面板找到 chatcut，点击「信任 / 启用」
#   （若工具数为 0，重启 WorkBuddy）

# 5. 冒烟测试：用 list 类只读工具（如 list_projects），
#    应加载约 52 个 ChatCut 工具
```

令牌过期后续期：

```bash
python3 chatcut_refresh.py
```

## 📁 文件说明

| 文件 | 作用 |
|------|------|
| `chatcut_auth.py` | OAuth 登录：动态注册 + PKCE + 本地回调 + 写令牌 |
| `chatcut_refresh.py` | 用 refresh_token 续期 access_token |
| `mcp.json.example` | MCP 配置模板（仅 url + 兼容头，无 token） |
| `SKILL.md` | WorkBuddy Skill：剪辑能力说明与使用建议 |
| `open_projects.py` | 列出项目并输出可在 WorkBuddy 内置浏览器打开的编辑器链接 |
| `SECURITY.md` | 安全与密钥管理规范 |
| `.gitignore` | 忽略凭证与本地文件 |

## 🔒 安全

- 本项目**不包含任何 token / refresh_token / client_secret**。
- 真实凭证只存在于你本地的 `~/.workbuddy/chatcut/credentials.json`（权限 600）与 `~/.workbuddy/mcp.json`（权限 600）。
- 详见 [SECURITY.md](./SECURITY.md)。

## 🖥️ 在 WorkBuddy 内置浏览器打开编辑器

配置并信任 `chatcut` 后，你可以**不切到外部浏览器**，直接在 WorkBuddy 的内置预览面板里打开 ChatCut 编辑器做手动精修。

**原理**：ChatCut 编辑器页面（`app.chatcut.io/editor/<project_id>`）经实测**没有 `X-Frame-Options` / CSP `frame-ancestors` 限制**，可以被 WorkBuddy 的内置浏览器预览面板直接嵌入打开。

### 方式一：对话式（推荐，最省事）
在 WorkBuddy 对话框里说：
> 列出我 ChatCut 里的项目

WorkBuddy 会调用 `list_projects` 并返回每个项目的编辑器链接，**直接点链接即可在内置面板打开**。

### 方式二：命令行拿链接
运行本项目提供的脚本，自动列出项目并打印可在内置面板打开的编辑器链接：

```bash
python3 open_projects.py
```

### 注意事项
- **首次**在面板里打开需要先**登录一次 ChatCut 网站账号**——内置预览面板是独立的 webview，与外部浏览器的登录态不共享；登录一次后 cookie 会保留在该面板。
- 区分两类登录：MCP 的 OAuth token（`mcp.json`，已就绪）用于工具调用；ChatCut 网站 session cookie 用于 web 编辑器手动精修。
- 真正「完全不切浏览器」的剪辑主路径是用自然语言让 WorkBuddy 调 ChatCut 工具（如「给某项目加字幕、掐头去尾」），连打开页面都不需要。

## ⚠️ 已知限制

- 请求头 `x-chatcut-mcp-surface: codex` 为兼容占位，未来服务端可能加强校验。
- 仅依赖 Codex 内置浏览器等专属功能在 WorkBuddy 不可用。
- ChatCut 用 credits 计费，长视频与生成类消耗大，先确认额度。

## 📄 License

[MIT](./LICENSE) © chonpszhou
