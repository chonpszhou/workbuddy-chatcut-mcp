#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatCut MCP 令牌刷新脚本（WorkBuddy 接入用）
============================================
access_token 约 1 小时过期。本脚本用 credentials.json 里的 refresh_token
换取新的 access_token，并写回 ~/.workbuddy/mcp.json 的 Authorization 头。

仅依赖 Python 标准库。

用法：
  python3 chatcut_refresh.py
"""
import json
import os
import time
import urllib.parse
import urllib.request
import urllib.error

MCP_URL = "https://api.chatcut.io/api/external-mcp/mcp"
TOKEN_URL = "https://api.chatcut.io/auth/mcp/token"

MCP_JSON = os.path.expanduser("~/.workbuddy/mcp.json")
CRED_FILE = os.path.expanduser("~/.workbuddy/chatcut/credentials.json")


def write_mcp(access_token: str):
    with open(MCP_JSON, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    entry = cfg.setdefault("mcpServers", {}).setdefault("chatcut", {})
    entry["url"] = MCP_URL
    entry.setdefault("headers", {})["x-chatcut-mcp-surface"] = "codex"
    entry["headers"]["Authorization"] = "Bearer " + access_token
    entry["disabled"] = False
    tmp = MCP_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    os.replace(tmp, MCP_JSON)
    os.chmod(MCP_JSON, 0o600)


def main():
    if not os.path.exists(CRED_FILE):
        print("✗ 未找到", CRED_FILE, "请先运行 chatcut_auth.py 完成首次授权。")
        return

    with open(CRED_FILE, "r", encoding="utf-8") as f:
        cred = json.load(f)
    client_id = cred["client_id"]
    refresh_token = cred.get("refresh_token")
    if not refresh_token:
        print("✗ credentials.json 中没有 refresh_token，请重新运行 chatcut_auth.py。")
        return

    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
    }).encode("utf-8")
    req = urllib.request.Request(
        TOKEN_URL, data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            tok = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print("✗ 刷新失败:", e.code, e.read().decode("utf-8")[:300])
        print("  多半是 refresh_token 失效，请重新运行 chatcut_auth.py。")
        return

    access_token = tok["access_token"]
    write_mcp(access_token)

    # 服务端可能轮换 refresh_token
    if "refresh_token" in tok:
        cred["refresh_token"] = tok["refresh_token"]
    cred["issued_at"] = int(time.time())
    cred["expires_in"] = int(tok.get("expires_in", 3600))
    with open(CRED_FILE, "w", encoding="utf-8") as f:
        json.dump(cred, f, indent=2, ensure_ascii=False)
    os.chmod(CRED_FILE, 0o600)

    print("✅ 已刷新 access_token 并写入 mcp.json（权限 600）。")
    print("→ 若 WorkBuddy 仍用旧令牌，请重启 WorkBuddy 或重新「信任」chatcut 连接器。")


if __name__ == "__main__":
    main()