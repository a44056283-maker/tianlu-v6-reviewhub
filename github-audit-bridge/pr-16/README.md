# PR #16 GitHub Audit Bridge

This directory is reserved for PR #16 sanitized audit materials.

Codex prepared the full package locally at:

```text
/Volumes/TianLu_Archive/private_repos/github-audit-bridge/pr-16
```

Prepared files:

- `diff.patch`
- `l5_readonly_adapter.py`
- `console_server.patch`
- `l5-evolution.html`
- `test_l5_readonly_adapter.py`
- `test_l5_webui_static.py`
- `tests.md`
- `audit-summary.md`
- `SHA256SUMS.txt`

GitHub CLI push from this Mac is currently blocked because `gh` is not logged in and `git push` cannot read a GitHub username/token from the current macOS credential helper.

Once GitHub auth is available, push with:

```bash
cd /tmp/github-reviewhub.*/repo
git push origin main
```

Safety boundary: do not include Token, Cookie, Authorization, API Key, password, or `.env` contents in this bridge.
