# WorkBuddy × ChatCut MCP Integration

Connect [ChatCut](https://chatcut.io) — an AI video editing SaaS — to [WorkBuddy](https://workbuddy.ai) as an MCP Server, so you can drive its full editing suite with natural language: cut videos, add subtitles, do long/short cuts, generate B-roll / talking-head / commercial clips, and get back a **real timeline you can keep refining manually**.

> This project provides the OAuth authorization scripts, an MCP config template, and an operation manual needed for the integration. **It contains no secrets** — tokens are generated locally on your machine after authorization and never enter git.

## ✨ Features

- 🔌 Standard MCP (Streamable HTTP) integration, natively supported by WorkBuddy
- 🔐 OAuth 2.0 + PKCE (public client, no `client_secret`) — a standard, secure shape
- 🪪 One-click auth script: dynamic client registration → browser login → auto-write config
- 🔄 Token refresh script: silently renew `access_token` after it expires
- 📚 Bundled WorkBuddy Skill with ready-to-use editing capability notes
- 🖥️ Open the ChatCut editor right inside WorkBuddy's built-in browser (the page has no iframe restriction, works out of the box after setup)

## 🧩 How it works

ChatCut exposes its entire editing studio as a **hosted MCP Server**:

```
https://api.chatcut.io/api/external-mcp/mcp
```

WorkBuddy supports custom MCP connectors, but it **does not pop up an OAuth login dialog automatically**. So this project uses two small scripts to complete the handshake:

1. `chatcut_auth.py`: dynamically registers an OAuth public client (PKCE/S256), opens your browser for login & authorization, then writes the token into `~/.workbuddy/mcp.json`.
2. `chatcut_refresh.py`: `access_token` expires in ~1 hour; use this to renew it.

The auth flow is verified working (dynamic registration actually returns a `client_id`, with `client_secret` being `null`).

## 📋 Prerequisites

- Python 3.8+ installed (standard library only, no `pip` needed)
- A ChatCut account ([chatcut.io](https://chatcut.io))
- WorkBuddy installed locally, with `~/.workbuddy/mcp.json` writable
- The auth script listens for the OAuth callback on `localhost:18930`; make sure that port is free

## 🚀 Quick start

```bash
# 1. Clone this project
git clone https://github.com/chonpszhou/workbuddy-chatcut-mcp.git
cd workbuddy-chatcut-mcp

# 2. Drop the MCP config template into WorkBuddy (no token — only URL + compatibility header)
cp mcp.json.example ~/.workbuddy/mcp.json
#   If you already have an mcp.json, manually merge the chatcut entry in.

# 3. Run the auth script, log in and authorize in the browser
python3 chatcut_auth.py

# 4. In WorkBuddy's Connectors panel, find chatcut and click "Trust / Enable"
#   (If the tool count shows 0, restart WorkBuddy)

# 5. Smoke test: use a list-type read-only tool (e.g. list_projects),
#    ~52 ChatCut tools should load
```

To renew the token after it expires:

```bash
python3 chatcut_refresh.py
```

## 📁 Files

| File | Purpose |
|------|---------|
| `chatcut_auth.py` | OAuth login: dynamic registration + PKCE + local callback + write token |
| `chatcut_refresh.py` | Renew `access_token` using `refresh_token` |
| `mcp.json.example` | MCP config template (URL + compatibility header only, no token) |
| `SKILL.md` | WorkBuddy Skill: editing capability notes & usage tips |
| `open_projects.py` | List projects and print editor links openable in WorkBuddy's built-in browser |
| `SECURITY.md` | Security & secret-management spec |
| `.gitignore` | Ignore credentials and local files |

## 🔒 Security

- This project **contains no token / refresh_token / client_secret**.
- Real credentials live only in your local `~/.workbuddy/chatcut/credentials.json` (mode 600) and `~/.workbuddy/mcp.json` (mode 600).
- See [SECURITY.md](./SECURITY.md) for details.
- 🤖 **CI safety net**: on every push / PR, GitHub Actions runs [Gitleaks](https://github.com/gitleaks/gitleaks) to scan for secrets. If a suspected leak is committed, the run fails automatically and blocks the merge (config in [`.github/workflows/secret-scan.yml`](./.github/workflows/secret-scan.yml) and [`.gitleaks.toml`](./.gitleaks.toml)).

## 🖥️ Open the editor in WorkBuddy's built-in browser

After configuring and trusting `chatcut`, you can **stay inside WorkBuddy** and open the ChatCut editor in the built-in preview panel for manual fine-tuning — no need to switch to an external browser.

**Why it works**: the ChatCut editor page (`app.chatcut.io/editor/<project_id>`) was verified to have **no `X-Frame-Options` / CSP `frame-ancestors` restriction**, so it can be embedded directly into WorkBuddy's built-in browser preview.

### Option A: Conversational (recommended, easiest)
Just say in the WorkBuddy chat box:
> List my ChatCut projects

WorkBuddy calls `list_projects` and returns an editor link for each project — **click the link to open it right in the built-in panel**.

### Option B: Get the link from the command line
Run the bundled script to list projects and print editor links openable in the built-in panel:

```bash
python3 open_projects.py
```

### Notes
- **First time** opening the panel, you need to **log in to your ChatCut account once** — the built-in preview is an isolated webview that does not share login state with your external browser; the cookie persists in that panel afterwards.
- Two kinds of login: the MCP OAuth token (`mcp.json`, already set up) is for tool calls; the ChatCut website session cookie is for manual editor refinement.
- The truly "never leave the browser" editing path is to tell WorkBuddy in natural language to call ChatCut tools (e.g. "add subtitles and trim the heads/tails of project X") — you don't even need to open a page.

## ⚠️ Known limitations

- The header `x-chatcut-mcp-surface: codex` is a compatibility placeholder; the server may enforce stricter checks in the future.
- Features that depend on Codex-only built-ins (e.g. its embedded browser) are unavailable in WorkBuddy.
- ChatCut bills by credits; long videos and generation-heavy operations cost more — check your quota first.

## 📄 License

[MIT](./LICENSE) © chonpszhou
