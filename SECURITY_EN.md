# Security Policy

This project lets WorkBuddy connect to ChatCut's MCP Server. The connection relies on OAuth tokens. **This repository never stores any secrets.**

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| `main`  | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please **do not open a public issue**. Instead:

- Use GitHub **Security Advisories** (repo → Security → Advisories → "Report a vulnerability"), or
- Contact the maintainer via a private message / the email listed on the profile.

We aim to acknowledge reports within 72 hours and will coordinate a fix and disclosure timeline with you.

## What Must NEVER Be Committed

The following files / strings must **never** enter git or any public sync folder (iCloud, backup drives, etc.):

- `~/.workbuddy/chatcut/credentials.json` — contains `client_id` and a **long-lived** `refresh_token`.
- The `Authorization: Bearer <token>` injected by the script into `~/.workbuddy/mcp.json`.
- Any `__pycache__/`, `*.pyc`.

Only `mcp.json.example` (a template with **no token**) ever lives in the repo.

## Why These Must Not Be Committed

- `refresh_token` is a long-lived credential. If leaked, an attacker can impersonate your ChatCut account and burn your credits indefinitely.
- `access_token` expires in ~1 hour, but within that window it can still read and modify your projects and assets.

## Revocation Steps If Leaked

1. Re-run `chatcut_auth.py` — it performs a fresh **dynamic client registration**, issuing a new `client_id` and invalidating the old `client_id` / `refresh_token`.
2. If ChatCut exposes an "Authorized apps / sessions" management page, actively revoke the old grant.
3. Immediately check whether `~/.workbuddy/chatcut/credentials.json` or `~/.workbuddy/mcp.json` have been synced to iCloud / backup drives, and clean them up if so.
4. If a secret was **already pushed to GitHub**: a public repo's history is immutable — treat it as compromised. First do steps 1–3 to revoke, then rewrite history with `git filter-repo` or BFG and force-push. Note that rewriting cannot undo copies already scraped by third parties; **revocation is the real remedy**.

## Public Client Rationale

ChatCut uses an OAuth 2.0 **public client** (`token_endpoint_auth_method: none`, no `client_secret`). Security comes from **PKCE (S256)**: every authorization generates a one-time `code_verifier`, so even if an authorization code is intercepted it cannot be exchanged for a token. Therefore this integration needs — and holds — **no secret at all**.

## Pre-Commit Checklist

- [ ] `git status` shows **no** `credentials.json` or real `mcp.json`.
- [ ] Inside the repo, `git grep -niE "Bearer |refresh_token|client_secret|access_token"` finds **no real values** (explanatory text in scripts/docs is fine).
- [ ] `git ls-files` contains only the expected files: `README.md` / `.gitignore` / `SECURITY.md` / `LICENSE` / `mcp.json.example` / `chatcut_auth.py` / `chatcut_refresh.py` / `SKILL.md`.
- [ ] Local credential files are `chmod 600`:
      `chmod 600 ~/.workbuddy/chatcut/credentials.json ~/.workbuddy/mcp.json`
- [ ] You are committing `mcp.json.example`, **not** the real `mcp.json`.
