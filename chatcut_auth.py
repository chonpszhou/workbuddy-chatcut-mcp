#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatCut MCP 授权脚本（WorkBuddy 接入用）
=========================================
ChatCut 的 MCP Server 走 OAuth 2.0 + PKCE（公共客户端，无 client_secret）。
本脚本自动完成：
  1) 动态客户端注册（拿到 client_id）
  2) 生成 PKCE 参数并打开浏览器让用户登录授权
  3) 本地 18930 端口接收回调授权码
  4) 用授权码换取 access_token / refresh_token
  5) 把 access_token 写入 ~/.workbuddy/mcp.json 的 Authorization 头
  6) 把 client_id / refresh_token 单独存到 ~/.workbuddy/chatcut/credentials.json（600）

仅依赖 Python 标准库，无需 pip 安装。

用法：
  python3 chatcut_auth.py
然后到 WorkBuddy 连接器面板，对 chatcut 点击「信任 / 启用」，必要时重启 WorkBuddy。
"""
import base64
import hashlib
import json
import os
import secrets
import time
import urllib.parse
import urllib.request
import urllib.error
import webbrowser
import http.server

MCP_URL = "https://api.chatcut.io/api/external-mcp/mcp"
REGISTER_URL = "https://api.chatcut.io/auth/mcp/register"
AUTH_URL = "https://api.chatcut.io/auth/mcp/authorize"
TOKEN_URL = "https://api.chatcut.io/auth/mcp/token"
REDIRECT_URI = "http://localhost:18930/callback"
SCOPE = "openid profile email offline_access"

MCP_JSON = os.path.expanduser("~/.workbuddy/mcp.json")
CRED_DIR = os.path.expanduser("~/.workbuddy/chatcut")
CRED_FILE = os.path.join(CRED_DIR, "credentials.json")

_auth_code = None


def b64url(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode("ascii").rstrip("=")


def register_client() -> dict:
    body = json.dumps({
        "redirect_uris": [REDIRECT_URI],
        "client_name": "WorkBuddy MCP Client",
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "none",
        "scope": SCOPE,
    }).encode("utf-8")
    req = urllib.request.Request(
        REGISTER_URL, data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


class _Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global _auth_code
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if "code" in params:
            _auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                "<h1>ChatCut 授权成功 ✅</h1>"
                "<p>可以关闭此页面，回到 WorkBuddy 继续。</p>".encode("utf-8")
            )
        else:
            self.send_response(400)
            self.end_headers()
        # 静默日志，避免把回调参数打进终端
        self.log_message = lambda *a, **k: None  # type: ignore

    def log_message(self, *args):  # noqa: D401
        return


def write_mcp(access_token: str):
    os.makedirs(os.path.dirname(MCP_JSON), exist_ok=True)
    if os.path.exists(MCP_JSON):
        with open(MCP_JSON, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    else:
        cfg = {"mcpServers": {}}
    cfg.setdefault("mcpServers", {})["chatcut"] = {
        "url": MCP_URL,
        "headers": {
            "x-chatcut-mcp-surface": "codex",
            "Authorization": "Bearer " + access_token,
        },
        "disabled": False,
    }
    tmp = MCP_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    os.replace(tmp, MCP_JSON)
    os.chmod(MCP_JSON, 0o600)


def save_cred(client_id: str, refresh_token, issued_at: int, expires_in: int):
    os.makedirs(CRED_DIR, exist_ok=True)
    data = {
        "client_id": client_id,
        "refresh_token": refresh_token,
        "issued_at": issued_at,
        "expires_in": expires_in,
    }
    with open(CRED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.chmod(CRED_FILE, 0o600)


def main():
    print("→ 正在向 ChatCut 注册 OAuth 公共客户端……")
    client = register_client()
    client_id = client["client_id"]
    print("✓ 已注册 client_id:", client_id)

    verifier = b64url(secrets.token_bytes(32))
    challenge = b64url(hashlib.sha256(verifier.encode("ascii")).digest())
    state = secrets.token_urlsafe(16)

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "scope": SCOPE,
        "state": state,
        "resource": MCP_URL,
    }
    url = AUTH_URL + "?" + urllib.parse.urlencode(params)

    print("→ 正在打开浏览器，请在 ChatCut 登录页完成授权……")
    webbrowser.open(url)

    srv = http.server.HTTPServer(("127.0.0.1", 18930), _Handler)
    srv.timeout = 300
    print("→ 等待浏览器回调 http://localhost:18930/callback …（超时 5 分钟）")
    while _auth_code is None:
        srv.handle_request()
    srv.server_close()

    print("→ 收到授权码，正在换取令牌……")
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": _auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": client_id,
        "code_verifier": verifier,
    }).encode("utf-8")
    req = urllib.request.Request(
        TOKEN_URL, data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            tok = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print("✗ 令牌交换失败:", e.code, e.read().decode("utf-8")[:300])
        return

    access_token = tok["access_token"]
    refresh_token = tok.get("refresh_token")
    expires_in = int(tok.get("expires_in", 3600))

    write_mcp(access_token)
    save_cred(client_id, refresh_token, int(time.time()), expires_in)

    print("✅ access_token 已写入 mcp.json（文件权限 600）")
    print("✅ 长效 refresh_token 已单独存入", CRED_FILE, "（权限 600）")
    print("→ 下一步：在 WorkBuddy 连接器面板找到 chatcut，点击「信任 / 启用」；")
    print("  若仍未加载工具，请重启 WorkBuddy。access_token 约 1 小时过期，")
    print("  过期后运行 chatcut_refresh.py 自动续期。")


if __name__ == "__main__":
    main()
