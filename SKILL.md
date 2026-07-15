---
name: chatcut
description: 通过 WorkBuddy 的 ChatCut MCP 连接器直接驱动 ChatCut AI 视频剪辑。当用户想在 WorkBuddy 里剪视频、加字幕、做长短切、加动效、生成 B-roll / 口播 / 商业短片、整理时间线并导出时使用。
---

# ChatCut（WorkBuddy MCP 接入）

ChatCut 是一个把整间剪辑室以 MCP Server 形式开放的 AI 视频剪辑 SaaS。WorkBuddy 接入后，可直接用自然语言驱动它完成剪辑工作流，并在 ChatCut 里拿到**可继续手动精修的真实时间线**。

## 前置条件
- 已在 `~/.workbuddy/mcp.json` 配置 `chatcut` 条目（url: `https://api.chatcut.io/api/external-mcp/mcp`）。
- 已运行 `chatcut_auth.py` 完成 OAuth 登录，令牌已写入 mcp.json。
- 在 WorkBuddy 连接器面板对 `chatcut` 点击「信任 / 启用」（必要时重启 WorkBuddy）。
- access_token 约 1 小时过期，过期后运行 `chatcut_refresh.py` 续期。

## 连接验证（冒烟测试）
连接成功后，ChatCut 会暴露约 52 个工具。可用只读类工具确认已加载，例如列出项目 / 资产，或调用一个 list 类工具。若工具数为 0 或调用 403，说明令牌未生效——重新授权或重启 WorkBuddy。

## 常用能力（对应 ChatCut 工作流）
- **口播精修 (talking-head)**：清理填充词/静默、保留高光、加字幕与轻量配乐，渲染 MP4。
- **长转短 (long-to-short)**：把播客/访谈扫描出最强段落，切 9:16 竖屏短视频并加字幕。
- **自动字幕 (auto-caption)**：逐词级字幕，按时长对齐，可直接发社媒。
- **动态图形 (motion graphics)**：下三分之一、标题卡、数据图表，按 prompt 生成并上轨。
- **AI B-roll / 短片 / 商业片 / 解说 / UGC 广告**：描述缺失镜头或产品卖点，生成并落到时间线。
- **多轨时间线**：所有编辑都落在真实时间线，不烘焙成扁平导出，可继续改节奏/文案/顺序。
- **导出**：MP4、可导入 Premiere/DaVinci 的 XML、SRT 字幕、Word 文档。

## 使用建议
1. 先给素材或主题/prompt，让 ChatCut 出初剪与时间线。
2. 用「可调时间线」特性继续让 Agent 微调，或拿到链接去 ChatCut 手动精修。
3. 导出时按需选 MP4（直发）或 XML（进专业软件精修）。
4. 涉及账号/付费额度：ChatCut 用 credits 计费，长视频与生成类消耗大，先确认额度。

## 注意
- 请求头 `x-chatcut-mcp-surface: codex` 为兼容占位，未来服务端可能加强校验。
- 仅依赖 Codex 内置浏览器等的专属功能在 WorkBuddy 不可用。
- 令牌存于 `~/.workbuddy/mcp.json`（权限 600），refresh_token 存于 `~/.workbuddy/chatcut/credentials.json`（权限 600），勿提交到 git 或同步盘。
- **在 WorkBuddy 内置浏览器打开编辑器**：ChatCut 编辑器页面无 iframe 限制，可被内置预览面板直接嵌入。对话说「列出我 ChatCut 里的项目」或运行仓库的 `open_projects.py` 拿到 editor 链接，在面板里打开即可；首次需在面板登录一次 ChatCut 账号（面板为独立 webview，与外部浏览器登录态隔离）。日常剪辑优先走 MCP 工具（自然语言驱动），手动精修才用 web 编辑器。
