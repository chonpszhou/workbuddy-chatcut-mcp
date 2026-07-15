#!/usr/bin/env python3
"""
open_projects.py — 列出你的 ChatCut 项目，并输出可在 WorkBuddy 内置浏览器
直接打开的编辑器链接。

用法:
    python3 open_projects.py

输出每个项目的编辑器 URL（带 codex 启动参数）。在 WorkBuddy 中通过
「打开链接 / 预览」能力打开该 URL，即可在内置浏览器里操作，无需切到
外部浏览器。

依赖:仅 Python 标准库；需要已完成 chatcut_auth.py 授权（~/.workbuddy/mcp.json 含令牌）。
安全:本脚本只读取本地 mcp.json 调用 MCP，不打印任何 token，不写任何文件。
"""
import json
import os
import re
import sys
import urllib.request

CONFIG = os.path.expanduser("~/.workbuddy/mcp.json")


def parse(raw):
    raw = raw.strip()
    if raw.startswith("event:") or raw.startswith("data:"):
        return "\n".join(l[5:].strip() for l in raw.splitlines() if l.startswith("data:"))
    return raw


def main():
    if not os.path.exists(CONFIG):
        print("✗ 找不到 %s，请先运行 chatcut_auth.py 完成授权" % CONFIG)
        sys.exit(1)
    cfg = json.load(open(CONFIG))
    e = cfg.get("mcpServers", {}).get("chatcut")
    if not e:
        print("✗ mcp.json 中没有 chatcut 条目，请先按 README 配置")
        sys.exit(1)
    url = e["url"]
    headers = dict(e.get("headers", {}))

    sid = [None]

    def rpc(method, params, mid):
        h = dict(headers)
        h["Content-Type"] = "application/json"
        h["Accept"] = "application/json, text/event-stream"
        if sid[0]:
            h["Mcp-Session-Id"] = sid[0]
        body = {"jsonrpc": "2.0", "id": mid, "method": method, "params": params}
        req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=h)
        r = urllib.request.urlopen(req, timeout=40)
        if sid[0] is None:
            sid[0] = r.headers.get("Mcp-Session-Id") or r.headers.get("mcp-session-id")
        return json.loads(parse(r.read().decode()))

    rpc("initialize", {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "open-projects", "version": "1.0"}}, 1)
    res = rpc("tools/call", {"name": "list_projects", "arguments": {}}, 2)
    if "error" in res:
        print("✗ list_projects 调用失败:", json.dumps(res.get("error"), ensure_ascii=False)[:300])
        sys.exit(1)

    txt = "\n".join(c.get("text", "") for c in res.get("result", {}).get("content", []) if c.get("type") == "text")
    # 从返回文本提取 [Name](url) — <uuid>
    pat = re.compile(r"-\s*\[([^\]]+)\]\(([^)]+)\)\s*—\s*([0-9a-fA-F-]{36})")
    projects = pat.findall(txt)
    if not projects:
        print(txt)
        return

    print("你的 ChatCut 项目（在 WorkBuddy 内置预览面板打开）：\n")
    for name, _link, pid in projects:
        editor = ("https://app.chatcut.io/editor/%s"
                  "?chatcutLaunchClient=codex_app&chatcutLaunchSurface=ext_browser") % pid
        print("• %s" % name)
        print("  %s\n" % editor)
    print("提示：在 WorkBuddy 中打开上述链接（预览 / 打开 URL 能力），即可在内置浏览器操作；")
    print("首次打开需在面板里登录一次 ChatCut 账号（面板为独立 webview，与外部浏览器隔离）。")


if __name__ == "__main__":
    main()
