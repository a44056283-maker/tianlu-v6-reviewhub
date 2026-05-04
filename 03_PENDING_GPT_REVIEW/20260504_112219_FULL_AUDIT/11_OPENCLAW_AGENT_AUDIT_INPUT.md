# OpenClaw 与智能体审计输入

生成时间: 2026-05-04 11:23:01
输出目录: /Users/luxiangnan/Desktop/Tianlu_V6_5_Workspace/00_INBOX/FULL_AUDIT_INPUT_20260504_112219

===== openclaw status =====
/opt/homebrew/bin/openclaw
OpenClaw 2026.4.29 (a448042)
Config warnings:
- plugins.entries.openclaw-weixin: plugin openclaw-weixin: channel plugin manifest declares openclaw-weixin without channelConfigs metadata; add openclaw.plugin.json#channelConfigs so config schema and setup surfaces work before runtime loads
- plugins.entries.openclaw-weixin: plugin openclaw-weixin: channel plugin manifest declares openclaw-weixin without channelConfigs metadata; add openclaw.plugin.json#channelConfigs so config schema and setup surfaces work before runtime loads
- plugins.entries.device-pair: plugin disabled (disabled in config) but config is present
- plugins.entries.claude-mem: plugin disabled (disabled in config) but config is present
▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
██░▄▄▄░██░▄▄░██░▄▄▄██░▀██░██░▄▄▀██░████░▄▄▀██░███░██
██░███░██░▀▀░██░▄▄▄██░█░█░██░█████░████░▀▀░██░█░█░██
██░▀▀▀░██░█████░▀▀▀██░██▄░██░▀▀▄██░▀▀░█░██░██▄▀▄▀▄██
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
                  🦞 OPENCLAW 🦞                    
 
┌  OpenClaw doctor
│
◇  Config warnings ────────────────────────────────────────────────────────╮
│                                                                          │
│  - plugins.entries.openclaw-weixin: plugin openclaw-weixin: channel      │
│    plugin manifest declares openclaw-weixin without channelConfigs       │
│    metadata; add openclaw.plugin.json#channelConfigs so config schema    │
│    and setup surfaces work before runtime loads                          │
│  - plugins.entries.openclaw-weixin: plugin openclaw-weixin: channel      │
│    plugin manifest declares openclaw-weixin without channelConfigs       │
│    metadata; add openclaw.plugin.json#channelConfigs so config schema    │
│    and setup surfaces work before runtime loads                          │
│  - plugins.entries.device-pair: plugin disabled (disabled in config)     │
│    but config is present                                                 │
│  - plugins.entries.claude-mem: plugin disabled (disabled in config) but  │
│    config is present                                                     │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────╯
│
◇  Doctor warnings ──────────────────────────────────────────────────────╮
│                                                                        │
│  - channels.feishu.accounts.default.allowFrom: set to ["*"] (required  │
│    by dmPolicy="open")                                                 │
│  - Run "openclaw doctor --fix" to add missing allowFrom wildcards.     │
│                                                                        │
├────────────────────────────────────────────────────────────────────────╯
│
◇  Command owner ─────────────────────────────────────────────────────────╮
│                                                                         │
│  No command owner is configured.                                        │
│  A command owner is the human operator account allowed to run           │
│  owner-only commands and approve dangerous actions, including           │
│  /diagnostics, /export-trajectory, /config, and exec approvals.         │
│  DM pairing only lets someone talk to the bot; it does not make that    │
│  sender the owner for privileged commands.                              │
│  Fix: set commands.ownerAllowFrom to your channel user id, for example  │
│  openclaw config set commands.ownerAllowFrom '["telegram:123456789"]'   │
│  Restart the gateway after changing this if it is already running.      │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────╯
│
◇  State integrity ──────────────────────────────────────────────────────╮
│                                                                        │
│  - Found 2 agent directories on disk without a matching agents.list    │
│    entry.                                                              │
│    These agents can still have sessions/auth state on disk, but        │
│    config-driven routing, identity, and model selection will ignore    │
│    them.                                                               │
│    Examples: main, tianfu                                              │
│    Restore the missing agents.list entries or remove stale dirs after  │
│    confirming they are no longer needed: ~/.openclaw/agents            │
│  - Found 819 orphan transcript files in                                │
│    ~/.openclaw/agents/tianlu/sessions.                                 │
│    These .jsonl files are no longer referenced by sessions.json, so    │
│    they are not part of any active session history.                    │
│    Doctor can archive them safely by renaming each file to             │
│    *.deleted.<timestamp>.                                              │
│    Examples: 00387696-ed10-4bf2-bca4-ff94dd8dc122.jsonl,               │
│    0047eb29-1d84-4902-8801-014540d32e37.jsonl,                         │
│    009feaf9-fdc0-4fed-80ce-858255494f73.jsonl, and 816 more            │
│                                                                        │
├────────────────────────────────────────────────────────────────────────╯
│
◇  Session locks ──────────────────────────────────────────────────────────────╮
│                                                                              │
│  - Found 1 session lock file.                                                │
│  - ~/.openclaw/agents/tianlu/sessions/da902474-3b1d-4246-87b4-8279e290b0ce.  │
│  jsonl.lock                                                                  │
│    pid=55441 (alive) age=1m2s stale=no                                       │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────╯
│
◇  Gateway service config ────────────────────────────────────────────────╮
│                                                                         │
│  - Gateway service embeds managed environment values that should load   │
│    at runtime. (inline keys: FEISHU_WEBHOOK)                            │
│  - Gateway service embeds proxy environment values that should not be   │
│    persisted. (inline keys: NO_PROXY)                                   │
│  - Gateway service PATH missing required dirs:                          │
│    /Users/luxiangnan/.nix-profile/bin                                   │
│  - Gateway service PATH includes version managers or package managers;  │
│    recommend a minimal PATH. (/Users/luxiangnan/.volta/bin,             │
│    /Users/luxiangnan/.asdf/shims,                                       │
│    /Users/luxiangnan/.fnm/aliases/default/bin,                          │
│    /Users/luxiangnan/.local/share/pnpm)                                 │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────╯
│
◇  Security ───────────────────────────────────────────────────────────────╮
│                                                                          │
│  - Feishu[main] groups: groupPolicy="open" allows any member to trigger  │
│    (mention-gated). Set channels.feishu.groupPolicy="allowlist" +        │
│    channels.feishu.groupAllowFrom to restrict senders.                   │
│  - Run: openclaw security audit --deep                                   │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────╯
│
◇  Skills status ────────────╮
│                            │
│  Eligible: 116             │
│  Missing requirements: 15  │
│  Blocked by allowlist: 0   │
│                            │
├────────────────────────────╯
│
◇  Plugins ───────╮
│                 │
│  Loaded: 9      │
│  Imported: 0    │
│  Disabled: 114  │
│  Errors: 0      │
│                 │
├─────────────────╯
│
◇  Plugin compatibility ───────────────────────────────────────────────────╮
│                                                                          │
│  - lossless-claw relies on deprecated implicit startup loading; add      │
│    activation.onStartup: true for startup work or activation.onStartup:  │
│    false for startup-lazy plugins.                                       │
│  - ocuclaw relies on deprecated implicit startup loading; add            │
│    activation.onStartup: true for startup work or activation.onStartup:  │
│    false for startup-lazy plugins.                                       │
│  - ratelimit-retry relies on deprecated implicit startup loading; add    │
│    activation.onStartup: true for startup work or activation.onStartup:  │
│    false for startup-lazy plugins.                                       │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────╯
│
◇  Plugin diagnostics ─────────────────────────────────────────────────────────╮
│                                                                              │
│  - WARN openclaw-weixin: channel plugin manifest declares                    │
│    openclaw-weixin without channelConfigs metadata; add                      │
│    openclaw.plugin.json#channelConfigs so config schema and setup            │
│    surfaces work before runtime loads                                        │
│    (/Users/luxiangnan/.openclaw/extensions/openclaw-weixin/openclaw.plugin.  │
│  json)                                                                       │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────╯
Health check failed: GatewayTransportError: gateway timeout after 10000ms
Gateway target: ws://127.0.0.1:18789
Source: local loopback
Config: /Users/luxiangnan/.openclaw/openclaw.json
Bind: loopback
[plugins] openclaw-mem0: registered (mode: platform, user: tianlu, graph: false, autoRecall: false, autoCapture: false)
│
◇  Memory search ─────────────────────────────────────────────────╮
│                                                                 │
│  No active memory plugin is registered for the current config.  │
│                                                                 │
├─────────────────────────────────────────────────────────────────╯
│
◇  Gateway port ───────────────────────────────────────────────────────────╮
│                                                                          │
│  Port 18789 is already in use.                                           │
│  - pid 55441 luxiangnan: /opt/homebrew/opt/node/bin/node                 │
│    /opt/homebrew/lib/node_modules/openclaw/dist/index.js gateway --port  │
│    18789 (127.0.0.1:18789)                                               │
│  - Gateway already running locally. Stop it (openclaw gateway stop) or   │
│    use a different port.                                                 │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────╯
│
◇  Gateway ──────────────────────╮
│                                │
│  Runtime: running (pid 55441)  │
│                                │
├────────────────────────────────╯
│
◇  Gateway ──────────────────────────────────────────────────────────╮
│                                                                    │
│  LaunchAgent loaded; stopping requires "openclaw gateway stop" or  │
│  launchctl bootout gui/$UID/ai.openclaw.gateway.                   │
│                                                                    │
├────────────────────────────────────────────────────────────────────╯
Run "openclaw doctor --fix" to apply changes.
│
└  Doctor complete.

node      55441 luxiangnan   23u  IPv4 0xcf2dab8c3fa52a14      0t0  TCP 127.0.0.1:18789 (LISTEN)
node      55441 luxiangnan   25u  IPv6 0x9d13de304750b9b6      0t0  TCP [::1]:18789 (LISTEN)

===== openclaw config model scan =====
/Users/luxiangnan/.openclaw/openclaw.json:15:      "model": {
/Users/luxiangnan/.openclaw/openclaw.json:16:        "primary": "minimax2-7/MiniMax-M2.7-highspeed"
/Users/luxiangnan/.openclaw/openclaw.json:18:      "models": {
/Users/luxiangnan/.openclaw/openclaw.json:19:        "minimax2-7/MiniMax-M2.7-highspeed": {}
/Users/luxiangnan/.openclaw/openclaw.json:30:        "model": {
/Users/luxiangnan/.openclaw/openclaw.json:31:          "primary": "minimax2-7/MiniMax-M2.7-highspeed"
/Users/luxiangnan/.openclaw/openclaw.json:55:        "model": {
/Users/luxiangnan/.openclaw/openclaw.json:56:          "primary": "minimax2-7/MiniMax-M2.7-highspeed"
/Users/luxiangnan/.openclaw/openclaw.json:70:        "model": {
/Users/luxiangnan/.openclaw/openclaw.json:71:          "primary": "minimax2-7/MiniMax-M2.7-highspeed"
/Users/luxiangnan/.openclaw/openclaw.json:86:        "model": {
/Users/luxiangnan/.openclaw/openclaw.json:87:          "primary": "minimax2-7/MiniMax-M2.7-highspeed"
/Users/luxiangnan/.openclaw/openclaw.json:102:        "model": {
/Users/luxiangnan/.openclaw/openclaw.json:103:          "primary": "minimax2-7/MiniMax-M2.7-highspeed"
/Users/luxiangnan/.openclaw/openclaw.json:125:        "model": {
/Users/luxiangnan/.openclaw/openclaw.json:126:          "primary": "minimax2-7/MiniMax-M2.7-highspeed"
/Users/luxiangnan/.openclaw/openclaw.json:140:        "model": {
/Users/luxiangnan/.openclaw/openclaw.json:141:          "primary": "minimax2-7/MiniMax-M2.7-highspeed"
/Users/luxiangnan/.openclaw/openclaw.json:155:        "model": {
/Users/luxiangnan/.openclaw/openclaw.json:156:          "primary": "minimax2-7/MiniMax-M2.7-highspeed"
/Users/luxiangnan/.openclaw/openclaw.json:170:        "model": {
/Users/luxiangnan/.openclaw/openclaw.json:171:          "primary": "minimax2-7/MiniMax-M2.7-highspeed"
/Users/luxiangnan/.openclaw/openclaw.json:185:        "model": {
/Users/luxiangnan/.openclaw/openclaw.json:186:          "primary": "minimax2-7/MiniMax-M2.7-highspeed"
/Users/luxiangnan/.openclaw/openclaw.json:200:        "model": {
/Users/luxiangnan/.openclaw/openclaw.json:201:          "primary": "minimax2-7/MiniMax-M2.7-highspeed"
/Users/luxiangnan/.openclaw/openclaw.json:215:        "model": {
/Users/luxiangnan/.openclaw/openclaw.json:216:          "primary": "minimax2-7/MiniMax-M2.7-highspeed"
/Users/luxiangnan/.openclaw/openclaw.json:228:        "model": {
/Users/luxiangnan/.openclaw/openclaw.json:229:          "primary": "minimax2-7/MiniMax-M2.7-highspeed"
/Users/luxiangnan/.openclaw/openclaw.json:245:        "id": "claudecode",
/Users/luxiangnan/.openclaw/openclaw.json:246:        "workspace": "/Users/luxiangnan/.claude/",
/Users/luxiangnan/.openclaw/openclaw.json:247:        "model": {
/Users/luxiangnan/.openclaw/openclaw.json:248:          "primary": "minimax2-7/MiniMax-M2.7-highspeed"
/Users/luxiangnan/.openclaw/openclaw.json:251:          "name": "ClaudeCode"
/Users/luxiangnan/.openclaw/openclaw.json:258:      "minimax-cn:default": {
/Users/luxiangnan/.openclaw/openclaw.json:259:        "mode": "api_key",
/Users/luxiangnan/.openclaw/openclaw.json:260:        "provider": "minimax-cn"
/Users/luxiangnan/.openclaw/openclaw.json:371:      "FEISHU_WEBHOOK": "https://open.feishu.cn/open-apis/bot/v2/hook/632c7bfc-e3a1-4ba3-b763-72bdac398b4e",
/Users/luxiangnan/.openclaw/openclaw.json:372:      "MINIMAX_API_KEY": "***REDACTED_SK***"
/Users/luxiangnan/.openclaw/openclaw.json:420:  "models": {
/Users/luxiangnan/.openclaw/openclaw.json:422:    "providers": {
/Users/luxiangnan/.openclaw/openclaw.json:423:      "minimax2-7": {
/Users/luxiangnan/.openclaw/openclaw.json:424:        "baseUrl": "https://api.minimaxi.com/v1",
/Users/luxiangnan/.openclaw/openclaw.json:425:        "api": "openai-completions",
/Users/luxiangnan/.openclaw/openclaw.json:426:        "models": [
/Users/luxiangnan/.openclaw/openclaw.json:428:            "id": "MiniMax-M2.7-highspeed",
/Users/luxiangnan/.openclaw/openclaw.json:429:            "name": "MiniMax-M2.7-highspeed",
/Users/luxiangnan/.openclaw/openclaw.json:430:            "api": "openai-completions",
/Users/luxiangnan/.openclaw/openclaw.json:446:        "apiKey": "***REDACTED***"
/Users/luxiangnan/.openclaw/openclaw.json:473:      "fsi-er-cmd-model-update": {
/Users/luxiangnan/.openclaw/openclaw.json:500:      "fsi-er-model-update": {
/Users/luxiangnan/.openclaw/openclaw.json:518:      "fsi-fa-check-model": {
/Users/luxiangnan/.openclaw/openclaw.json:536:      "fsi-fa-cmd-debug-model": {
/Users/luxiangnan/.openclaw/openclaw.json:548:      "fsi-fa-dcf-model": {
/Users/luxiangnan/.openclaw/openclaw.json:551:      "fsi-fa-lbo-model": {
/Users/luxiangnan/.openclaw/openclaw.json:575:      "fsi-ib-cmd-merger-model": {
/Users/luxiangnan/.openclaw/openclaw.json:593:      "fsi-ib-merger-model": {
/Users/luxiangnan/.openclaw/openclaw.json:797:      "claude-mem",
/Users/luxiangnan/.openclaw/openclaw.json:799:      "openrouter",
/Users/luxiangnan/.openclaw/openclaw.json:804:      "minimax"
/Users/luxiangnan/.openclaw/openclaw.json:833:          "apiKey": "***REDACTED***",
/Users/luxiangnan/.openclaw/openclaw.json:843:      "openrouter": {
/Users/luxiangnan/.openclaw/openclaw.json:846:      "claude-mem": {
/Users/luxiangnan/.openclaw/openclaw.json:859:      "minimax": {
/Users/luxiangnan/.openclaw/agents/bingbu/agent/models.json:2:  "models": {
/Users/luxiangnan/.openclaw/agents/bingbu/agent/models.json:4:    "providers": {
/Users/luxiangnan/.openclaw/agents/bingbu/agent/models.json:5:      "minimax2-7": {
/Users/luxiangnan/.openclaw/agents/bingbu/agent/models.json:6:        "baseUrl": "https://api.minimaxi.com/v1",
/Users/luxiangnan/.openclaw/agents/bingbu/agent/models.json:7:        "api": "openai-completions",
/Users/luxiangnan/.openclaw/agents/bingbu/agent/models.json:8:        "models": [
/Users/luxiangnan/.openclaw/agents/bingbu/agent/models.json:10:            "id": "MiniMax-M2.7-highspeed",
/Users/luxiangnan/.openclaw/agents/bingbu/agent/models.json:11:            "name": "MiniMax-M2.7-highspeed",
/Users/luxiangnan/.openclaw/agents/bingbu/agent/models.json:12:            "api": "openai-completions",
/Users/luxiangnan/.openclaw/agents/bingbu/agent/models.json:28:        "apiKey": "***REDACTED***"
/Users/luxiangnan/.openclaw/agents/bingbu/agent/auth-profiles.json:4:    "minimax-cn:default": {
/Users/luxiangnan/.openclaw/agents/bingbu/agent/auth-profiles.json:5:      "type": "api_key",
/Users/luxiangnan/.openclaw/agents/bingbu/agent/auth-profiles.json:6:      "provider": "minimax-cn",
/Users/luxiangnan/.openclaw/agents/bingbu/agent/auth-profiles.json:11:    "openrouter": "openrouter:default",
/Users/luxiangnan/.openclaw/agents/bingbu/agent/auth-profiles.json:12:    "minimax-cn": "minimax-cn:default",
/Users/luxiangnan/.openclaw/agents/bingbu/agent/auth-profiles.json:16:    "openrouter:default": {
/Users/luxiangnan/.openclaw/agents/bingbu/agent/auth-profiles.json:20:    "minimax-cn:default": {
/Users/luxiangnan/.openclaw/agents/zaochao/agent/models.json:2:  "models": {
/Users/luxiangnan/.openclaw/agents/zaochao/agent/models.json:4:    "providers": {
/Users/luxiangnan/.openclaw/agents/zaochao/agent/models.json:5:      "minimax2-7": {
/Users/luxiangnan/.openclaw/agents/zaochao/agent/models.json:6:        "baseUrl": "https://api.minimaxi.com/v1",
/Users/luxiangnan/.openclaw/agents/zaochao/agent/models.json:7:        "api": "openai-completions",
/Users/luxiangnan/.openclaw/agents/zaochao/agent/models.json:8:        "models": [
/Users/luxiangnan/.openclaw/agents/zaochao/agent/models.json:10:            "id": "MiniMax-M2.7-highspeed",
/Users/luxiangnan/.openclaw/agents/zaochao/agent/models.json:11:            "name": "MiniMax-M2.7-highspeed",
/Users/luxiangnan/.openclaw/agents/zaochao/agent/models.json:12:            "api": "openai-completions",
/Users/luxiangnan/.openclaw/agents/zaochao/agent/models.json:28:        "apiKey": "***REDACTED***"
/Users/luxiangnan/.openclaw/agents/zaochao/agent/auth-profiles.json:4:    "minimax-cn:default": {
/Users/luxiangnan/.openclaw/agents/zaochao/agent/auth-profiles.json:5:      "type": "api_key",
/Users/luxiangnan/.openclaw/agents/zaochao/agent/auth-profiles.json:6:      "provider": "minimax-cn",
/Users/luxiangnan/.openclaw/agents/zaochao/agent/auth-profiles.json:11:    "openrouter": "openrouter:default",
/Users/luxiangnan/.openclaw/agents/zaochao/agent/auth-profiles.json:12:    "minimax-cn": "minimax-cn:default",
/Users/luxiangnan/.openclaw/agents/zaochao/agent/auth-profiles.json:16:    "openrouter:default": {
/Users/luxiangnan/.openclaw/agents/zaochao/agent/auth-profiles.json:20:    "minimax-cn:default": {
/Users/luxiangnan/.openclaw/agents/libu_hr/agent/models.json:2:  "models": {
/Users/luxiangnan/.openclaw/agents/libu_hr/agent/models.json:4:    "providers": {
/Users/luxiangnan/.openclaw/agents/libu_hr/agent/models.json:5:      "minimax2-7": {
/Users/luxiangnan/.openclaw/agents/libu_hr/agent/models.json:6:        "baseUrl": "https://api.minimaxi.com/v1",
/Users/luxiangnan/.openclaw/agents/libu_hr/agent/models.json:7:        "api": "openai-completions",
/Users/luxiangnan/.openclaw/agents/libu_hr/agent/models.json:8:        "models": [
/Users/luxiangnan/.openclaw/agents/libu_hr/agent/models.json:10:            "id": "MiniMax-M2.7-highspeed",
/Users/luxiangnan/.openclaw/agents/libu_hr/agent/models.json:11:            "name": "MiniMax-M2.7-highspeed",
/Users/luxiangnan/.openclaw/agents/libu_hr/agent/models.json:12:            "api": "openai-completions",
/Users/luxiangnan/.openclaw/agents/libu_hr/agent/models.json:28:        "apiKey": "***REDACTED***"
/Users/luxiangnan/.openclaw/agents/libu_hr/agent/auth-profiles.json:4:    "minimax-cn:default": {
/Users/luxiangnan/.openclaw/agents/libu_hr/agent/auth-profiles.json:5:      "type": "api_key",
/Users/luxiangnan/.openclaw/agents/libu_hr/agent/auth-profiles.json:6:      "provider": "minimax-cn",
/Users/luxiangnan/.openclaw/agents/libu_hr/agent/auth-profiles.json:11:    "openrouter": "openrouter:default",
/Users/luxiangnan/.openclaw/agents/libu_hr/agent/auth-profiles.json:12:    "minimax-cn": "minimax-cn:default",
/Users/luxiangnan/.openclaw/agents/libu_hr/agent/auth-profiles.json:16:    "openrouter:default": {
/Users/luxiangnan/.openclaw/agents/libu_hr/agent/auth-profiles.json:20:    "minimax-cn:default": {
/Users/luxiangnan/.openclaw/agents/zhongshu/agent/models.json:2:  "models": {
/Users/luxiangnan/.openclaw/agents/zhongshu/agent/models.json:4:    "providers": {
/Users/luxiangnan/.openclaw/agents/zhongshu/agent/models.json:5:      "minimax2-7": {
/Users/luxiangnan/.openclaw/agents/zhongshu/agent/models.json:6:        "baseUrl": "https://api.minimaxi.com/v1",
/Users/luxiangnan/.openclaw/agents/zhongshu/agent/models.json:7:        "api": "openai-completions",
/Users/luxiangnan/.openclaw/agents/zhongshu/agent/models.json:8:        "models": [
/Users/luxiangnan/.openclaw/agents/zhongshu/agent/models.json:10:            "id": "MiniMax-M2.7-highspeed",
/Users/luxiangnan/.openclaw/agents/zhongshu/agent/models.json:11:            "name": "MiniMax-M2.7-highspeed",
/Users/luxiangnan/.openclaw/agents/zhongshu/agent/models.json:12:            "api": "openai-completions",
/Users/luxiangnan/.openclaw/agents/zhongshu/agent/models.json:28:        "apiKey": "***REDACTED***"
/Users/luxiangnan/.openclaw/agents/zhongshu/agent/auth-profiles.json:4:    "minimax-cn:default": {
/Users/luxiangnan/.openclaw/agents/zhongshu/agent/auth-profiles.json:5:      "type": "api_key",
/Users/luxiangnan/.openclaw/agents/zhongshu/agent/auth-profiles.json:6:      "provider": "minimax-cn",
/Users/luxiangnan/.openclaw/agents/zhongshu/agent/auth-profiles.json:11:    "openrouter": "openrouter:default",
/Users/luxiangnan/.openclaw/agents/zhongshu/agent/auth-profiles.json:12:    "minimax-cn": "minimax-cn:default",
/Users/luxiangnan/.openclaw/agents/zhongshu/agent/auth-profiles.json:16:    "openrouter:default": {
/Users/luxiangnan/.openclaw/agents/zhongshu/agent/auth-profiles.json:20:    "minimax-cn:default": {
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2:  "agent:claudecode:main": {
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:9:    "sessionFile": "/Users/luxiangnan/.openclaw/agents/claudecode/sessions/f92074f9-874e-4a4e-9ed9-103587002013.jsonl",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:12:      "prompt": "Remote macOS node available (TianLu-Mac). Run macOS-only skills via exec host=node on that node.\n⚠️ Skills catalog using compact format (descriptions omitted). Run `openclaw skills check` to audit.\n\n\nThe following skills provide specialized instructions for specific tasks.\nUse the read tool to load a skill's file when the task matches its name.\nWhen a skill file references a relative path, resolve it against the skill directory (parent of SKILL.md / dirname of the path) and use that absolute path in tool commands.\n\n<available_skills>\n  <skill>\n    <name>1password</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/1password/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>acn</name>\n    <location>~/.openclaw/skills/agent-collaboration-network/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>api-design</name>\n    <location>~/.claude/.agents/skills/api-design/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>apple-notes</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/apple-notes/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>apple-reminders</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/apple-reminders/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>arc-skill-gitops</name>\n    <location>~/.openclaw/skills/arc-skill-gitops/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>article-writing</name>\n    <location>~/.claude/skills/article-writing/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>backend-patterns</name>\n    <location>~/.claude/skills/backend-patterns/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>bear-notes</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/bear-notes/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>blogwatcher</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/blogwatcher/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>blucli</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/blucli/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>camsnap</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/camsnap/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>claude-api</name>\n    <location>~/.claude/skills/claude-api/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>clawhub</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/clawhub/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>clickhouse-io</name>\n    <location>~/.claude/skills/clickhouse-io/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>Codex-api</name>\n    <location>~/.agents/skills/claude-api/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>coding-standards</name>\n    <location>~/.claude/skills/coding-standards/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>content-engine</name>\n    <location>~/.claude/skills/content-engine/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>continuous-learning</name>\n    <location>~/.claude/skills/continuous-learning/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>continuous-learning-v2</name>\n    <location>~/.claude/skills/continuous-learning-v2/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>crosspost</name>\n    <location>~/.claude/skills/crosspost/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>deep-research</name>\n    <location>~/.claude/skills/deep-research/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>django-patterns</name>\n    <location>~/.claude/skills/django-patterns/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>django-security</name>\n    <location>~/.claude/skills/django-security/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>django-tdd</name>\n    <location>~/.claude/skills/django-tdd/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>django-verification</name>\n    <location>~/.claude/skills/django-verification/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>dmux-workflows</name>\n    <location>~/.claude/skills/dmux-workflows/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>e2e-testing</name>\n    <location>~/.claude/.agents/skills/e2e-testing/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>eightctl</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/eightctl/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>eval-harness</name>\n    <location>~/.claude/skills/eval-harness/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>exa-search</name>\n    <location>~/.claude/skills/exa-search/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>fal-ai-media</name>\n    <location>~/.claude/skills/fal-ai-media/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>feishu-doc</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/dist/extensions/feishu/skills/feishu-doc/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>feishu-drive</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/dist/extensions/feishu/skills/feishu-drive/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>feishu-perm</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/dist/extensions/feishu/skills/feishu-perm/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>feishu-wiki</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/dist/extensions/feishu/skills/feishu-wiki/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>frontend-patterns</name>\n    <location>~/.claude/skills/frontend-patterns/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>frontend-slides</name>\n    <location>~/.claude/skills/frontend-slides/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>gemini</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/gemini/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>gh-issues</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/gh-issues/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>gifgrep</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/gifgrep/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>github</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/github/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>gog</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/gog/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>golang-patterns</name>\n    <location>~/.claude/skills/golang-patterns/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>golang-testing</name>\n    <location>~/.claude/skills/golang-testing/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>healthcheck</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/healthcheck/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>himalaya</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/himalaya/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>imsg</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/imsg/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>investor-materials</name>\n    <location>~/.claude/skills/investor-materials/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>investor-outreach</name>\n    <location>~/.claude/skills/investor-outreach/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>iterative-retrieval</name>\n    <location>~/.claude/skills/iterative-retrieval/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>java-coding-standards</name>\n    <location>~/.claude/skills/java-coding-standards/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>jpa-patterns</name>\n    <location>~/.claude/skills/jpa-patterns/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>market-research</name>\n    <location>~/.claude/skills/market-research/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>mcporter</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/mcporter/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>nano-pdf</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/nano-pdf/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>node-connect</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/node-connect/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>obsidian</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/obsidian/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>openai-whisper</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/openai-whisper/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>openhue</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/openhue/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>oracle</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/oracle/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>ordercli</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/ordercli/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>peekaboo</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/peekaboo/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>postgres-patterns</name>\n    <location>~/.claude/skills/postgres-patterns/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>python-patterns</name>\n    <location>~/.claude/skills/python-patterns/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>python-testing</name>\n    <location>~/.claude/skills/python-testing/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>security-review</name>\n    <location>~/.claude/skills/security-review/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>security-scan</name>\n    <location>~/.claude/skills/security-scan/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>skill-creator</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/skill-creator/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>songsee</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/songsee/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>sonoscli</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/sonoscli/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>source-command-aside</name>\n    <location>~/.agents/skills/source-command-aside/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>source-command-claw</name>\n    <location>~/.agents/skills/source-command-claw/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>source-command-e2e</name>\n    <location>~/.agents/skills/source-command-e2e/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>source-command-evolve</name>\n    <location>~/.agents/skills/source-command-evolve/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>source-command-go-build</name>\n    <location>~/.agents/skills/source-command-go-build/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>source-command-go-review</name>\n    <location>~/.agents/skills/source-command-go-review/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>source-command-gradle-build</name>\n    <location>~/.agents/skills/source-command-gradle-build/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>source-command-instinct-export</name>\n    <location>~/.agents/skills/source-command-instinct-export/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>source-command-instinct-import</name>\n    <location>~/.agents/skills/source-command-instinct-import/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>source-command-instinct-status</name>\n    <location>~/.agents/skills/source-command-instinct-status/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>source-command-kotlin-build</name>\n    <location>~/.agents/skills/source-command-kotlin-build/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>source-command-kotlin-test</name>\n    <location>~/.agents/skills/source-command-kotlin-test/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>source-command-learn-eval</name>\n    <location>~/.agents/skills/source-command-learn-eval/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>source-command-plan</name>\n    <location>~/.agents/skills/source-command-plan/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>source-command-projects</name>\n    <location>~/.agents/skills/source-command-projects/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>source-command-promote</name>\n    <location>~/.agents/skills/source-command-promote/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>source-command-python-review</name>\n    <location>~/.agents/skills/source-command-python-review/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>source-command-resume-session</name>\n    <location>~/.agents/skills/source-command-resume-session/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>source-command-save-session</name>\n    <location>~/.agents/skills/source-command-save-session/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>source-command-setup-pm</name>\n    <location>~/.agents/skills/source-command-setup-pm/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>source-command-skill-create</name>\n    <location>~/.agents/skills/source-command-skill-create/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>source-command-tdd</name>\n    <location>~/.agents/skills/source-command-tdd/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>springboot-patterns</name>\n    <location>~/.claude/skills/springboot-patterns/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>springboot-security</name>\n    <location>~/.claude/skills/springboot-security/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>springboot-tdd</name>\n    <location>~/.claude/skills/springboot-tdd/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>springboot-verification</name>\n    <location>~/.claude/skills/springboot-verification/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>strategic-compact</name>\n    <location>~/.claude/skills/strategic-compact/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>summarize</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/summarize/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>taskflow</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/taskflow/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>taskflow-inbox-triage</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/taskflow-inbox-triage/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>tdd-workflow</name>\n    <location>~/.claude/skills/tdd-workflow/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>things-mac</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/things-mac/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>tianlu-evolution</name>\n    <location>~/.openclaw/skills/tianlu-evolution/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>tianyan-ai-v50</name>\n    <location>~/.claude/skills/tianyan-ai-v50/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>trust-verifier</name>\n    <location>~/.openclaw/skills/arc-trust-verifier/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>verification-loop</name>\n    <location>~/.claude/skills/verification-loop/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>video-editing</name>\n    <location>~/.claude/skills/video-editing/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>video-frames</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/video-frames/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>videodb</name>\n    <location>~/.claude/skills/videodb/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>wacli</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/wacli/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>weather</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/weather/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>x-api</name>\n    <location>~/.claude/skills/x-api/SKILL.md</location>\n  </skill>\n  <skill>\n    <name>xurl</name>\n    <location>/opt/homebrew/lib/node_modules/openclaw/skills/xurl/SKILL.md</location>\n  </skill>\n</available_skills>",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:22:          "name": "api-design"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:59:          "name": "claude-api"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:69:          "name": "Codex-api"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:385:          "name": "x-api"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:406:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:421:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:424:          "name": "api-design",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:425:          "description": "REST API design patterns including resource naming, status codes, pagination, filtering, error responses, versioning, and rate limiting for production APIs.",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:426:          "filePath": "/Users/luxiangnan/.claude/.agents/skills/api-design/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:427:          "baseDir": "/Users/luxiangnan/.claude/.agents/skills/api-design",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:430:            "path": "/Users/luxiangnan/.claude/.agents/skills/api-design/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:434:            "baseDir": "/Users/luxiangnan/.claude/.agents/skills/api-design"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:436:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:451:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:466:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:481:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:486:          "filePath": "/Users/luxiangnan/.claude/skills/article-writing/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:487:          "baseDir": "/Users/luxiangnan/.claude/skills/article-writing",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:490:            "path": "/Users/luxiangnan/.claude/skills/article-writing/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:494:            "baseDir": "/Users/luxiangnan/.claude/skills/article-writing"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:496:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:500:          "description": "Backend architecture patterns, API design, database optimization, and server-side best practices for Node.js, Express, and Next.js API routes.",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:501:          "filePath": "/Users/luxiangnan/.claude/skills/backend-patterns/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:502:          "baseDir": "/Users/luxiangnan/.claude/skills/backend-patterns",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:505:            "path": "/Users/luxiangnan/.claude/skills/backend-patterns/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:509:            "baseDir": "/Users/luxiangnan/.claude/skills/backend-patterns"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:511:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:526:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:541:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:556:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:571:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:574:          "name": "claude-api",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:575:          "description": "Anthropic Claude API patterns for Python and TypeScript. Covers Messages API, streaming, tool use, vision, extended thinking, batches, prompt caching, and Claude Agent SDK. Use when building applications with the Claude API or Anthropic SDKs.",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:576:          "filePath": "/Users/luxiangnan/.claude/skills/claude-api/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:577:          "baseDir": "/Users/luxiangnan/.claude/skills/claude-api",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:580:            "path": "/Users/luxiangnan/.claude/skills/claude-api/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:584:            "baseDir": "/Users/luxiangnan/.claude/skills/claude-api"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:586:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:601:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:606:          "filePath": "/Users/luxiangnan/.claude/skills/clickhouse-io/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:607:          "baseDir": "/Users/luxiangnan/.claude/skills/clickhouse-io",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:610:            "path": "/Users/luxiangnan/.claude/skills/clickhouse-io/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:614:            "baseDir": "/Users/luxiangnan/.claude/skills/clickhouse-io"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:616:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:619:          "name": "Codex-api",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:620:          "description": "Anthropic Codex API patterns for Python and TypeScript. Covers Messages API, streaming, tool use, vision, extended thinking, batches, prompt caching, and Codex Agent SDK. Use when building applications with the Codex API or Anthropic SDKs.",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:621:          "filePath": "/Users/luxiangnan/.agents/skills/claude-api/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:622:          "baseDir": "/Users/luxiangnan/.agents/skills/claude-api",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:625:            "path": "/Users/luxiangnan/.agents/skills/claude-api/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:629:            "baseDir": "/Users/luxiangnan/.agents/skills/claude-api"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:631:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:636:          "filePath": "/Users/luxiangnan/.claude/skills/coding-standards/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:637:          "baseDir": "/Users/luxiangnan/.claude/skills/coding-standards",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:640:            "path": "/Users/luxiangnan/.claude/skills/coding-standards/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:644:            "baseDir": "/Users/luxiangnan/.claude/skills/coding-standards"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:646:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:651:          "filePath": "/Users/luxiangnan/.claude/skills/content-engine/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:652:          "baseDir": "/Users/luxiangnan/.claude/skills/content-engine",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:655:            "path": "/Users/luxiangnan/.claude/skills/content-engine/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:659:            "baseDir": "/Users/luxiangnan/.claude/skills/content-engine"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:661:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:665:          "description": "Automatically extract reusable patterns from Claude Code sessions and save them as learned skills for future use.",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:666:          "filePath": "/Users/luxiangnan/.claude/skills/continuous-learning/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:667:          "baseDir": "/Users/luxiangnan/.claude/skills/continuous-learning",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:670:            "path": "/Users/luxiangnan/.claude/skills/continuous-learning/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:674:            "baseDir": "/Users/luxiangnan/.claude/skills/continuous-learning"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:676:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:681:          "filePath": "/Users/luxiangnan/.claude/skills/continuous-learning-v2/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:682:          "baseDir": "/Users/luxiangnan/.claude/skills/continuous-learning-v2",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:685:            "path": "/Users/luxiangnan/.claude/skills/continuous-learning-v2/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:689:            "baseDir": "/Users/luxiangnan/.claude/skills/continuous-learning-v2"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:691:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:696:          "filePath": "/Users/luxiangnan/.claude/skills/crosspost/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:697:          "baseDir": "/Users/luxiangnan/.claude/skills/crosspost",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:700:            "path": "/Users/luxiangnan/.claude/skills/crosspost/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:704:            "baseDir": "/Users/luxiangnan/.claude/skills/crosspost"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:706:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:711:          "filePath": "/Users/luxiangnan/.claude/skills/deep-research/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:712:          "baseDir": "/Users/luxiangnan/.claude/skills/deep-research",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:715:            "path": "/Users/luxiangnan/.claude/skills/deep-research/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:719:            "baseDir": "/Users/luxiangnan/.claude/skills/deep-research"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:721:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:725:          "description": "Django architecture patterns, REST API design with DRF, ORM best practices, caching, signals, middleware, and production-grade Django apps.",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:726:          "filePath": "/Users/luxiangnan/.claude/skills/django-patterns/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:727:          "baseDir": "/Users/luxiangnan/.claude/skills/django-patterns",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:730:            "path": "/Users/luxiangnan/.claude/skills/django-patterns/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:734:            "baseDir": "/Users/luxiangnan/.claude/skills/django-patterns"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:736:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:741:          "filePath": "/Users/luxiangnan/.claude/skills/django-security/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:742:          "baseDir": "/Users/luxiangnan/.claude/skills/django-security",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:745:            "path": "/Users/luxiangnan/.claude/skills/django-security/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:749:            "baseDir": "/Users/luxiangnan/.claude/skills/django-security"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:751:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:755:          "description": "Django testing strategies with pytest-django, TDD methodology, factory_boy, mocking, coverage, and testing Django REST Framework APIs.",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:756:          "filePath": "/Users/luxiangnan/.claude/skills/django-tdd/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:757:          "baseDir": "/Users/luxiangnan/.claude/skills/django-tdd",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:760:            "path": "/Users/luxiangnan/.claude/skills/django-tdd/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:764:            "baseDir": "/Users/luxiangnan/.claude/skills/django-tdd"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:766:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:771:          "filePath": "/Users/luxiangnan/.claude/skills/django-verification/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:772:          "baseDir": "/Users/luxiangnan/.claude/skills/django-verification",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:775:            "path": "/Users/luxiangnan/.claude/skills/django-verification/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:779:            "baseDir": "/Users/luxiangnan/.claude/skills/django-verification"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:781:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:785:          "description": "Multi-agent orchestration using dmux (tmux pane manager for AI agents). Patterns for parallel agent workflows across Claude Code, Codex, OpenCode, and other harnesses. Use when running multiple agent sessions in parallel or coordinating multi-agent development workflows.",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:786:          "filePath": "/Users/luxiangnan/.claude/skills/dmux-workflows/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:787:          "baseDir": "/Users/luxiangnan/.claude/skills/dmux-workflows",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:790:            "path": "/Users/luxiangnan/.claude/skills/dmux-workflows/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:794:            "baseDir": "/Users/luxiangnan/.claude/skills/dmux-workflows"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:796:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:800:          "description": "Playwright E2E testing patterns, Page Object Model, configuration, CI/CD integration, artifact management, and flaky test strategies.",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:801:          "filePath": "/Users/luxiangnan/.claude/.agents/skills/e2e-testing/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:802:          "baseDir": "/Users/luxiangnan/.claude/.agents/skills/e2e-testing",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:805:            "path": "/Users/luxiangnan/.claude/.agents/skills/e2e-testing/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:809:            "baseDir": "/Users/luxiangnan/.claude/.agents/skills/e2e-testing"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:811:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:826:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:830:          "description": "Formal evaluation framework for Claude Code sessions implementing eval-driven development (EDD) principles",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:831:          "filePath": "/Users/luxiangnan/.claude/skills/eval-harness/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:832:          "baseDir": "/Users/luxiangnan/.claude/skills/eval-harness",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:835:            "path": "/Users/luxiangnan/.claude/skills/eval-harness/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:839:            "baseDir": "/Users/luxiangnan/.claude/skills/eval-harness"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:841:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:846:          "filePath": "/Users/luxiangnan/.claude/skills/exa-search/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:847:          "baseDir": "/Users/luxiangnan/.claude/skills/exa-search",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:850:            "path": "/Users/luxiangnan/.claude/skills/exa-search/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:854:            "baseDir": "/Users/luxiangnan/.claude/skills/exa-search"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:856:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:861:          "filePath": "/Users/luxiangnan/.claude/skills/fal-ai-media/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:862:          "baseDir": "/Users/luxiangnan/.claude/skills/fal-ai-media",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:865:            "path": "/Users/luxiangnan/.claude/skills/fal-ai-media/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:869:            "baseDir": "/Users/luxiangnan/.claude/skills/fal-ai-media"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:871:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:886:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:901:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:916:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:931:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:936:          "filePath": "/Users/luxiangnan/.claude/skills/frontend-patterns/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:937:          "baseDir": "/Users/luxiangnan/.claude/skills/frontend-patterns",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:940:            "path": "/Users/luxiangnan/.claude/skills/frontend-patterns/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:944:            "baseDir": "/Users/luxiangnan/.claude/skills/frontend-patterns"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:946:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:951:          "filePath": "/Users/luxiangnan/.claude/skills/frontend-slides/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:952:          "baseDir": "/Users/luxiangnan/.claude/skills/frontend-slides",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:955:            "path": "/Users/luxiangnan/.claude/skills/frontend-slides/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:959:            "baseDir": "/Users/luxiangnan/.claude/skills/frontend-slides"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:961:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:976:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:991:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:995:          "description": "Search GIF providers with CLI/TUI, download results, and extract stills/sheets.",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1006:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1010:          "description": "Use gh for GitHub issues, PR status, CI/logs, comments, reviews, releases, and API queries.",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1021:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1036:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1041:          "filePath": "/Users/luxiangnan/.claude/skills/golang-patterns/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1042:          "baseDir": "/Users/luxiangnan/.claude/skills/golang-patterns",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1045:            "path": "/Users/luxiangnan/.claude/skills/golang-patterns/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1049:            "baseDir": "/Users/luxiangnan/.claude/skills/golang-patterns"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1051:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1056:          "filePath": "/Users/luxiangnan/.claude/skills/golang-testing/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1057:          "baseDir": "/Users/luxiangnan/.claude/skills/golang-testing",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1060:            "path": "/Users/luxiangnan/.claude/skills/golang-testing/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1064:            "baseDir": "/Users/luxiangnan/.claude/skills/golang-testing"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1066:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1081:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1096:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1111:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1115:          "description": "Create and update pitch decks, one-pagers, investor memos, accelerator applications, financial models, and fundraising materials. Use when the user needs investor-facing documents, projections, use-of-funds tables, milestone plans, or materials that must stay internally consistent across multiple fundraising assets.",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1116:          "filePath": "/Users/luxiangnan/.claude/skills/investor-materials/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1117:          "baseDir": "/Users/luxiangnan/.claude/skills/investor-materials",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1120:            "path": "/Users/luxiangnan/.claude/skills/investor-materials/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1124:            "baseDir": "/Users/luxiangnan/.claude/skills/investor-materials"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1126:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1131:          "filePath": "/Users/luxiangnan/.claude/skills/investor-outreach/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1132:          "baseDir": "/Users/luxiangnan/.claude/skills/investor-outreach",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1135:            "path": "/Users/luxiangnan/.claude/skills/investor-outreach/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1139:            "baseDir": "/Users/luxiangnan/.claude/skills/investor-outreach"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1141:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1146:          "filePath": "/Users/luxiangnan/.claude/skills/iterative-retrieval/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1147:          "baseDir": "/Users/luxiangnan/.claude/skills/iterative-retrieval",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1150:            "path": "/Users/luxiangnan/.claude/skills/iterative-retrieval/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1154:            "baseDir": "/Users/luxiangnan/.claude/skills/iterative-retrieval"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1156:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1161:          "filePath": "/Users/luxiangnan/.claude/skills/java-coding-standards/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1162:          "baseDir": "/Users/luxiangnan/.claude/skills/java-coding-standards",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1165:            "path": "/Users/luxiangnan/.claude/skills/java-coding-standards/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1169:            "baseDir": "/Users/luxiangnan/.claude/skills/java-coding-standards"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1171:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1176:          "filePath": "/Users/luxiangnan/.claude/skills/jpa-patterns/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1177:          "baseDir": "/Users/luxiangnan/.claude/skills/jpa-patterns",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1180:            "path": "/Users/luxiangnan/.claude/skills/jpa-patterns/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1184:            "baseDir": "/Users/luxiangnan/.claude/skills/jpa-patterns"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1186:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1191:          "filePath": "/Users/luxiangnan/.claude/skills/market-research/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1192:          "baseDir": "/Users/luxiangnan/.claude/skills/market-research",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1195:            "path": "/Users/luxiangnan/.claude/skills/market-research/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1199:            "baseDir": "/Users/luxiangnan/.claude/skills/market-research"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1201:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1216:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1231:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1246:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1261:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1265:          "description": "Local speech-to-text with the Whisper CLI (no API key).",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1276:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1291:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1295:          "description": "Use oracle CLI to bundle prompts and files for second-model debugging, refactor, design, or review checks.",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1306:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1321:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1336:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1341:          "filePath": "/Users/luxiangnan/.claude/skills/postgres-patterns/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1342:          "baseDir": "/Users/luxiangnan/.claude/skills/postgres-patterns",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1345:            "path": "/Users/luxiangnan/.claude/skills/postgres-patterns/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1349:            "baseDir": "/Users/luxiangnan/.claude/skills/postgres-patterns"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1351:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1356:          "filePath": "/Users/luxiangnan/.claude/skills/python-patterns/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1357:          "baseDir": "/Users/luxiangnan/.claude/skills/python-patterns",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1360:            "path": "/Users/luxiangnan/.claude/skills/python-patterns/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1364:            "baseDir": "/Users/luxiangnan/.claude/skills/python-patterns"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1366:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1371:          "filePath": "/Users/luxiangnan/.claude/skills/python-testing/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1372:          "baseDir": "/Users/luxiangnan/.claude/skills/python-testing",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1375:            "path": "/Users/luxiangnan/.claude/skills/python-testing/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1379:            "baseDir": "/Users/luxiangnan/.claude/skills/python-testing"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1381:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1385:          "description": "Use this skill when adding authentication, handling user input, working with secrets, creating API endpoints, or implementing payment/sensitive features. Provides comprehensive security checklist and patterns.",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1386:          "filePath": "/Users/luxiangnan/.claude/skills/security-review/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1387:          "baseDir": "/Users/luxiangnan/.claude/skills/security-review",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1390:            "path": "/Users/luxiangnan/.claude/skills/security-review/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1394:            "baseDir": "/Users/luxiangnan/.claude/skills/security-review"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1396:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1400:          "description": "Scan your Claude Code configuration (.claude/ directory) for security vulnerabilities, misconfigurations, and injection risks using AgentShield. Checks CLAUDE.md, settings.json, MCP servers, hooks, and agent definitions.",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1401:          "filePath": "/Users/luxiangnan/.claude/skills/security-scan/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1402:          "baseDir": "/Users/luxiangnan/.claude/skills/security-scan",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1405:            "path": "/Users/luxiangnan/.claude/skills/security-scan/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1409:            "baseDir": "/Users/luxiangnan/.claude/skills/security-scan"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1411:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1426:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1441:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1456:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1471:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1475:          "description": "Start NanoClaw v2 — ECC's persistent, zero-dependency REPL with model routing, skill hot-load, branching, compaction, export, and metrics.",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1486:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1501:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1516:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1531:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1546:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1561:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1576:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1591:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1606:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1621:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1636:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1651:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1666:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1681:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1696:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1711:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1726:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1741:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1756:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1771:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1786:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1790:          "description": "Spring Boot architecture patterns, REST API design, layered services, data access, caching, async processing, and logging. Use for Java Spring Boot backend work.",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1791:          "filePath": "/Users/luxiangnan/.claude/skills/springboot-patterns/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1792:          "baseDir": "/Users/luxiangnan/.claude/skills/springboot-patterns",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1795:            "path": "/Users/luxiangnan/.claude/skills/springboot-patterns/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1799:            "baseDir": "/Users/luxiangnan/.claude/skills/springboot-patterns"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1801:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1806:          "filePath": "/Users/luxiangnan/.claude/skills/springboot-security/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1807:          "baseDir": "/Users/luxiangnan/.claude/skills/springboot-security",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1810:            "path": "/Users/luxiangnan/.claude/skills/springboot-security/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1814:            "baseDir": "/Users/luxiangnan/.claude/skills/springboot-security"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1816:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1821:          "filePath": "/Users/luxiangnan/.claude/skills/springboot-tdd/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1822:          "baseDir": "/Users/luxiangnan/.claude/skills/springboot-tdd",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1825:            "path": "/Users/luxiangnan/.claude/skills/springboot-tdd/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1829:            "baseDir": "/Users/luxiangnan/.claude/skills/springboot-tdd"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1831:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1836:          "filePath": "/Users/luxiangnan/.claude/skills/springboot-verification/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1837:          "baseDir": "/Users/luxiangnan/.claude/skills/springboot-verification",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1840:            "path": "/Users/luxiangnan/.claude/skills/springboot-verification/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1844:            "baseDir": "/Users/luxiangnan/.claude/skills/springboot-verification"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1846:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1851:          "filePath": "/Users/luxiangnan/.claude/skills/strategic-compact/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1852:          "baseDir": "/Users/luxiangnan/.claude/skills/strategic-compact",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1855:            "path": "/Users/luxiangnan/.claude/skills/strategic-compact/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1859:            "baseDir": "/Users/luxiangnan/.claude/skills/strategic-compact"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1861:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1876:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1891:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1906:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1911:          "filePath": "/Users/luxiangnan/.claude/skills/tdd-workflow/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1912:          "baseDir": "/Users/luxiangnan/.claude/skills/tdd-workflow",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1915:            "path": "/Users/luxiangnan/.claude/skills/tdd-workflow/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1919:            "baseDir": "/Users/luxiangnan/.claude/skills/tdd-workflow"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1921:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1936:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1940:          "description": "天禄自我进化系统 - 基于 Claude Code 架构的记忆管理、预算追踪、反思与安全检查。当需要：(1)记录重要事件到记忆系统 (2)检查当前预算状态 (3)进行操作前安全确认 (4)反思提炼规律 (5)执行每日/会话复盘 时触发。",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1951:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1956:          "filePath": "/Users/luxiangnan/.claude/skills/tianyan-ai-v50/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1957:          "baseDir": "/Users/luxiangnan/.claude/skills/tianyan-ai-v50",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1960:            "path": "/Users/luxiangnan/.claude/skills/tianyan-ai-v50/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1964:            "baseDir": "/Users/luxiangnan/.claude/skills/tianyan-ai-v50"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1966:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1981:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1985:          "description": "A comprehensive verification system for Claude Code sessions.",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1986:          "filePath": "/Users/luxiangnan/.claude/skills/verification-loop/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1987:          "baseDir": "/Users/luxiangnan/.claude/skills/verification-loop",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1990:            "path": "/Users/luxiangnan/.claude/skills/verification-loop/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1994:            "baseDir": "/Users/luxiangnan/.claude/skills/verification-loop"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:1996:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2001:          "filePath": "/Users/luxiangnan/.claude/skills/video-editing/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2002:          "baseDir": "/Users/luxiangnan/.claude/skills/video-editing",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2005:            "path": "/Users/luxiangnan/.claude/skills/video-editing/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2009:            "baseDir": "/Users/luxiangnan/.claude/skills/video-editing"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2011:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2026:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2031:          "filePath": "/Users/luxiangnan/.claude/skills/videodb/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2032:          "baseDir": "/Users/luxiangnan/.claude/skills/videodb",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2035:            "path": "/Users/luxiangnan/.claude/skills/videodb/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2039:            "baseDir": "/Users/luxiangnan/.claude/skills/videodb"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2041:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2056:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2071:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2074:          "name": "x-api",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2075:          "description": "X/Twitter API integration for posting tweets, threads, reading timelines, search, and analytics. Covers OAuth auth patterns, rate limits, and platform-native content posting. Use when the user wants to interact with X programmatically.",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2076:          "filePath": "/Users/luxiangnan/.claude/skills/x-api/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2077:          "baseDir": "/Users/luxiangnan/.claude/skills/x-api",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2080:            "path": "/Users/luxiangnan/.claude/skills/x-api/SKILL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2084:            "baseDir": "/Users/luxiangnan/.claude/skills/x-api"
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2086:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2090:          "description": "Use xurl for authenticated X API posts, replies, search, DMs, media upload, followers, or raw v2 calls.",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2101:          "disableModelInvocation": false
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2114:      "provider": "webchat",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2118:    "modelProvider": "minimax2-7",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2119:    "model": "MiniMax-M2.7-highspeed",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2125:      "sessionKey": "agent:claudecode:main",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2126:      "provider": "minimax2-7",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2127:      "model": "MiniMax-M2.7-highspeed",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2128:      "workspaceDir": "/Users/luxiangnan/.claude",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2150:          "path": "/Users/luxiangnan/.claude/AGENTS.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2158:          "path": "/Users/luxiangnan/.claude/SOUL.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2166:          "path": "/Users/luxiangnan/.claude/TOOLS.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2174:          "path": "/Users/luxiangnan/.claude/IDENTITY.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2182:          "path": "/Users/luxiangnan/.claude/USER.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2190:          "path": "/Users/luxiangnan/.claude/HEARTBEAT.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2198:          "path": "/Users/luxiangnan/.claude/BOOTSTRAP.md",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2217:            "name": "api-design",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2257:            "name": "claude-api",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2269:            "name": "Codex-api",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/sessions.json:2657:            "name": "x-api",
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/f92074f9-874e-4a4e-9ed9-103587002013.jsonl:1:{"type":"session","version":3,"id":"f92074f9-874e-4a4e-9ed9-103587002013","timestamp":"2026-05-04T01:17:48.626Z","cwd":"/Users/luxiangnan/.claude"}
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/f92074f9-874e-4a4e-9ed9-103587002013.jsonl:2:{"type":"model_change","id":"4a41bb5c","parentId":null,"timestamp":"2026-05-04T01:17:49.116Z","provider":"minimax2-7","modelId":"MiniMax-M2.7-highspeed"}
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/f92074f9-874e-4a4e-9ed9-103587002013.jsonl:4:{"type":"custom","customType":"model-snapshot","data":{"timestamp":1777857495525,"provider":"minimax2-7","modelApi":"openai-completions","modelId":"MiniMax-M2.7-highspeed"},"id":"e1a036ab","parentId":"81536599","timestamp":"2026-05-04T01:18:15.528Z"}
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/f92074f9-874e-4a4e-9ed9-103587002013.jsonl:6:{"type":"custom_message","customType":"openclaw.runtime-context","content":"Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.\nWhen reading HEARTBEAT.md, use workspace file /Users/luxiangnan/.claude/HEARTBEAT.md (exact case). Do not read docs/heartbeat.md.\nCurrent time: Monday, May 4th, 2026 - 9:16 AM (Asia/Shanghai) / 2026-05-04 01:16 UTC","display":false,"details":{"source":"openclaw-runtime-context"},"id":"cedafb51","parentId":"a92d69be","timestamp":"2026-05-04T01:18:26.543Z"}
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/f92074f9-874e-4a4e-9ed9-103587002013.jsonl:7:{"type":"message","id":"7ea87f98","parentId":"cedafb51","timestamp":"2026-05-04T01:18:37.274Z","message":{"role":"assistant","content":[{"type":"thinking","thinking":"This is a heartbeat poll. I need to check if HEARTBEAT.md has any tasks or just return HEARTBEAT_OK."},{"type":"text","text":"HEARTBEAT_OK"}],"api":"openai-completions","provider":"minimax2-7","model":"MiniMax-M2.7-highspeed","usage":{"input":0,"output":0,"cacheRead":0,"cacheWrite":0,"totalTokens":0,"cost":{"input":0,"output":0,"cacheRead":0,"cacheWrite":0,"total":0}},"stopReason":"stop","timestamp":1777857506547,"responseId":"064726eab6532cc35a2a95401ab5746c"}}
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/f92074f9-874e-4a4e-9ed9-103587002013.jsonl:9:{"type":"custom_message","customType":"openclaw.runtime-context","content":"Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.\nWhen reading HEARTBEAT.md, use workspace file /Users/luxiangnan/.claude/HEARTBEAT.md (exact case). Do not read docs/heartbeat.md.\nCurrent time: Monday, May 4th, 2026 - 9:47 AM (Asia/Shanghai) / 2026-05-04 01:47 UTC","display":false,"details":{"source":"openclaw-runtime-context"},"id":"ee59cc42","parentId":"68ec2e44","timestamp":"2026-05-04T01:49:30.875Z"}
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/f92074f9-874e-4a4e-9ed9-103587002013.jsonl:10:{"type":"message","id":"d5f47a07","parentId":"ee59cc42","timestamp":"2026-05-04T01:49:37.300Z","message":{"role":"assistant","content":[{"type":"thinking","thinking":"Another heartbeat poll. Nothing in HEARTBEAT.md means no tasks to perform."},{"type":"text","text":"HEARTBEAT_OK"}],"api":"openai-completions","provider":"minimax2-7","model":"MiniMax-M2.7-highspeed","usage":{"input":0,"output":0,"cacheRead":0,"cacheWrite":0,"totalTokens":0,"cost":{"input":0,"output":0,"cacheRead":0,"cacheWrite":0,"total":0}},"stopReason":"stop","timestamp":1777859370875,"responseId":"06472e2dae290189abc80e1ea98f2c6d"}}
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/f92074f9-874e-4a4e-9ed9-103587002013.jsonl:12:{"type":"custom_message","customType":"openclaw.runtime-context","content":"Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.\nWhen reading HEARTBEAT.md, use workspace file /Users/luxiangnan/.claude/HEARTBEAT.md (exact case). Do not read docs/heartbeat.md.\nCurrent time: Monday, May 4th, 2026 - 10:27 AM (Asia/Shanghai) / 2026-05-04 02:27 UTC","display":false,"details":{"source":"openclaw-runtime-context"},"id":"71774432","parentId":"609e9c25","timestamp":"2026-05-04T02:29:23.917Z"}
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/f92074f9-874e-4a4e-9ed9-103587002013.jsonl:13:{"type":"message","id":"fa1f9fa1","parentId":"71774432","timestamp":"2026-05-04T02:29:26.614Z","message":{"role":"assistant","content":[{"type":"thinking","thinking":"Another heartbeat poll. Nothing to do."},{"type":"text","text":"HEARTBEAT_OK"}],"api":"openai-completions","provider":"minimax2-7","model":"MiniMax-M2.7-highspeed","usage":{"input":0,"output":0,"cacheRead":0,"cacheWrite":0,"totalTokens":0,"cost":{"input":0,"output":0,"cacheRead":0,"cacheWrite":0,"total":0}},"stopReason":"stop","timestamp":1777861763917,"responseId":"06473784eb8d775d215367401c252d94"}}
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/f92074f9-874e-4a4e-9ed9-103587002013.jsonl:15:{"type":"custom_message","customType":"openclaw.runtime-context","content":"Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.\nWhen reading HEARTBEAT.md, use workspace file /Users/luxiangnan/.claude/HEARTBEAT.md (exact case). Do not read docs/heartbeat.md.\nCurrent time: Monday, May 4th, 2026 - 10:50 AM (Asia/Shanghai) / 2026-05-04 02:50 UTC","display":false,"details":{"source":"openclaw-runtime-context"},"id":"3e0bc6e5","parentId":"eabe17db","timestamp":"2026-05-04T02:52:01.300Z"}
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/f92074f9-874e-4a4e-9ed9-103587002013.jsonl:16:{"type":"message","id":"81556e30","parentId":"3e0bc6e5","timestamp":"2026-05-04T02:52:04.738Z","message":{"role":"assistant","content":[{"type":"thinking","thinking":"Heartbeat poll - nothing to do."},{"type":"text","text":"HEARTBEAT_OK"}],"api":"openai-completions","provider":"minimax2-7","model":"MiniMax-M2.7-highspeed","usage":{"input":0,"output":0,"cacheRead":0,"cacheWrite":0,"totalTokens":0,"cost":{"input":0,"output":0,"cacheRead":0,"cacheWrite":0,"total":0}},"stopReason":"stop","timestamp":1777863121300,"responseId":"06473cd2e9bc25b1c2b4e20b1dfaec79"}}
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/f92074f9-874e-4a4e-9ed9-103587002013.jsonl:18:{"type":"custom_message","customType":"openclaw.runtime-context","content":"Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.\nWhen reading HEARTBEAT.md, use workspace file /Users/luxiangnan/.claude/HEARTBEAT.md (exact case). Do not read docs/heartbeat.md.\nCurrent time: Monday, May 4th, 2026 - 11:18 AM (Asia/Shanghai) / 2026-05-04 03:18 UTC","display":false,"details":{"source":"openclaw-runtime-context"},"id":"453d2153","parentId":"bc5a3678","timestamp":"2026-05-04T03:20:38.905Z"}
/Users/luxiangnan/.openclaw/agents/claudecode/sessions/f92074f9-874e-4a4e-9ed9-103587002013.jsonl:19:{"type":"message","id":"ad7c3719","parentId":"453d2153","timestamp":"2026-05-04T03:20:42.636Z","message":{"role":"assistant","content":[{"type":"thinking","thinking":"The user is sending a heartbeat poll. HEARTBEAT_OK."},{"type":"text","text":"HEARTBEAT_OK"}],"api":"openai-completions","provider":"minimax2-7","model":"MiniMax-M2.7-highspeed","usage":{"input":0,"output":0,"cacheRead":0,"cacheWrite":0,"totalTokens":0,"cost":{"input":0,"output":0,"cacheRead":0,"cacheWrite":0,"total":0}},"stopReason":"stop","timestamp":1777864838905,"responseId":"064743888e519f7ed2272c6d5f15bb71"}}

===== gateway logs tail =====
2026-05-04T10:00:37.238+08:00 [ws] ⇄ res ✓ sessions.list 555ms conn=0716c4c6…d791 id=7abd2839…f04e
2026-05-04T10:00:37.737+08:00 [ws] ⇄ res ✓ node.list 1830ms conn=0716c4c6…d791 id=9c512089…e46b
2026-05-04T10:00:42.922+08:00 [ws] ⇄ res ✓ sessions.list 548ms conn=0716c4c6…d791 id=b07927e3…25e0
2026-05-04T10:00:43.570+08:00 [ws] ⇄ res ✓ sessions.list 563ms conn=0716c4c6…d791 id=c7fc84be…c94f
2026-05-04T10:00:43.849+08:00 [ws] ⇄ res ✓ node.list 1476ms conn=0716c4c6…d791 id=a45a18c4…13a9
2026-05-04T10:00:47.747+08:00 [ws] ⇄ res ✓ node.list 405ms conn=0716c4c6…d791 id=1c7bbba7…5f81
2026-05-04T10:01:26.629+08:00 [ws] ⇄ res ✓ node.list 15438ms conn=0716c4c6…d791 id=3d710e4a…5844
2026-05-04T10:01:35.081+08:00 [ws] ⇄ res ✓ node.list 221ms conn=0716c4c6…d791 id=c2c76d22…fd79
2026-05-04T10:01:57.069+08:00 [ws] ⇄ res ✓ channels.status 217ms conn=1d3f4b7f…7fd4 id=2151e395…999d
2026-05-04T10:01:59.962+08:00 [ws] ⇄ res ✓ node.list 3610ms conn=0716c4c6…d791 id=bb3fa544…3167
2026-05-04T10:02:31.370+08:00 [ws] ⇄ res ✓ sessions.list 665ms conn=0716c4c6…d791 id=1d7335d5…127b
2026-05-04T10:02:31.371+08:00 [plugins] [openclaw] Agent run started: 11218f3b-b078-4794-b4e9-508a092b7331
2026-05-04T10:02:31.999+08:00 [ws] ⇄ res ✓ sessions.list 534ms conn=0716c4c6…d791 id=f51531d9…349b
2026-05-04T10:02:32.691+08:00 [ws] ⇄ res ✓ node.list 1988ms conn=0716c4c6…d791 id=41fcebfb…1d6d
2026-05-04T10:02:37.748+08:00 [ws] ⇄ res ✓ node.list 369ms conn=0716c4c6…d791 id=f28662d5…354e
2026-05-04T10:02:38.840+08:00 [ws] ⇄ res ✓ sessions.list 566ms conn=0716c4c6…d791 id=803507a6…1712
2026-05-04T10:02:42.712+08:00 [ws] ⇄ res ✓ node.list 345ms conn=0716c4c6…d791 id=c17c9364…4eeb
2026-05-04T10:02:47.764+08:00 [ws] ⇄ res ✓ node.list 354ms conn=0716c4c6…d791 id=03382f8d…4fdd
2026-05-04T10:02:50.199+08:00 [ws] ⇄ res ✓ sessions.list 1135ms conn=0716c4c6…d791 id=272b1565…5ff5
2026-05-04T10:02:52.788+08:00 [ws] ⇄ res ✓ node.list 379ms conn=0716c4c6…d791 id=111ffbe2…6af1
2026-05-04T10:02:53.209+08:00 [ws] ⇄ res ✓ chat.history 51ms conn=80844195…c06c id=331804e5…ed15
2026-05-04T10:02:56.316+08:00 [ws] ⇄ res ✓ sessions.list 1176ms conn=0716c4c6…d791 id=7a607815…7e67
2026-05-04T10:03:00.175+08:00 [ws] ⇄ res ✓ node.list 318ms conn=0716c4c6…d791 id=1fe3c85e…d8db
2026-05-04T10:03:02.688+08:00 [ws] ⇄ res ✓ node.list 344ms conn=0716c4c6…d791 id=2d896675…d3f3
2026-05-04T10:03:07.777+08:00 [ws] ⇄ res ✓ node.list 421ms conn=0716c4c6…d791 id=6952c1e9…efc2
2026-05-04T10:03:13.188+08:00 [ws] ⇄ res ✓ node.list 809ms conn=0716c4c6…d791 id=73ad650f…9f1d
2026-05-04T10:03:15.553+08:00 [ws] ⇄ res ✓ sessions.list 1354ms conn=0716c4c6…d791 id=60326ca9…2ee7
2026-05-04T10:03:15.891+08:00 [ws] ⇄ res ✓ chat.history 192ms conn=80844195…c06c id=461807fe…7297
2026-05-04T10:03:16.360+08:00 [ws] ⇄ res ✓ chat.history 67ms conn=80844195…c06c id=57d17b15…3e34
2026-05-04T10:03:17.773+08:00 [ws] ⇄ res ✓ node.list 414ms conn=0716c4c6…d791 id=61a092f4…56da
2026-05-04T10:03:20.204+08:00 [ws] ⇄ res ✓ sessions.list 1019ms conn=0716c4c6…d791 id=f9f8b4dd…0883
2026-05-04T10:03:24.939+08:00 [ws] ⇄ res ✓ sessions.list 877ms conn=0716c4c6…d791 id=1a965068…b90b
2026-05-04T10:03:24.963+08:00 [plugins] [openclaw] Agent run ended: 11218f3b-b078-4794-b4e9-508a092b7331 (178 chars)
2026-05-04T10:03:25.541+08:00 [ws] ⇄ res ✓ sessions.list 575ms conn=0716c4c6…d791 id=8ddf530c…b80a
2026-05-04T10:03:49.002+08:00 [ws] ⇄ res ✓ node.list 9777ms conn=0716c4c6…d791 id=5dd43a3f…af90
2026-05-04T10:04:22.026+08:00 [ws] ⇄ res ✓ node.list 3745ms conn=0716c4c6…d791 id=f02c4cd5…23ad
2026-05-04T10:04:22.904+08:00 [ws] ⇄ res ✓ node.list 428ms conn=0716c4c6…d791 id=ed5f8c88…0ef3
2026-05-04T10:05:07.376+08:00 [plugins] [openclaw] Agent run started: 9cca3760-3f65-4990-83c8-84ba67e59a59
2026-05-04T10:05:09.162+08:00 [ws] ⇄ res ✓ sessions.list 958ms conn=0716c4c6…d791 id=08576672…6cc0
2026-05-04T10:05:09.973+08:00 [ws] ⇄ res ✓ sessions.list 623ms conn=0716c4c6…d791 id=763c1392…e99a
2026-05-04T10:05:10.398+08:00 [ws] ⇄ res ✓ node.list 2200ms conn=0716c4c6…d791 id=b632cbca…c915
2026-05-04T10:05:13.534+08:00 [ws] ⇄ res ✓ sessions.list 739ms conn=0716c4c6…d791 id=f38a3ac3…06b0
2026-05-04T10:05:13.803+08:00 [ws] ⇄ res ✓ node.list 1385ms conn=0716c4c6…d791 id=874d5b97…fbf6
2026-05-04T10:05:18.197+08:00 [ws] ⇄ res ✓ sessions.list 628ms conn=0716c4c6…d791 id=464c732b…df52
2026-05-04T10:05:20.003+08:00 [ws] ⇄ res ✓ sessions.list 635ms conn=0716c4c6…d791 id=59fe9406…14ad
2026-05-04T10:05:20.047+08:00 [plugins] [openclaw] Agent run ended: 9cca3760-3f65-4990-83c8-84ba67e59a59 (39 chars)
2026-05-04T10:05:20.323+08:00 [ws] ⇄ res ✓ node.list 2776ms conn=0716c4c6…d791 id=6a1b747e…73ff
2026-05-04T10:05:22.845+08:00 [ws] ⇄ res ✓ node.list 493ms conn=0716c4c6…d791 id=f452afc1…a6c3
2026-05-04T10:05:27.688+08:00 [ws] ⇄ res ✓ node.list 360ms conn=0716c4c6…d791 id=ca208c51…c53d
2026-05-04T10:05:48.611+08:00 [ws] ⇄ res ✓ node.list 8696ms conn=0716c4c6…d791 id=f0c590f2…0dfd
2026-05-04T10:06:22.907+08:00 [ws] ⇄ res ✓ node.list 3726ms conn=0716c4c6…d791 id=cff88f9e…8333
2026-05-04T10:07:30.522+08:00 [plugins] [openclaw] Agent run started: 941ea129-f082-4f54-8843-1d9433f1dd00
2026-05-04T10:07:32.794+08:00 [ws] ⇄ res ✓ sessions.list 1074ms conn=0716c4c6…d791 id=6bc7139d…3a21
[info]: [ '[ws]', 'reconnect' ]
2026-05-04T10:07:33.892+08:00 [ws] ⇄ res ✓ sessions.list 918ms conn=0716c4c6…d791 id=34bb423b…4b87
2026-05-04T10:07:34.158+08:00 [plugins] [openclaw] WebSocket closed: 4000 tick timeout
2026-05-04T10:07:34.159+08:00 [plugins] [openclaw] Reconnecting in 1000ms (backoff: 2000ms)
2026-05-04T10:07:34.433+08:00 [ws] ⇄ res ✓ node.list 2710ms conn=0716c4c6…d791 id=9a00b613…3fe6
2026-05-04T10:07:35.222+08:00 [plugins] [openclaw] Connecting to ws://127.0.0.1:18789
2026-05-04T10:07:35.513+08:00 [plugins] [openclaw] WebSocket open, waiting for challenge...
2026-05-04T10:07:35.514+08:00 [plugins] [openclaw] Received connect.challenge
2026-05-04T10:07:35.518+08:00 [plugins] [openclaw] Sending connect request...
2026-05-04T10:07:37.183+08:00 [plugins] [openclaw] Connected! protocol=3, tick=30000ms
2026-05-04T10:07:37.580+08:00 [ws] ⇄ res ✓ skills.status 201ms conn=97f4d9f3…7e30 id=d8eafe7c…2a9e
2026-05-04T10:07:37.584+08:00 [ws] ⇄ res ✓ agent.identity.get 204ms conn=97f4d9f3…7e30 id=1d549cd8…36ba
2026-05-04T10:07:37.635+08:00 [ws] ⇄ res ✓ chat.history 254ms conn=97f4d9f3…7e30 id=61ff057e…e6a2
2026-05-04T10:07:37.800+08:00 [ws] ⇄ res ✓ models.list 421ms conn=97f4d9f3…7e30 id=7775df8b…171e
2026-05-04T10:07:40.162+08:00 [ws] ⇄ res ✓ status 2781ms conn=97f4d9f3…7e30 id=815d6b40…71e1
2026-05-04T10:07:40.311+08:00 [plugins] [openclaw] Agent identity: 天禄
2026-05-04T10:07:40.312+08:00 [plugins] [openclaw] Chat history loaded: 7 messages
2026-05-04T10:07:42.069+08:00 [ws] ⇄ res ✓ sessions.list 1437ms conn=0716c4c6…d791 id=fd7b53db…9cf0
2026-05-04T10:07:42.614+08:00 [ws] ⇄ res ✓ node.list 2434ms conn=0716c4c6…d791 id=76c863a8…b119
2026-05-04T10:07:44.602+08:00 [ws] ⇄ res ✓ config.get 3975ms conn=97f4d9f3…7e30 id=20f60dee…6ba6
2026-05-04T10:07:47.948+08:00 [ws] ⇄ res ✓ node.list 436ms conn=0716c4c6…d791 id=37953d41…6684
2026-05-04T10:07:53.457+08:00 [ws] ⇄ res ✓ node.list 954ms conn=0716c4c6…d791 id=f4c8bd2e…0301
2026-05-04T10:07:55.041+08:00 [ws] ⇄ res ✓ sessions.list 798ms conn=0716c4c6…d791 id=af58194c…1f7c
2026-05-04T10:07:56.010+08:00 [ws] ⇄ res ✓ channels.status 356ms conn=8adf1884…164a id=60a65227…5b5b
2026-05-04T10:07:58.645+08:00 [ws] ⇄ res ✓ sessions.list 777ms conn=0716c4c6…d791 id=64639198…8b42
2026-05-04T10:07:58.761+08:00 [ws] ⇄ res ✓ node.list 1336ms conn=0716c4c6…d791 id=13e588bd…c9ec
2026-05-04T10:08:01.713+08:00 [ws] ⇄ res ✓ sessions.list 718ms conn=0716c4c6…d791 id=496f0aa6…5ed1
2026-05-04T10:08:03.157+08:00 [ws] ⇄ res ✓ node.list 832ms conn=0716c4c6…d791 id=5f1eb890…df32
2026-05-04T10:08:13.066+08:00 [ws] ⇄ res ✓ sessions.list 647ms conn=0716c4c6…d791 id=fba07dd1…898a
2026-05-04T10:08:13.068+08:00 [ws] ⇄ res ✓ node.list 650ms conn=0716c4c6…d791 id=63f18202…1dd6
2026-05-04T10:08:24.927+08:00 [ws] ⇄ res ✓ sessions.list 763ms conn=0716c4c6…d791 id=76d16ec8…9165
2026-05-04T10:08:27.521+08:00 [ws] ⇄ res ✓ sessions.list 1076ms conn=0716c4c6…d791 id=4b87ea9d…3ad7
2026-05-04T10:08:30.529+08:00 [ws] ⇄ res ✓ sessions.list 824ms conn=0716c4c6…d791 id=7d81520a…e2ec
2026-05-04T10:08:38.712+08:00 [ws] ⇄ res ✓ sessions.list 2132ms conn=0716c4c6…d791 id=45ce5774…2894
2026-05-04T10:08:38.757+08:00 [ws] ⇄ res ✓ node.list 2701ms conn=0716c4c6…d791 id=637bb0bb…31ff
2026-05-04T10:08:42.877+08:00 [ws] ⇄ res ✓ node.list 533ms conn=0716c4c6…d791 id=b29b8f00…3ab3
2026-05-04T10:08:44.078+08:00 [ws] ⇄ res ✓ sessions.list 1078ms conn=0716c4c6…d791 id=afe88851…232f
2026-05-04T10:08:47.811+08:00 [ws] ⇄ res ✓ node.list 405ms conn=0716c4c6…d791 id=0532ead3…681e
2026-05-04T10:08:53.208+08:00 [ws] ⇄ res ✓ node.list 458ms conn=0716c4c6…d791 id=7e644d00…b35d
2026-05-04T10:08:57.127+08:00 [ws] ⇄ res ✓ sessions.list 1607ms conn=0716c4c6…d791 id=a7542681…a1ab
2026-05-04T10:08:58.466+08:00 [ws] ⇄ res ✓ node.list 1095ms conn=0716c4c6…d791 id=b4ca9c09…ab97
2026-05-04T10:09:08.342+08:00 [ws] ⇄ res ✓ sessions.list 961ms conn=0716c4c6…d791 id=fb2f8b41…46da
2026-05-04T10:09:08.683+08:00 [ws] ⇄ res ✓ node.list 1302ms conn=0716c4c6…d791 id=d159d3c1…6f2d
2026-05-04T10:09:16.088+08:00 [ws] ⇄ res ✓ sessions.list 901ms conn=0716c4c6…d791 id=3cbc5ba3…98e8
2026-05-04T10:09:16.111+08:00 [plugins] [openclaw] Agent run ended: 941ea129-f082-4f54-8843-1d9433f1dd00 (279 chars)
2026-05-04T10:09:17.043+08:00 [ws] ⇄ res ✓ sessions.list 930ms conn=0716c4c6…d791 id=c228ae7b…4891
2026-05-04T10:09:51.547+08:00 [feishu] feishu[main]: dropping duplicate event for message om_x100b504bb3f2f4a8c3d07e980799832
2026-05-04T10:10:06.749+08:00 [ws] ⇄ res ✓ node.list 15230ms conn=0716c4c6…d791 id=e9b35239…e85c
2026-05-04T10:10:15.346+08:00 [ws] ⇄ res ✓ node.list 515ms conn=0716c4c6…d791 id=cc3d4fe0…a07d
2026-05-04T10:10:17.932+08:00 [ws] ⇄ res ✓ node.list 553ms conn=0716c4c6…d791 id=f3a2c3a7…bc3b
2026-05-04T10:10:19.974+08:00 [feishu] feishu[main]: received message from ou_86334cb4d260a4c4c4de1e87bf59474d in oc_5016041d5ee6ed2a8cc4e98372569cec (p2p)
2026-05-04T10:10:19.982+08:00 [feishu] feishu[main]: Feishu[main] DM from ou_86334cb4d260a4c4c4de1e87bf59474d: 你们继续 吧
2026-05-04T10:10:20.028+08:00 [feishu] feishu[main]: dispatching to agent (session=agent:tianlu:feishu:direct:ou_86334cb4d260a4c4c4de1e87bf59474d)
2026-05-04T10:11:05.775+08:00 [ws] ⇄ res ✓ node.list 10329ms conn=0716c4c6…d791 id=39270fb7…f25f
2026-05-04T10:11:57.438+08:00 [ws] ⇄ res ✓ sessions.list 916ms conn=0716c4c6…d791 id=bf055988…9627
2026-05-04T10:11:58.834+08:00 [ws] ⇄ res ✓ sessions.list 1220ms conn=0716c4c6…d791 id=11b5d1a4…64e0
2026-05-04T10:11:58.841+08:00 [ws] ⇄ res ✓ node.list 50462ms conn=0716c4c6…d791 id=7b1b16b2…afde
2026-05-04T10:11:59.462+08:00 [plugins] [openclaw] WebSocket closed: 4000 tick timeout
2026-05-04T10:11:59.463+08:00 [plugins] [openclaw] Reconnecting in 1000ms (backoff: 2000ms)
2026-05-04T10:11:59.733+08:00 [ws] ⇄ res ✓ channels.status 269ms conn=7d1c7819…8070 id=184a790a…cbb4
2026-05-04T10:12:00.562+08:00 [plugins] [openclaw] Connecting to ws://127.0.0.1:18789
2026-05-04T10:12:00.811+08:00 [plugins] [openclaw] WebSocket open, waiting for challenge...
2026-05-04T10:12:00.812+08:00 [plugins] [openclaw] Received connect.challenge
2026-05-04T10:12:00.814+08:00 [plugins] [openclaw] Sending connect request...
2026-05-04T10:12:02.441+08:00 [plugins] [openclaw] Connected! protocol=3, tick=30000ms
2026-05-04T10:12:03.151+08:00 [ws] ⇄ res ✓ skills.status 251ms conn=ecca49e4…15ee id=7d00244c…2a91
2026-05-04T10:12:03.154+08:00 [ws] ⇄ res ✓ agent.identity.get 255ms conn=ecca49e4…15ee id=bee57aff…4b5f
2026-05-04T10:12:03.253+08:00 [ws] ⇄ res ✓ chat.history 354ms conn=ecca49e4…15ee id=812f40ce…2413
2026-05-04T10:12:03.511+08:00 [ws] ⇄ res ✓ models.list 612ms conn=ecca49e4…15ee id=d5f334bf…a316
2026-05-04T10:12:05.048+08:00 [ws] ⇄ res ✓ status 2150ms conn=ecca49e4…15ee id=7c1b783f…1c13
2026-05-04T10:12:05.384+08:00 [plugins] [openclaw] Agent identity: 天禄
2026-05-04T10:12:05.384+08:00 [plugins] [openclaw] Chat history loaded: 7 messages
2026-05-04T10:12:05.675+08:00 [ws] ⇄ res ✓ node.list 3193ms conn=0716c4c6…d791 id=dc3e9ee0…90d8
2026-05-04T10:12:06.914+08:00 [ws] ⇄ res ✓ sessions.list 844ms conn=0716c4c6…d791 id=a5e4ce91…7663
2026-05-04T10:12:07.980+08:00 [ws] ⇄ res ✓ node.list 436ms conn=0716c4c6…d791 id=9d56d345…e14c
2026-05-04T10:12:07.993+08:00 [ws] ⇄ res ✓ config.get 2450ms conn=ecca49e4…15ee id=fb3ba372…7b35
2026-05-04T10:12:59.223+08:00 [ws] ⇄ res ✓ node.list 16478ms conn=0716c4c6…d791 id=8badd65c…e891
2026-05-04T10:13:00.841+08:00 [ws] ⇄ res ✓ sessions.list 1548ms conn=0716c4c6…d791 id=1071d94c…bb64
2026-05-04T10:13:01.902+08:00 [ws] ⇄ res ✓ sessions.list 778ms conn=0716c4c6…d791 id=8012e6ed…8a66
2026-05-04T10:13:13.014+08:00 [ws] ⇄ res ✓ node.list 787ms conn=0716c4c6…d791 id=ac3de7a8…504f
2026-05-04T10:13:47.073+08:00 [ws] ⇄ res ✓ node.list 5378ms conn=0716c4c6…d791 id=1716a78d…81ca
typing TTL reached (2m); stopping typing indicator
2026-05-04T10:14:27.449+08:00 [ws] ⇄ res ✓ sessions.list 1093ms conn=0716c4c6…d791 id=df46742c…bc13
2026-05-04T10:14:28.650+08:00 [ws] ⇄ res ✓ sessions.list 1037ms conn=0716c4c6…d791 id=ded800e0…79f8
2026-05-04T10:14:28.844+08:00 [ws] ⇄ res ✓ node.list 40616ms conn=0716c4c6…d791 id=253b7225…4004
2026-05-04T10:15:22.237+08:00 [ws] ⇄ res ✓ node.list 16735ms conn=0716c4c6…d791 id=bb4231cc…7898
2026-05-04T10:15:31.844+08:00 [ws] ⇄ res ✓ node.list 1837ms conn=0716c4c6…d791 id=c9cdaa0e…e755
2026-05-04T10:15:37.727+08:00 [ws] ⇄ res ✓ sessions.list 3089ms conn=0716c4c6…d791 id=2d46dff9…ce18
2026-05-04T10:15:39.680+08:00 [ws] ⇄ res ✓ sessions.list 1695ms conn=0716c4c6…d791 id=d53c6c9d…b794
2026-05-04T10:15:39.685+08:00 [ws] ⇄ res ✓ node.list 7069ms conn=0716c4c6…d791 id=07c08e92…70e7
2026-05-04T10:15:43.427+08:00 [ws] ⇄ res ✓ node.list 793ms conn=0716c4c6…d791 id=b48ff53a…f231
2026-05-04T10:16:21.714+08:00 [ws] ⇄ res ✓ node.list 5887ms conn=0716c4c6…d791 id=354b5c8b…b1c9
2026-05-04T10:16:58.046+08:00 [ws] webchat disconnected code=1006 reason=n/a conn=0716c4c6-f75d-4e37-affe-180eec28d791
2026-05-04T10:16:58.826+08:00 [plugins] [openclaw] Agent run started: 555553ee-dc56-48d8-8b06-4c0a76d3158e
2026-05-04T10:16:58.920+08:00 [ws] ⇄ res ✓ node.list 36503ms conn=0716c4c6…d791 id=b84d4369…7c8b
2026-05-04T10:17:08.955+08:00 [plugins] [openclaw] Agent run ended: 555553ee-dc56-48d8-8b06-4c0a76d3158e (99 chars)
2026-05-04T10:17:10.779+08:00 [feishu] feishu[main]: dispatch complete (queuedFinal=true, replies=1)
2026-05-04T10:17:10.781+08:00 [feishu] skipping duplicate message om_x100b504bb3f2f4a8c3d07e980799832
2026-05-04T10:17:56.946+08:00 [ws] ⇄ res ✓ channels.status 200ms conn=38eb033a…0330 id=fe32a59a…2b5d
2026-05-04T10:18:23.977+08:00 [plugins] [openclaw] Agent run started: 0785d573-929e-4e4f-9fdf-fd0062fc4f8b
2026-05-04T10:18:55.426+08:00 [ws] ⇄ res ✓ chat.history 53ms conn=ecca49e4…15ee id=2f7ed0a6…654c
2026-05-04T10:18:55.940+08:00 [ws] ⇄ res ✓ chat.history 73ms conn=ecca49e4…15ee id=f85aa56a…500e
2026-05-04T10:18:56.433+08:00 [ws] ⇄ res ✓ chat.history 63ms conn=ecca49e4…15ee id=70e44d6a…1fa5
2026-05-04T10:18:57.508+08:00 [ws] ⇄ res ✓ chat.history 106ms conn=ecca49e4…15ee id=eca01fc7…3727
2026-05-04T10:18:59.943+08:00 [ws] ⇄ res ✓ chat.history 53ms conn=ecca49e4…15ee id=6e33bdde…ddd2
2026-05-04T10:19:03.492+08:00 [ws] ⇄ res ✓ channels.status 220ms conn=3dcdd46b…5b13 id=7dfa1507…bd7d
2026-05-04T10:19:05.843+08:00 [ws] ⇄ res ✓ chat.history 57ms conn=ecca49e4…15ee id=2848d64d…312c
2026-05-04T10:19:09.347+08:00 [ws] ⇄ res ✓ chat.history 77ms conn=ecca49e4…15ee id=dc94393f…f7c4
2026-05-04T10:19:14.366+08:00 [ws] ⇄ res ✓ chat.history 71ms conn=ecca49e4…15ee id=33ea9b0a…b1c9
2026-05-04T10:19:16.337+08:00 [ws] ⇄ res ✓ chat.history 51ms conn=ecca49e4…15ee id=1896e85e…91bd
2026-05-04T10:19:16.836+08:00 [ws] ⇄ res ✓ chat.history 61ms conn=ecca49e4…15ee id=e2c3f4e3…c114
2026-05-04T10:19:47.151+08:00 [plugins] [openclaw] Agent run ended: 0785d573-929e-4e4f-9fdf-fd0062fc4f8b (247 chars)
2026-05-04T10:21:02.230+08:00 [ws] ⇄ res ✓ channels.status 213ms conn=f5a81191…1dc7 id=e062315d…b7a5
2026-05-04T10:21:56.733+08:00 [ws] ⇄ res ✓ channels.status 197ms conn=0dfac784…c51a id=42e9191f…19c9
2026-05-04T10:23:08.493+08:00 [plugins] [openclaw] Agent run started: 3cacff9e-6223-4dc3-b7fd-f70e898eb182
2026-05-04T10:23:13.687+08:00 [plugins] [openclaw] Agent run ended: 3cacff9e-6223-4dc3-b7fd-f70e898eb182 (36 chars)
2026-05-04T10:24:46.688+08:00 [plugins] [openclaw] Agent run started: 94e8d612-7be8-4eb9-a3b9-5c2947b81ae9
2026-05-04T10:24:51.361+08:00 [ws] ⇄ res ✓ channels.status 226ms conn=f9fa34aa…1920 id=567ef8bd…06aa
2026-05-04T10:25:10.323+08:00 [ws] ⇄ res ✓ chat.history 76ms conn=ecca49e4…15ee id=ad0b584d…c3b1
2026-05-04T10:25:15.311+08:00 [ws] ⇄ res ✓ chat.history 52ms conn=ecca49e4…15ee id=331039e7…a48c
2026-05-04T10:25:17.314+08:00 [ws] ⇄ res ✓ chat.history 54ms conn=ecca49e4…15ee id=306ad106…7d18
2026-05-04T10:25:17.849+08:00 [ws] ⇄ res ✓ chat.history 87ms conn=ecca49e4…15ee id=0342ef89…9ee4
2026-05-04T10:25:28.836+08:00 [ws] ⇄ res ✓ chat.history 68ms conn=ecca49e4…15ee id=6eb58e2d…906b
2026-05-04T10:25:31.823+08:00 [ws] ⇄ res ✓ chat.history 52ms conn=ecca49e4…15ee id=5010d1af…c6ee
2026-05-04T10:25:37.501+08:00 [plugins] [openclaw] Agent run ended: 94e8d612-7be8-4eb9-a3b9-5c2947b81ae9 (201 chars)
2026-05-04T10:30:56.918+08:00 [ws] ⇄ res ✓ channels.status 225ms conn=025058ee…37b2 id=e81b68e3…d4af
2026-05-04T10:31:53.661+08:00 [ws] ⇄ res ✓ channels.status 209ms conn=d066b3c3…1f2a id=fd9fdd1d…c2b6
2026-05-04T10:33:12.262+08:00 [plugins] [openclaw] Agent run started: 325ee8aa-9179-4172-825b-bef585198956
2026-05-04T10:33:18.231+08:00 [plugins] [openclaw] Agent run ended: 325ee8aa-9179-4172-825b-bef585198956 (33 chars)
2026-05-04T10:34:52.922+08:00 [plugins] [openclaw] Agent run started: 7ac053bb-baf0-45c1-9106-62e80291e183
2026-05-04T10:34:53.807+08:00 [ws] ⇄ res ✓ channels.status 203ms conn=306c1f67…8113 id=42cbe000…301a
2026-05-04T10:35:41.516+08:00 [plugins] [openclaw] Agent run ended: 7ac053bb-baf0-45c1-9106-62e80291e183 (211 chars)
2026-05-04T10:35:41.575+08:00 [ws] ⇄ res ✓ chat.history 56ms conn=ecca49e4…15ee id=ded5dead…b7b2
2026-05-04T10:36:38.838+08:00 [plugins] [openclaw] WebSocket closed: 4000 tick timeout
2026-05-04T10:36:38.839+08:00 [plugins] [openclaw] Reconnecting in 1000ms (backoff: 2000ms)
2026-05-04T10:36:43.254+08:00 [plugins] [openclaw] Connecting to ws://127.0.0.1:18789
2026-05-04T10:36:43.431+08:00 [plugins] [openclaw] WebSocket open, waiting for challenge...
2026-05-04T10:36:43.432+08:00 [plugins] [openclaw] Received connect.challenge
2026-05-04T10:36:43.434+08:00 [plugins] [openclaw] Sending connect request...
2026-05-04T10:36:44.487+08:00 [plugins] [openclaw] Connected! protocol=3, tick=30000ms
2026-05-04T10:36:44.647+08:00 [ws] ⇄ res ✓ skills.status 72ms conn=4baebb68…eef2 id=e0698f7c…f9cd
2026-05-04T10:36:44.653+08:00 [ws] ⇄ res ✓ agent.identity.get 79ms conn=4baebb68…eef2 id=bca3fc22…58b3
2026-05-04T10:36:44.678+08:00 [ws] ⇄ res ✓ chat.history 104ms conn=4baebb68…eef2 id=c3df1485…486f
2026-05-04T10:36:44.765+08:00 [ws] ⇄ res ✓ models.list 190ms conn=4baebb68…eef2 id=6a6ca9eb…1095
2026-05-04T10:36:45.770+08:00 [ws] ⇄ res ✓ status 1196ms conn=4baebb68…eef2 id=77dc1d24…11a6
2026-05-04T10:36:45.859+08:00 [plugins] [openclaw] Agent identity: 天禄
2026-05-04T10:36:45.860+08:00 [plugins] [openclaw] Chat history loaded: 10 messages
2026-05-04T10:36:47.007+08:00 [ws] ⇄ res ✓ config.get 1059ms conn=4baebb68…eef2 id=5f650a5c…29e2
2026-05-04T10:40:55.088+08:00 [ws] ⇄ res ✓ channels.status 224ms conn=51c859f9…0457 id=f1ecd779…efab
2026-05-04T10:41:31.633+08:00 [plugins] [openclaw] Agent run started: 5782c754-a146-4d4c-a34a-ff9c85ef18d5
2026-05-04T10:41:35.033+08:00 [ws] ⇄ res ✓ chat.history 70ms conn=4baebb68…eef2 id=bb560747…0784
2026-05-04T10:41:48.464+08:00 [ws] ⇄ res ✓ chat.history 52ms conn=4baebb68…eef2 id=597575a1…54f9
2026-05-04T10:41:50.866+08:00 [ws] ⇄ res ✓ channels.status 223ms conn=6ada14ba…9428 id=fe5f7eb0…acc2
2026-05-04T10:42:07.439+08:00 [plugins] [openclaw] Agent run ended: 5782c754-a146-4d4c-a34a-ff9c85ef18d5 (295 chars)
2026-05-04T10:42:59.739+08:00 [ws] ⇄ res ✓ channels.status 264ms conn=e83a47aa…e506 id=e0a9c088…ad7f
2026-05-04T10:43:50.794+08:00 [ws] ⇄ res ✓ channels.status 205ms conn=fc94e3b3…ebb1 id=e1bdda6f…5791
2026-05-04T10:44:50.981+08:00 [ws] ⇄ res ✓ channels.status 221ms conn=680ca04c…eb52 id=def1c878…9119
2026-05-04T10:46:30.722+08:00 [plugins] [openclaw] Agent run started: aedd9d7a-d475-4165-b424-a897151f1196
2026-05-04T10:46:36.641+08:00 [plugins] [openclaw] Agent run ended: aedd9d7a-d475-4165-b424-a897151f1196 (33 chars)
2026-05-04T10:48:05.823+08:00 [plugins] [openclaw] Agent run started: 5cdf3a46-2f60-40c9-9970-f2b3522759c1
2026-05-04T10:48:06.099+08:00 [plugins] [openclaw] WebSocket closed: 4000 tick timeout
2026-05-04T10:48:06.100+08:00 [plugins] [openclaw] Reconnecting in 1000ms (backoff: 2000ms)
2026-05-04T10:48:07.139+08:00 [plugins] [openclaw] Connecting to ws://127.0.0.1:18789
2026-05-04T10:48:07.582+08:00 [plugins] [openclaw] WebSocket open, waiting for challenge...
2026-05-04T10:48:07.582+08:00 [plugins] [openclaw] Received connect.challenge
2026-05-04T10:48:07.624+08:00 [plugins] [openclaw] Sending connect request...
2026-05-04T10:48:08.974+08:00 [plugins] [openclaw] Connected! protocol=3, tick=30000ms
2026-05-04T10:48:09.153+08:00 [ws] ⇄ res ✓ agent.identity.get 56ms conn=ebd0dfd9…ec24 id=78e07113…25f3
2026-05-04T10:48:10.631+08:00 [ws] ⇄ res ✓ skills.status 1543ms conn=ebd0dfd9…ec24 id=3f4dc6e2…5bf8
2026-05-04T10:48:10.632+08:00 [ws] ⇄ res ✓ agent.identity.get 1545ms conn=ebd0dfd9…ec24 id=0bfb8c83…779d
2026-05-04T10:48:10.662+08:00 [ws] ⇄ res ✓ chat.history 1575ms conn=ebd0dfd9…ec24 id=0754d182…ffe8
2026-05-04T10:48:10.758+08:00 [ws] ⇄ res ✓ models.list 1671ms conn=ebd0dfd9…ec24 id=f2179e63…3378
2026-05-04T10:48:12.072+08:00 [ws] ⇄ res ✓ status 2966ms conn=ebd0dfd9…ec24 id=ad585d87…de80
2026-05-04T10:48:12.187+08:00 [plugins] [openclaw] Agent identity: 天禄
2026-05-04T10:48:12.187+08:00 [plugins] [openclaw] Chat history loaded: 13 messages
2026-05-04T10:48:13.401+08:00 [ws] ⇄ res ✓ config.get 1105ms conn=ebd0dfd9…ec24 id=3aca743f…c7ac
2026-05-04T10:48:51.879+08:00 [ws] ⇄ res ✓ channels.status 233ms conn=7c6a2276…4221 id=0d69591a…3ac8
2026-05-04T10:50:01.870+08:00 [ws] ⇄ res ✓ channels.status 241ms conn=4ab327cd…a467 id=8aa4369d…176f
2026-05-04T10:50:03.973+08:00 [plugins] [openclaw] Agent run ended: 5cdf3a46-2f60-40c9-9970-f2b3522759c1 (156 chars)
2026-05-04T10:50:51.937+08:00 [ws] ⇄ res ✓ channels.status 204ms conn=1302c227…c723 id=f9e087c0…6c10
2026-05-04T10:52:01.876+08:00 [ws] ⇄ res ✓ channels.status 201ms conn=d279a1c6…0a2c id=585f3425…839a
2026-05-04T10:53:54.056+08:00 [ws] ⇄ res ✓ channels.status 214ms conn=0e219f80…1a55 id=10b62c63…2745
2026-05-04T10:56:35.298+08:00 [plugins] [openclaw] Agent run started: ccb4d1b2-0b75-4763-8932-78670d1eda8e
2026-05-04T10:56:39.446+08:00 [ws] ⇄ res ✓ chat.history 63ms conn=ebd0dfd9…ec24 id=ace98fd2…2c33
2026-05-04T10:56:49.102+08:00 [ws] ⇄ res ✓ chat.history 103ms conn=ebd0dfd9…ec24 id=ebb8c187…4ab5
2026-05-04T10:56:53.465+08:00 [ws] ⇄ res ✓ channels.status 212ms conn=607a0dd5…718a id=deaa0d5e…ecc5
2026-05-04T10:57:34.295+08:00 [ws] ⇄ res ✓ chat.history 52ms conn=ebd0dfd9…ec24 id=6c8c19cd…1cff
2026-05-04T10:57:41.679+08:00 [plugins] [openclaw] Agent run ended: ccb4d1b2-0b75-4763-8932-78670d1eda8e (200 chars)
2026-05-04T10:58:50.877+08:00 [ws] ⇄ res ✓ channels.status 289ms conn=8c688acc…c642 id=e8cc8b28…4e63
2026-05-04T11:00:54.126+08:00 [ws] ⇄ res ✓ channels.status 207ms conn=a2db60cf…dc99 id=8132e039…86a8
2026-05-04T11:01:45.240+08:00 [plugins] [openclaw] Agent run started: cce67ae6-9079-443e-b817-fff2f2a5727f
2026-05-04T11:01:56.222+08:00 [ws] ⇄ res ✓ chat.history 50ms conn=ebd0dfd9…ec24 id=88c63788…be57
2026-05-04T11:01:57.689+08:00 [ws] ⇄ res ✓ chat.history 54ms conn=ebd0dfd9…ec24 id=d14f6d7b…f874
2026-05-04T11:02:03.208+08:00 [ws] ⇄ res ✓ chat.history 52ms conn=ebd0dfd9…ec24 id=cb1d19a9…434b
2026-05-04T11:02:03.748+08:00 [ws] ⇄ res ✓ channels.status 245ms conn=aa695c62…ab60 id=66683866…e0eb
2026-05-04T11:02:29.328+08:00 [ws] ⇄ res ✓ chat.history 55ms conn=ebd0dfd9…ec24 id=dc0d07c6…69c1
2026-05-04T11:02:51.373+08:00 [ws] ⇄ res ✓ channels.status 211ms conn=f770380c…4605 id=25752276…b80c
2026-05-04T11:02:52.362+08:00 [plugins] [openclaw] Agent run ended: cce67ae6-9079-443e-b817-fff2f2a5727f (33 chars)
2026-05-04T11:04:34.896+08:00 [plugins] [openclaw] Agent run started: 1504c34d-b46b-4a7d-bdd4-524c439d01a2
2026-05-04T11:04:40.651+08:00 [ws] ⇄ res ✓ chat.history 67ms conn=ebd0dfd9…ec24 id=dda5b8aa…b825
2026-05-04T11:04:48.144+08:00 [ws] ⇄ res ✓ chat.history 250ms conn=ebd0dfd9…ec24 id=edcabf85…fbc5
2026-05-04T11:05:00.832+08:00 [ws] ⇄ res ✓ chat.history 52ms conn=ebd0dfd9…ec24 id=a425bb3a…0c73
2026-05-04T11:05:01.323+08:00 [ws] ⇄ res ✓ chat.history 52ms conn=ebd0dfd9…ec24 id=3495e897…49ad
2026-05-04T11:05:25.248+08:00 [ws] ⇄ res ✓ chat.history 52ms conn=ebd0dfd9…ec24 id=8a4c5d6c…be47
2026-05-04T11:05:26.231+08:00 [ws] ⇄ res ✓ chat.history 51ms conn=ebd0dfd9…ec24 id=44c39be5…a525
2026-05-04T11:05:27.216+08:00 [ws] ⇄ res ✓ chat.history 57ms conn=ebd0dfd9…ec24 id=7cbc92e6…ad3f
2026-05-04T11:05:28.259+08:00 [ws] ⇄ res ✓ chat.history 76ms conn=ebd0dfd9…ec24 id=42fc34db…62ff
2026-05-04T11:05:30.778+08:00 [ws] ⇄ res ✓ chat.history 96ms conn=ebd0dfd9…ec24 id=60bb4522…af13
2026-05-04T11:05:33.373+08:00 [ws] ⇄ res ✓ chat.history 188ms conn=ebd0dfd9…ec24 id=780ff132…f4e5
2026-05-04T11:05:34.257+08:00 [ws] ⇄ res ✓ chat.history 69ms conn=ebd0dfd9…ec24 id=d413ce4b…a8c6
2026-05-04T11:05:34.740+08:00 [ws] ⇄ res ✓ chat.history 75ms conn=ebd0dfd9…ec24 id=4c92a6f9…aa4d
2026-05-04T11:05:36.723+08:00 [ws] ⇄ res ✓ chat.history 53ms conn=ebd0dfd9…ec24 id=a9a68819…81e4
2026-05-04T11:05:39.734+08:00 [ws] ⇄ res ✓ chat.history 60ms conn=ebd0dfd9…ec24 id=f0eb7781…7336
2026-05-04T11:05:49.245+08:00 [ws] ⇄ res ✓ chat.history 58ms conn=ebd0dfd9…ec24 id=2919773f…6b4f
2026-05-04T11:05:50.758+08:00 [ws] ⇄ res ✓ chat.history 64ms conn=ebd0dfd9…ec24 id=87b67a7c…e4e9
2026-05-04T11:05:52.145+08:00 [ws] ⇄ res ✓ channels.status 356ms conn=1b1c3220…e6c9 id=ddc9b2e7…1a6f
2026-05-04T11:05:57.350+08:00 [ws] ⇄ res ✓ chat.history 59ms conn=ebd0dfd9…ec24 id=8d9903dd…05cb
2026-05-04T11:05:57.890+08:00 [ws] ⇄ res ✓ chat.history 99ms conn=ebd0dfd9…ec24 id=5af917d4…2944
2026-05-04T11:05:58.345+08:00 [ws] ⇄ res ✓ chat.history 55ms conn=ebd0dfd9…ec24 id=6061df54…8c1e
2026-05-04T11:06:04.450+08:00 [plugins] [openclaw] Agent run ended: 1504c34d-b46b-4a7d-bdd4-524c439d01a2 (224 chars)
2026-05-04T11:09:01.023+08:00 [ws] ⇄ res ✓ channels.status 216ms conn=0d433c95…7cf5 id=7f376b32…c1c8
2026-05-04T11:09:55.405+08:00 [ws] ⇄ res ✓ channels.status 274ms conn=370f4d51…ec16 id=c0d7ea15…279e
2026-05-04T11:11:35.931+08:00 [plugins] [openclaw] Agent run started: 4ec047f7-ba60-4041-a487-e76ebb72c62b
2026-05-04T11:11:50.168+08:00 [ws] ⇄ res ✓ chat.history 62ms conn=ebd0dfd9…ec24 id=56ea31d0…9ba3
2026-05-04T11:11:50.589+08:00 [ws] ⇄ res ✓ channels.status 204ms conn=e91cd180…da0e id=bb0a1cde…07df
2026-05-04T11:11:59.749+08:00 [ws] ⇄ res ✓ chat.history 95ms conn=ebd0dfd9…ec24 id=41c0de28…3d21
2026-05-04T11:12:32.922+08:00 [plugins] [openclaw] Agent run ended: 4ec047f7-ba60-4041-a487-e76ebb72c62b (23 chars)
2026-05-04T11:12:51.245+08:00 [ws] ⇄ res ✓ channels.status 222ms conn=e740b536…d544 id=f5a55ad9…3885
2026-05-04T11:13:51.236+08:00 [ws] ⇄ res ✓ channels.status 213ms conn=178afb55…3afd id=90670e28…0488
2026-05-04T11:14:52.313+08:00 [feishu] skipping duplicate message om_x100b504bb3f2f4a8c3d07e980799832
2026-05-04T11:15:52.921+08:00 [ws] ⇄ res ✓ channels.status 201ms conn=5a4281d5…be73 id=f4c76f56…8a7a
2026-05-04T11:16:20.596+08:00 [plugins] [openclaw] Agent run started: d2684226-fd2e-44de-b4f2-f5073759a885
2026-05-04T11:16:28.494+08:00 [plugins] [openclaw] Agent run ended: d2684226-fd2e-44de-b4f2-f5073759a885 (58 chars)
2026-05-04T11:18:03.903+08:00 [plugins] [openclaw] Agent run started: f1809ab8-4dce-4eec-a16c-90da9b861590
2026-05-04T11:18:15.977+08:00 [ws] ⇄ res ✓ chat.history 56ms conn=ebd0dfd9…ec24 id=a83fa511…d848
2026-05-04T11:18:17.158+08:00 [ws] ⇄ res ✓ chat.history 279ms conn=ebd0dfd9…ec24 id=9c0930eb…1e4b
2026-05-04T11:18:39.152+08:00 [ws] ⇄ res ✓ chat.history 50ms conn=ebd0dfd9…ec24 id=6363d14f…1add
2026-05-04T11:18:41.157+08:00 [ws] ⇄ res ✓ chat.history 55ms conn=ebd0dfd9…ec24 id=f29c8dc2…e2f4
2026-05-04T11:18:43.182+08:00 [ws] ⇄ res ✓ chat.history 95ms conn=ebd0dfd9…ec24 id=9729edb6…c86c
2026-05-04T11:18:52.311+08:00 [plugins] [openclaw] Agent run ended: f1809ab8-4dce-4eec-a16c-90da9b861590 (310 chars)
2026-05-04T11:19:55.438+08:00 [ws] ⇄ res ✓ channels.status 241ms conn=0a7220ba…a31e id=3a04d3a3…bb5d
2026-05-04T11:22:09.354+08:00 [plugins] [openclaw] Agent run started: da902474-3b1d-4246-87b4-8279e290b0ce
2026-05-04T11:22:25.218+08:00 [ws] ⇄ res ✓ node.list 409ms conn=50b41787…8eaf id=fc3b7c40…9161
2026-05-04T11:22:31.051+08:00 [ws] ⇄ res ✓ chat.history 53ms conn=ebd0dfd9…ec24 id=74818869…eedc
2026-05-04T11:22:32.558+08:00 [ws] ⇄ res ✓ chat.history 60ms conn=ebd0dfd9…ec24 id=53181958…7e8f
2026-05-04T11:22:35.081+08:00 [ws] ⇄ res ✓ chat.history 65ms conn=ebd0dfd9…ec24 id=934acdec…e20c
2026-05-04T11:22:48.103+08:00 [plugins] [openclaw] Agent run ended: da902474-3b1d-4246-87b4-8279e290b0ce (262 chars)
2026-05-04T10:19:47.696+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/eval-harness resolved=~/.openclaw/workspace/skills/eval-harness
2026-05-04T10:19:47.697+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/exa-search resolved=~/.openclaw/workspace/skills/exa-search
2026-05-04T10:19:47.697+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/excalidraw resolved=~/.openclaw/workspace/skills/excalidraw
2026-05-04T10:19:47.698+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fal-ai-media resolved=~/.openclaw/workspace/skills/fal-ai-media
2026-05-04T10:19:47.698+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fear-greed resolved=~/.openclaw/workspace/skills/fear-greed
2026-05-04T10:19:47.698+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/foundation-models-on-device resolved=~/.openclaw/workspace/skills/foundation-models-on-device
2026-05-04T10:19:47.699+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/freqtrade-strategy resolved=~/.openclaw/workspace/skills/freqtrade-strategy
2026-05-04T10:19:47.699+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/frontend resolved=~/.openclaw/workspace/skills/frontend
2026-05-04T10:19:47.700+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/frontend-patterns resolved=~/.openclaw/workspace/skills/frontend-patterns
2026-05-04T10:19:47.700+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/frontend-slides resolved=~/.openclaw/workspace/skills/frontend-slides
2026-05-04T10:19:47.700+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-comps-analysis resolved=~/.openclaw/workspace/skills/fsi-comps-analysis
2026-05-04T10:19:47.701+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-er-catalyst-calendar resolved=~/.openclaw/workspace/skills/fsi-er-catalyst-calendar
2026-05-04T10:19:47.701+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-er-cmd-catalysts resolved=~/.openclaw/workspace/skills/fsi-er-cmd-catalysts
2026-05-04T10:19:47.702+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-er-cmd-earnings resolved=~/.openclaw/workspace/skills/fsi-er-cmd-earnings
2026-05-04T10:19:47.702+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-er-cmd-earnings-preview resolved=~/.openclaw/workspace/skills/fsi-er-cmd-earnings-preview
2026-05-04T10:19:47.702+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-er-cmd-initiate resolved=~/.openclaw/workspace/skills/fsi-er-cmd-initiate
2026-05-04T10:19:47.703+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-er-cmd-model-update resolved=~/.openclaw/workspace/skills/fsi-er-cmd-model-update
2026-05-04T10:19:47.703+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-er-cmd-morning-note resolved=~/.openclaw/workspace/skills/fsi-er-cmd-morning-note
2026-05-04T10:19:47.704+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-er-cmd-screen resolved=~/.openclaw/workspace/skills/fsi-er-cmd-screen
2026-05-04T10:19:47.704+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-er-cmd-sector resolved=~/.openclaw/workspace/skills/fsi-er-cmd-sector
2026-05-04T10:19:47.704+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-er-cmd-thesis resolved=~/.openclaw/workspace/skills/fsi-er-cmd-thesis
2026-05-04T10:19:47.705+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-er-earnings-analysis resolved=~/.openclaw/workspace/skills/fsi-er-earnings-analysis
2026-05-04T10:19:47.705+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-er-earnings-preview resolved=~/.openclaw/workspace/skills/fsi-er-earnings-preview
2026-05-04T10:19:47.706+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-er-idea-generation resolved=~/.openclaw/workspace/skills/fsi-er-idea-generation
2026-05-04T10:19:47.708+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-er-initiating-coverage resolved=~/.openclaw/workspace/skills/fsi-er-initiating-coverage
2026-05-04T10:19:47.708+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-er-model-update resolved=~/.openclaw/workspace/skills/fsi-er-model-update
2026-05-04T10:19:47.709+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-er-morning-note resolved=~/.openclaw/workspace/skills/fsi-er-morning-note
2026-05-04T10:19:47.709+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-er-sector-overview resolved=~/.openclaw/workspace/skills/fsi-er-sector-overview
2026-05-04T10:19:47.710+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-er-thesis-tracker resolved=~/.openclaw/workspace/skills/fsi-er-thesis-tracker
2026-05-04T10:19:47.710+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-fa-3-statements resolved=~/.openclaw/workspace/skills/fsi-fa-3-statements
2026-05-04T10:19:47.711+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-fa-check-deck resolved=~/.openclaw/workspace/skills/fsi-fa-check-deck
2026-05-04T10:19:47.711+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-fa-check-model resolved=~/.openclaw/workspace/skills/fsi-fa-check-model
2026-05-04T10:19:47.712+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-fa-cmd-3-statements resolved=~/.openclaw/workspace/skills/fsi-fa-cmd-3-statements
2026-05-04T10:19:47.712+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-fa-cmd-check-deck resolved=~/.openclaw/workspace/skills/fsi-fa-cmd-check-deck
2026-05-04T10:19:47.712+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-fa-cmd-competitive-analysis resolved=~/.openclaw/workspace/skills/fsi-fa-cmd-competitive-analysis
2026-05-04T10:19:47.713+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-fa-cmd-comps resolved=~/.openclaw/workspace/skills/fsi-fa-cmd-comps
2026-05-04T10:19:47.713+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-fa-cmd-dcf resolved=~/.openclaw/workspace/skills/fsi-fa-cmd-dcf
2026-05-04T10:19:47.714+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-fa-cmd-debug-model resolved=~/.openclaw/workspace/skills/fsi-fa-cmd-debug-model
2026-05-04T10:19:47.714+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-fa-cmd-lbo resolved=~/.openclaw/workspace/skills/fsi-fa-cmd-lbo
2026-05-04T10:19:47.714+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-fa-cmd-ppt-template resolved=~/.openclaw/workspace/skills/fsi-fa-cmd-ppt-template
2026-05-04T10:19:47.715+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-fa-competitive-analysis resolved=~/.openclaw/workspace/skills/fsi-fa-competitive-analysis
2026-05-04T10:19:47.715+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-fa-dcf-model resolved=~/.openclaw/workspace/skills/fsi-fa-dcf-model
2026-05-04T10:19:47.716+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-fa-lbo-model resolved=~/.openclaw/workspace/skills/fsi-fa-lbo-model
2026-05-04T10:19:47.716+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-fa-ppt-template-creator resolved=~/.openclaw/workspace/skills/fsi-fa-ppt-template-creator
2026-05-04T10:19:47.717+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-fa-skill-creator resolved=~/.openclaw/workspace/skills/fsi-fa-skill-creator
2026-05-04T10:19:47.717+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-ib-buyer-list resolved=~/.openclaw/workspace/skills/fsi-ib-buyer-list
2026-05-04T10:19:47.717+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-ib-cim-builder resolved=~/.openclaw/workspace/skills/fsi-ib-cim-builder
2026-05-04T10:19:47.718+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-ib-cmd-buyer-list resolved=~/.openclaw/workspace/skills/fsi-ib-cmd-buyer-list
2026-05-04T10:19:47.718+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-ib-cmd-cim resolved=~/.openclaw/workspace/skills/fsi-ib-cmd-cim
2026-05-04T10:19:47.719+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-ib-cmd-deal-tracker resolved=~/.openclaw/workspace/skills/fsi-ib-cmd-deal-tracker
2026-05-04T10:19:47.719+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-ib-cmd-merger-model resolved=~/.openclaw/workspace/skills/fsi-ib-cmd-merger-model
2026-05-04T10:19:47.720+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-ib-cmd-one-pager resolved=~/.openclaw/workspace/skills/fsi-ib-cmd-one-pager
2026-05-04T10:19:47.720+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-ib-cmd-process-letter resolved=~/.openclaw/workspace/skills/fsi-ib-cmd-process-letter
2026-05-04T10:19:47.720+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-ib-cmd-teaser resolved=~/.openclaw/workspace/skills/fsi-ib-cmd-teaser
2026-05-04T10:19:47.721+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-ib-datapack-builder resolved=~/.openclaw/workspace/skills/fsi-ib-datapack-builder
2026-05-04T10:19:47.721+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-ib-deal-tracker resolved=~/.openclaw/workspace/skills/fsi-ib-deal-tracker
2026-05-04T10:19:47.722+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-ib-merger-model resolved=~/.openclaw/workspace/skills/fsi-ib-merger-model
2026-05-04T10:19:47.722+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-ib-pitch-deck resolved=~/.openclaw/workspace/skills/fsi-ib-pitch-deck
2026-05-04T10:19:47.722+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-ib-process-letter resolved=~/.openclaw/workspace/skills/fsi-ib-process-letter
2026-05-04T10:19:47.723+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-ib-teaser resolved=~/.openclaw/workspace/skills/fsi-ib-teaser
2026-05-04T10:19:47.723+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-lseg-bond-futures-basis resolved=~/.openclaw/workspace/skills/fsi-lseg-bond-futures-basis
2026-05-04T10:19:47.724+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-lseg-bond-relative-value resolved=~/.openclaw/workspace/skills/fsi-lseg-bond-relative-value
2026-05-04T10:19:47.724+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-lseg-cmd-analyze-bond-basis resolved=~/.openclaw/workspace/skills/fsi-lseg-cmd-analyze-bond-basis
2026-05-04T10:19:47.724+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-lseg-cmd-analyze-bond-rv resolved=~/.openclaw/workspace/skills/fsi-lseg-cmd-analyze-bond-rv
2026-05-04T10:19:47.725+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-lseg-cmd-analyze-fx-carry resolved=~/.openclaw/workspace/skills/fsi-lseg-cmd-analyze-fx-carry
2026-05-04T10:19:47.725+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-lseg-cmd-analyze-option-vol resolved=~/.openclaw/workspace/skills/fsi-lseg-cmd-analyze-option-vol
2026-05-04T10:19:47.726+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-lseg-cmd-analyze-swap-curve resolved=~/.openclaw/workspace/skills/fsi-lseg-cmd-analyze-swap-curve
2026-05-04T10:19:47.726+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-lseg-cmd-macro-rates resolved=~/.openclaw/workspace/skills/fsi-lseg-cmd-macro-rates
2026-05-04T10:19:47.726+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-lseg-cmd-research-equity resolved=~/.openclaw/workspace/skills/fsi-lseg-cmd-research-equity
2026-05-04T10:19:47.727+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-lseg-cmd-review-fi-portfolio resolved=~/.openclaw/workspace/skills/fsi-lseg-cmd-review-fi-portfolio
2026-05-04T10:19:47.727+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-lseg-equity-research resolved=~/.openclaw/workspace/skills/fsi-lseg-equity-research
2026-05-04T10:19:47.728+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-lseg-fixed-income-portfolio resolved=~/.openclaw/workspace/skills/fsi-lseg-fixed-income-portfolio
2026-05-04T10:19:47.728+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-lseg-fx-carry-trade resolved=~/.openclaw/workspace/skills/fsi-lseg-fx-carry-trade
2026-05-04T10:19:47.728+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-lseg-macro-rates-monitor resolved=~/.openclaw/workspace/skills/fsi-lseg-macro-rates-monitor
2026-05-04T10:19:47.729+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-lseg-option-vol-analysis resolved=~/.openclaw/workspace/skills/fsi-lseg-option-vol-analysis
2026-05-04T10:19:47.729+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-lseg-swap-curve-strategy resolved=~/.openclaw/workspace/skills/fsi-lseg-swap-curve-strategy
2026-05-04T10:19:47.730+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-pe-cmd-dd-checklist resolved=~/.openclaw/workspace/skills/fsi-pe-cmd-dd-checklist
2026-05-04T10:19:47.730+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-pe-cmd-dd-prep resolved=~/.openclaw/workspace/skills/fsi-pe-cmd-dd-prep
2026-05-04T10:19:47.730+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-pe-cmd-ic-memo resolved=~/.openclaw/workspace/skills/fsi-pe-cmd-ic-memo
2026-05-04T10:19:47.731+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-pe-cmd-portfolio resolved=~/.openclaw/workspace/skills/fsi-pe-cmd-portfolio
2026-05-04T10:19:47.731+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-pe-cmd-returns resolved=~/.openclaw/workspace/skills/fsi-pe-cmd-returns
2026-05-04T10:19:47.732+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-pe-cmd-screen-deal resolved=~/.openclaw/workspace/skills/fsi-pe-cmd-screen-deal
2026-05-04T10:19:47.732+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-pe-cmd-source resolved=~/.openclaw/workspace/skills/fsi-pe-cmd-source
2026-05-04T10:19:47.732+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-pe-cmd-unit-economics resolved=~/.openclaw/workspace/skills/fsi-pe-cmd-unit-economics
2026-05-04T10:19:47.733+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-pe-cmd-value-creation resolved=~/.openclaw/workspace/skills/fsi-pe-cmd-value-creation
2026-05-04T10:19:47.733+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-pe-deal-screening resolved=~/.openclaw/workspace/skills/fsi-pe-deal-screening
2026-05-04T10:19:47.733+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-pe-deal-sourcing resolved=~/.openclaw/workspace/skills/fsi-pe-deal-sourcing
2026-05-04T10:19:47.734+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-pe-diligence-meeting-prep resolved=~/.openclaw/workspace/skills/fsi-pe-diligence-meeting-prep
2026-05-04T10:19:47.734+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-pe-due-diligence-checklist resolved=~/.openclaw/workspace/skills/fsi-pe-due-diligence-checklist
2026-05-04T10:19:47.735+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-pe-investment-committee-memo resolved=~/.openclaw/workspace/skills/fsi-pe-investment-committee-memo
2026-05-04T10:19:47.735+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-pe-portfolio-monitoring resolved=~/.openclaw/workspace/skills/fsi-pe-portfolio-monitoring
2026-05-04T10:19:47.736+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-pe-returns-analysis resolved=~/.openclaw/workspace/skills/fsi-pe-returns-analysis
2026-05-04T10:19:47.736+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-pe-unit-economics-analysis resolved=~/.openclaw/workspace/skills/fsi-pe-unit-economics-analysis
2026-05-04T10:19:47.736+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-pe-value-creation-plan resolved=~/.openclaw/workspace/skills/fsi-pe-value-creation-plan
2026-05-04T10:19:47.737+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-spg-earnings-preview-single resolved=~/.openclaw/workspace/skills/fsi-spg-earnings-preview-single
2026-05-04T10:19:47.737+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-spg-funding-digest resolved=~/.openclaw/workspace/skills/fsi-spg-funding-digest
2026-05-04T10:19:47.737+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-spg-tear-sheet resolved=~/.openclaw/workspace/skills/fsi-spg-tear-sheet
2026-05-04T10:19:47.738+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-strip-profile resolved=~/.openclaw/workspace/skills/fsi-strip-profile
2026-05-04T10:19:47.738+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-wm-client-report resolved=~/.openclaw/workspace/skills/fsi-wm-client-report
2026-05-04T10:19:47.739+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-wm-client-review-prep resolved=~/.openclaw/workspace/skills/fsi-wm-client-review-prep
2026-05-04T10:19:47.739+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-wm-cmd-client-report resolved=~/.openclaw/workspace/skills/fsi-wm-cmd-client-report
2026-05-04T10:19:47.739+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-wm-cmd-client-review resolved=~/.openclaw/workspace/skills/fsi-wm-cmd-client-review
2026-05-04T10:19:47.740+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-wm-cmd-financial-plan resolved=~/.openclaw/workspace/skills/fsi-wm-cmd-financial-plan
2026-05-04T10:19:47.740+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-wm-cmd-proposal resolved=~/.openclaw/workspace/skills/fsi-wm-cmd-proposal
2026-05-04T10:19:47.741+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-wm-cmd-rebalance resolved=~/.openclaw/workspace/skills/fsi-wm-cmd-rebalance
2026-05-04T10:19:47.741+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-wm-cmd-tlh resolved=~/.openclaw/workspace/skills/fsi-wm-cmd-tlh
2026-05-04T10:19:47.741+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-wm-financial-plan resolved=~/.openclaw/workspace/skills/fsi-wm-financial-plan
2026-05-04T10:19:47.742+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-wm-investment-proposal resolved=~/.openclaw/workspace/skills/fsi-wm-investment-proposal
2026-05-04T10:19:47.742+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-wm-portfolio-rebalance resolved=~/.openclaw/workspace/skills/fsi-wm-portfolio-rebalance
2026-05-04T10:19:47.743+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/fsi-wm-tax-loss-harvesting resolved=~/.openclaw/workspace/skills/fsi-wm-tax-loss-harvesting
2026-05-04T10:19:47.743+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/funding-rate resolved=~/.openclaw/workspace/skills/funding-rate
2026-05-04T10:19:47.743+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/github resolved=~/.openclaw/workspace/skills/github
2026-05-04T10:19:47.744+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/golang-patterns resolved=~/.openclaw/workspace/skills/golang-patterns
2026-05-04T10:19:47.744+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/golang-testing resolved=~/.openclaw/workspace/skills/golang-testing
2026-05-04T10:19:47.745+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/healthcheck resolved=~/.openclaw/workspace/skills/healthcheck
2026-05-04T10:19:47.745+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/image_recognizer resolved=~/.openclaw/workspace/skills/image_recognizer
2026-05-04T10:19:47.745+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/inventory-demand-planning resolved=~/.openclaw/workspace/skills/inventory-demand-planning
2026-05-04T10:19:47.746+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/investor-materials resolved=~/.openclaw/workspace/skills/investor-materials
2026-05-04T10:19:47.747+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/investor-outreach resolved=~/.openclaw/workspace/skills/investor-outreach
2026-05-04T10:19:47.747+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/iterative-retrieval resolved=~/.openclaw/workspace/skills/iterative-retrieval
2026-05-04T10:19:47.748+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/java-coding-standards resolved=~/.openclaw/workspace/skills/java-coding-standards
2026-05-04T10:19:47.748+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/jpa-patterns resolved=~/.openclaw/workspace/skills/jpa-patterns
2026-05-04T10:19:47.749+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/json resolved=~/.openclaw/workspace/skills/json
2026-05-04T10:19:47.749+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/kotlin-coroutines-flows resolved=~/.openclaw/workspace/skills/kotlin-coroutines-flows
2026-05-04T10:19:47.749+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/kotlin-exposed-patterns resolved=~/.openclaw/workspace/skills/kotlin-exposed-patterns
2026-05-04T10:19:47.750+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/kotlin-ktor-patterns resolved=~/.openclaw/workspace/skills/kotlin-ktor-patterns
2026-05-04T10:19:47.750+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/kotlin-patterns resolved=~/.openclaw/workspace/skills/kotlin-patterns
2026-05-04T10:19:47.750+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/kotlin-testing resolved=~/.openclaw/workspace/skills/kotlin-testing
2026-05-04T10:19:47.751+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/lenovo-smart-retail resolved=~/.openclaw/workspace/skills/lenovo-smart-retail
2026-05-04T10:19:47.751+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/lenovo_cli_system resolved=~/.openclaw/workspace/skills/lenovo_cli_system
2026-05-04T10:19:47.752+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/liquid-glass-design resolved=~/.openclaw/workspace/skills/liquid-glass-design
2026-05-04T10:19:47.752+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/logging resolved=~/.openclaw/workspace/skills/logging
2026-05-04T10:19:47.752+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/logistics-exception-management resolved=~/.openclaw/workspace/skills/logistics-exception-management
2026-05-04T10:19:47.753+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/market-research resolved=~/.openclaw/workspace/skills/market-research
2026-05-04T10:19:47.753+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/minimax-mcp-tools resolved=~/.openclaw/workspace/skills/minimax-mcp-tools
2026-05-04T10:19:47.754+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/multi-tf resolved=~/.openclaw/workspace/skills/multi-tf
2026-05-04T10:19:47.754+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/nanoclaw-repl resolved=~/.openclaw/workspace/skills/nanoclaw-repl
2026-05-04T10:19:47.754+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/news-alert resolved=~/.openclaw/workspace/skills/news-alert
2026-05-04T10:19:47.755+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/nutrient-document-processing resolved=~/.openclaw/workspace/skills/nutrient-document-processing
2026-05-04T10:19:47.755+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/obsidian resolved=~/.openclaw/workspace/skills/obsidian
2026-05-04T10:19:47.756+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/openclaw-excalidraw-diagrams resolved=~/.openclaw/workspace/skills/openclaw-excalidraw-diagrams
2026-05-04T10:19:47.756+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/openclaw-skill-polymarket-quant resolved=~/.openclaw/workspace/skills/openclaw-skill-polymarket-quant
2026-05-04T10:19:47.756+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/openclaw-trading-assistant resolved=~/.openclaw/workspace/skills/openclaw-trading-assistant
2026-05-04T10:19:47.757+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/paddle_ocr resolved=~/.openclaw/workspace/skills/paddle_ocr
2026-05-04T10:19:47.757+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/pdf resolved=~/.openclaw/workspace/skills/pdf
2026-05-04T10:19:47.757+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/perl-patterns resolved=~/.openclaw/workspace/skills/perl-patterns
2026-05-04T10:19:47.758+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/perl-security resolved=~/.openclaw/workspace/skills/perl-security
2026-05-04T10:19:47.758+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/perl-testing resolved=~/.openclaw/workspace/skills/perl-testing
2026-05-04T10:19:47.759+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/plankton-code-quality resolved=~/.openclaw/workspace/skills/plankton-code-quality
2026-05-04T10:19:47.759+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/postgres-patterns resolved=~/.openclaw/workspace/skills/postgres-patterns
2026-05-04T10:19:47.759+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/pptx resolved=~/.openclaw/workspace/skills/pptx
2026-05-04T10:19:47.760+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/proactive-agent-skill resolved=~/.openclaw/workspace/skills/proactive-agent-skill
2026-05-04T10:19:47.760+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/production-scheduling resolved=~/.openclaw/workspace/skills/production-scheduling
2026-05-04T10:19:47.761+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/project-guidelines-example resolved=~/.openclaw/workspace/skills/project-guidelines-example
2026-05-04T10:19:47.761+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/prompt-optimizer resolved=~/.openclaw/workspace/skills/prompt-optimizer
2026-05-04T10:19:47.762+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/python-patterns resolved=~/.openclaw/workspace/skills/python-patterns
2026-05-04T10:19:47.762+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/python-testing resolved=~/.openclaw/workspace/skills/python-testing
2026-05-04T10:19:47.763+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/quality-nonconformance resolved=~/.openclaw/workspace/skills/quality-nonconformance
2026-05-04T10:19:47.763+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/quantitative-realtime resolved=~/.openclaw/workspace/skills/quantitative-realtime
2026-05-04T10:19:47.764+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/ralphinho-rfc-pipeline resolved=~/.openclaw/workspace/skills/ralphinho-rfc-pipeline
2026-05-04T10:19:47.764+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/regex-vs-llm-structured-text resolved=~/.openclaw/workspace/skills/regex-vs-llm-structured-text
2026-05-04T10:19:47.764+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/rest-api resolved=~/.openclaw/workspace/skills/rest-api
2026-05-04T10:19:47.765+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/returns-reverse-logistics resolved=~/.openclaw/workspace/skills/returns-reverse-logistics
2026-05-04T10:19:47.765+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/search-first resolved=~/.openclaw/workspace/skills/search-first
2026-05-04T10:19:47.766+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/security-review resolved=~/.openclaw/workspace/skills/security-review
2026-05-04T10:19:47.766+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/security-scan resolved=~/.openclaw/workspace/skills/security-scan
2026-05-04T10:19:47.767+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/self-improving-agent resolved=~/.openclaw/workspace/skills/self-improving-agent
2026-05-04T10:19:47.767+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/skill-stocktake resolved=~/.openclaw/workspace/skills/skill-stocktake
2026-05-04T10:19:47.767+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/springboot-patterns resolved=~/.openclaw/workspace/skills/springboot-patterns
2026-05-04T10:19:47.768+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/springboot-security resolved=~/.openclaw/workspace/skills/springboot-security
2026-05-04T10:19:47.768+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/springboot-tdd resolved=~/.openclaw/workspace/skills/springboot-tdd
2026-05-04T10:19:47.768+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/springboot-verification resolved=~/.openclaw/workspace/skills/springboot-verification
2026-05-04T10:19:47.769+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/sqlite resolved=~/.openclaw/workspace/skills/sqlite
2026-05-04T10:19:47.769+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/strategic-compact resolved=~/.openclaw/workspace/skills/strategic-compact
2026-05-04T10:19:47.770+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/summarize resolved=~/.openclaw/workspace/skills/summarize
2026-05-04T10:19:47.770+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/swift-actor-persistence resolved=~/.openclaw/workspace/skills/swift-actor-persistence
2026-05-04T10:19:47.770+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/swift-concurrency-6-2 resolved=~/.openclaw/workspace/skills/swift-concurrency-6-2
2026-05-04T10:19:47.771+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/swift-protocol-di-testing resolved=~/.openclaw/workspace/skills/swift-protocol-di-testing
2026-05-04T10:19:47.771+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/swiftui-patterns resolved=~/.openclaw/workspace/skills/swiftui-patterns
2026-05-04T10:19:47.772+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/ta-lib resolved=~/.openclaw/workspace/skills/ta-lib
2026-05-04T10:19:47.772+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/tdd-workflow resolved=~/.openclaw/workspace/skills/tdd-workflow
2026-05-04T10:19:47.772+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/telegram resolved=~/.openclaw/workspace/skills/telegram
2026-05-04T10:19:47.773+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/tianlu-trader resolved=~/.openclaw/workspace/skills/tianlu-trader
2026-05-04T10:19:47.773+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/trade-analyzer resolved=~/.openclaw/workspace/skills/trade-analyzer
2026-05-04T10:19:47.774+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/trading-analysis resolved=~/.openclaw/workspace/skills/trading-analysis
2026-05-04T10:19:47.774+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/turix-cua-skill resolved=~/.openclaw/workspace/skills/turix-cua-skill
2026-05-04T10:19:47.775+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/twitter-monitor resolved=~/.openclaw/workspace/skills/twitter-monitor
2026-05-04T10:19:47.775+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/verification-loop resolved=~/.openclaw/workspace/skills/verification-loop
2026-05-04T10:19:47.775+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/video-editing resolved=~/.openclaw/workspace/skills/video-editing
2026-05-04T10:19:47.776+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/videodb resolved=~/.openclaw/workspace/skills/videodb
2026-05-04T10:19:47.776+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/visa-doc-translate resolved=~/.openclaw/workspace/skills/visa-doc-translate
2026-05-04T10:19:47.777+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/weather resolved=~/.openclaw/workspace/skills/weather
2026-05-04T10:19:47.777+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/wechat-mac resolved=~/.openclaw/workspace/skills/wechat-mac
2026-05-04T10:19:47.778+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/wechat-web-login resolved=~/.openclaw/workspace/skills/wechat-web-login
2026-05-04T10:19:47.778+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/wechat_web resolved=~/.openclaw/workspace/skills/wechat_web
2026-05-04T10:19:47.779+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/x-api resolved=~/.openclaw/workspace/skills/x-api
2026-05-04T10:19:47.779+08:00 [skills] Skipping escaped skill path outside its configured root: source=openclaw-workspace root=~/.openclaw/workspace-shangshu/skills reason=symlink-escape requested=~/.openclaw/workspace-shangshu/skills/xlsx resolved=~/.openclaw/workspace/skills/xlsx
2026-05-04T10:20:09.969+08:00 [diagnostic] liveness warning: reasons=event_loop_delay interval=45s eventLoopDelayP99Ms=115.9 eventLoopDelayMaxMs=22162.7 eventLoopUtilization=0.839 cpuCoreRatio=0.819 active=0 waiting=0 queued=0
2026-05-04T10:20:18.666+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=3baf9253-f5a1-4d91-8989-7a4f23828b28 sessionId=4cdd49e4-4f44-4571-8960-baf95f5e00c5 phase=attempt-dispatch totalMs=17559 stages=workspace:0ms@0ms,runtime-plugins:5ms@5ms,hooks:0ms@5ms,model-resolution:1816ms@1821ms,auth:7025ms@8846ms,context-engine:0ms@8846ms,attempt-dispatch:8713ms@17559ms
2026-05-04T10:20:18.696+08:00 [ws] closed before connect conn=ebc1398c-00ec-48d0-9cb6-a4ad46607137 peer=127.0.0.1:53615->127.0.0.1:18789 remote=127.0.0.1 fwd=n/a origin=n/a host=127.0.0.1:18789 ua=n/a code=1006 reason=n/a
2026-05-04T10:21:23.103+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=3baf9253-f5a1-4d91-8989-7a4f23828b28 sessionId=4cdd49e4-4f44-4571-8960-baf95f5e00c5 phase=stream-ready totalMs=64413 stages=workspace-sandbox:8ms@8ms,skills:0ms@8ms,core-plugin-tools:9545ms@9553ms,bootstrap-context:6433ms@15986ms,bundle-tools:12377ms@28363ms,system-prompt:19544ms@47907ms,session-resource-loader:2201ms@50108ms,agent-session:0ms@50108ms,stream-setup:14305ms@64413ms
[session-write-lock] releasing lock held for 60695ms (max=15000ms): /Users/luxiangnan/.openclaw/agents/tianlu/sessions/sessions.json.lock
2026-05-04T10:21:48.088+08:00 [agent/embedded] agent cleanup timed out: runId=3baf9253-f5a1-4d91-8989-7a4f23828b28 sessionId=4cdd49e4-4f44-4571-8960-baf95f5e00c5 step=pi-trajectory-flush timeoutMs=10000
2026-05-04T10:21:55.977+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=3cacff9e-6223-4dc3-b7fd-f70e898eb182 sessionId=3cacff9e-6223-4dc3-b7fd-f70e898eb182 phase=attempt-dispatch totalMs=16565 stages=workspace:0ms@0ms,runtime-plugins:3ms@3ms,hooks:0ms@3ms,model-resolution:1746ms@1749ms,auth:6835ms@8584ms,context-engine:0ms@8584ms,attempt-dispatch:7980ms@16564ms
2026-05-04T10:22:36.972+08:00 [diagnostic] liveness warning: reasons=event_loop_delay,event_loop_utilization interval=32s eventLoopDelayP99Ms=4190.1 eventLoopDelayMaxMs=4190.1 eventLoopUtilization=1 cpuCoreRatio=0.689 active=0 waiting=0 queued=0
2026-05-04T10:22:56.026+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=3cacff9e-6223-4dc3-b7fd-f70e898eb182 sessionId=3cacff9e-6223-4dc3-b7fd-f70e898eb182 phase=stream-ready totalMs=60047 stages=workspace-sandbox:757ms@757ms,skills:0ms@757ms,core-plugin-tools:4295ms@5052ms,bootstrap-context:4079ms@9131ms,bundle-tools:9177ms@18308ms,system-prompt:21822ms@40130ms,session-resource-loader:2603ms@42733ms,agent-session:1ms@42734ms,stream-setup:17313ms@60047ms
2026-05-04T10:23:08.556+08:00 [ws] closed before connect conn=f4bdd917-3a44-471e-a223-21f130a64f05 peer=127.0.0.1:49333->127.0.0.1:18789 remote=127.0.0.1 fwd=n/a origin=n/a host=127.0.0.1:18789 ua=n/a code=1006 reason=n/a
2026-05-04T10:23:30.178+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=94e8d612-7be8-4eb9-a3b9-5c2947b81ae9 sessionId=94e8d612-7be8-4eb9-a3b9-5c2947b81ae9 phase=attempt-dispatch totalMs=16023 stages=workspace:0ms@0ms,runtime-plugins:1ms@1ms,hooks:0ms@1ms,model-resolution:1846ms@1847ms,auth:6755ms@8602ms,context-engine:0ms@8602ms,attempt-dispatch:7421ms@16023ms
2026-05-04T10:24:33.350+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=94e8d612-7be8-4eb9-a3b9-5c2947b81ae9 sessionId=94e8d612-7be8-4eb9-a3b9-5c2947b81ae9 phase=stream-ready totalMs=63168 stages=workspace-sandbox:21ms@21ms,skills:1ms@22ms,core-plugin-tools:4228ms@4250ms,bootstrap-context:2ms@4252ms,bundle-tools:6145ms@10397ms,system-prompt:22720ms@33117ms,session-resource-loader:2366ms@35483ms,agent-session:2ms@35485ms,stream-setup:27683ms@63168ms
2026-05-04T10:24:46.907+08:00 [diagnostic] liveness warning: reasons=event_loop_delay,event_loop_utilization interval=51s eventLoopDelayP99Ms=41875.9 eventLoopDelayMaxMs=41875.9 eventLoopUtilization=1 cpuCoreRatio=0.674 active=1 waiting=0 queued=0
2026-05-04T10:26:22.267+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=189e4e1a-ce58-4a79-a4ed-69b3e23c82a2 sessionId=4cdd49e4-4f44-4571-8960-baf95f5e00c5 phase=attempt-dispatch totalMs=17554 stages=workspace:0ms@0ms,runtime-plugins:4ms@4ms,hooks:0ms@4ms,model-resolution:1794ms@1798ms,auth:7405ms@9203ms,context-engine:0ms@9203ms,attempt-dispatch:8351ms@17554ms
2026-05-04T10:26:22.369+08:00 [ws] closed before connect conn=2781cb2d-9df5-475a-adba-17d2b14dc188 peer=127.0.0.1:61723->127.0.0.1:18789 remote=127.0.0.1 fwd=n/a origin=n/a host=127.0.0.1:18789 ua=n/a code=1006 reason=n/a
2026-05-04T10:26:49.420+08:00 [diagnostic] liveness warning: reasons=event_loop_delay,event_loop_utilization,cpu interval=36s eventLoopDelayP99Ms=18689.8 eventLoopDelayMaxMs=18689.8 eventLoopUtilization=1 cpuCoreRatio=0.985 active=0 waiting=0 queued=0
2026-05-04T10:27:20.396+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=189e4e1a-ce58-4a79-a4ed-69b3e23c82a2 sessionId=4cdd49e4-4f44-4571-8960-baf95f5e00c5 phase=stream-ready totalMs=58124 stages=workspace-sandbox:400ms@400ms,skills:0ms@400ms,core-plugin-tools:4453ms@4853ms,bootstrap-context:3619ms@8472ms,bundle-tools:6009ms@14481ms,system-prompt:18390ms@32871ms,session-resource-loader:3925ms@36796ms,agent-session:27ms@36823ms,stream-setup:21301ms@58124ms
2026-05-04T10:28:12.723+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=2f24ac31-607e-4a3c-a7b9-d776bd0fd7a6 sessionId=f92074f9-874e-4a4e-9ed9-103587002013 phase=attempt-dispatch totalMs=17408 stages=workspace:0ms@0ms,runtime-plugins:4ms@4ms,hooks:0ms@4ms,model-resolution:2011ms@2015ms,auth:7498ms@9513ms,context-engine:0ms@9513ms,attempt-dispatch:7895ms@17408ms
2026-05-04T10:28:12.726+08:00 [ws] closed before connect conn=e65679ea-eebf-4950-b66a-336069552895 peer=127.0.0.1:53027->127.0.0.1:18789 remote=127.0.0.1 fwd=n/a origin=n/a host=127.0.0.1:18789 ua=n/a code=1006 reason=n/a
2026-05-04T10:29:11.303+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=2f24ac31-607e-4a3c-a7b9-d776bd0fd7a6 sessionId=f92074f9-874e-4a4e-9ed9-103587002013 phase=stream-ready totalMs=58539 stages=workspace-sandbox:411ms@411ms,skills:0ms@411ms,core-plugin-tools:4284ms@4695ms,bootstrap-context:4ms@4699ms,bundle-tools:6510ms@11209ms,system-prompt:24953ms@36162ms,session-resource-loader:3105ms@39267ms,agent-session:29ms@39296ms,stream-setup:19243ms@58539ms
2026-05-04T10:29:24.015+08:00 [diagnostic] liveness warning: reasons=event_loop_delay,event_loop_utilization interval=41s eventLoopDelayP99Ms=32833 eventLoopDelayMaxMs=32833 eventLoopUtilization=1 cpuCoreRatio=0.816 active=1 waiting=0 queued=0
2026-05-04T10:29:24.196+08:00 [ws] closed before connect conn=dec2970e-12c6-4607-b24b-ebcaa0c2d13d peer=127.0.0.1:57416->127.0.0.1:18789 remote=127.0.0.1 fwd=n/a origin=n/a host=127.0.0.1:18789 ua=n/a code=1006 reason=n/a
2026-05-04T10:30:07.802+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=911af39c-0f72-4d91-b8b3-45c314fc44cb sessionId=7c3ccd8e-0ce6-4b13-8461-bf5eb8585c42 phase=attempt-dispatch totalMs=17629 stages=workspace:0ms@0ms,runtime-plugins:4ms@4ms,hooks:0ms@4ms,model-resolution:2006ms@2010ms,auth:7239ms@9249ms,context-engine:0ms@9249ms,attempt-dispatch:8380ms@17629ms
2026-05-04T10:30:07.902+08:00 [ws] closed before connect conn=568c0d45-914c-4475-b874-df31c6f77ccd peer=127.0.0.1:60581->127.0.0.1:18789 remote=127.0.0.1 fwd=n/a origin=n/a host=127.0.0.1:18789 ua=n/a code=1006 reason=n/a
2026-05-04T10:31:18.824+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=911af39c-0f72-4d91-b8b3-45c314fc44cb sessionId=7c3ccd8e-0ce6-4b13-8461-bf5eb8585c42 phase=stream-ready totalMs=71015 stages=workspace-sandbox:375ms@375ms,skills:1ms@376ms,core-plugin-tools:5024ms@5400ms,bootstrap-context:6606ms@12006ms,bundle-tools:17165ms@29171ms,system-prompt:23269ms@52440ms,session-resource-loader:3804ms@56244ms,agent-session:23ms@56267ms,stream-setup:14748ms@71015ms
[session-write-lock] releasing lock held for 71666ms (max=15000ms): /Users/luxiangnan/.openclaw/agents/tianlu/sessions/sessions.json.lock
2026-05-04T10:31:31.269+08:00 [diagnostic] liveness warning: reasons=event_loop_delay,event_loop_utilization,cpu interval=35s eventLoopDelayP99Ms=28638.7 eventLoopDelayMaxMs=28638.7 eventLoopUtilization=1 cpuCoreRatio=0.956 active=1 waiting=0 queued=0
2026-05-04T10:31:52.862+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=325ee8aa-9179-4172-825b-bef585198956 sessionId=325ee8aa-9179-4172-825b-bef585198956 phase=attempt-dispatch totalMs=17174 stages=workspace:0ms@0ms,runtime-plugins:3ms@3ms,hooks:0ms@3ms,model-resolution:1842ms@1845ms,auth:7178ms@9023ms,context-engine:0ms@9023ms,attempt-dispatch:8151ms@17174ms
2026-05-04T10:32:28.109+08:00 [agent/embedded] agent cleanup timed out: runId=911af39c-0f72-4d91-b8b3-45c314fc44cb sessionId=7c3ccd8e-0ce6-4b13-8461-bf5eb8585c42 step=pi-trajectory-flush timeoutMs=10000
[session-write-lock] releasing lock held for 33870ms (max=15000ms): /Users/luxiangnan/.openclaw/agents/menxia/sessions/sessions.json.lock
2026-05-04T10:32:58.578+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=325ee8aa-9179-4172-825b-bef585198956 sessionId=325ee8aa-9179-4172-825b-bef585198956 phase=stream-ready totalMs=65711 stages=workspace-sandbox:798ms@798ms,skills:1ms@799ms,core-plugin-tools:4214ms@5013ms,bootstrap-context:4292ms@9305ms,bundle-tools:7211ms@16516ms,system-prompt:25768ms@42284ms,session-resource-loader:1672ms@43956ms,agent-session:2ms@43958ms,stream-setup:21753ms@65711ms
2026-05-04T10:33:12.483+08:00 [ws] closed before connect conn=a3a0d40e-16e9-44d4-9ebd-44354d08a715 peer=127.0.0.1:56330->127.0.0.1:18789 remote=127.0.0.1 fwd=n/a origin=n/a host=127.0.0.1:18789 ua=n/a code=1006 reason=n/a
2026-05-04T10:33:44.239+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=7ac053bb-baf0-45c1-9106-62e80291e183 sessionId=7ac053bb-baf0-45c1-9106-62e80291e183 phase=attempt-dispatch totalMs=16282 stages=workspace:0ms@0ms,runtime-plugins:1ms@1ms,hooks:0ms@1ms,model-resolution:1805ms@1806ms,auth:6858ms@8664ms,context-engine:0ms@8664ms,attempt-dispatch:7618ms@16282ms
2026-05-04T10:33:44.270+08:00 [diagnostic] liveness warning: reasons=event_loop_delay,event_loop_utilization,cpu interval=32s eventLoopDelayP99Ms=498.9 eventLoopDelayMaxMs=8766.1 eventLoopUtilization=0.999 cpuCoreRatio=1.014 active=0 waiting=0 queued=0
2026-05-04T10:34:09.792+08:00 [ws] closed before connect conn=b315db9e-3a9e-49d7-9712-d594d339a0de peer=127.0.0.1:60431->127.0.0.1:18789 remote=127.0.0.1 fwd=n/a origin=n/a host=127.0.0.1:18789 ua=n/a code=1006 reason=n/a
2026-05-04T10:34:40.812+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=7ac053bb-baf0-45c1-9106-62e80291e183 sessionId=7ac053bb-baf0-45c1-9106-62e80291e183 phase=stream-ready totalMs=56523 stages=workspace-sandbox:39ms@39ms,skills:4ms@43ms,core-plugin-tools:4349ms@4392ms,bootstrap-context:3ms@4395ms,bundle-tools:6290ms@10685ms,system-prompt:17937ms@28622ms,session-resource-loader:5108ms@33730ms,agent-session:29ms@33759ms,stream-setup:22764ms@56523ms
2026-05-04T10:36:30.454+08:00 [diagnostic] liveness warning: reasons=event_loop_delay interval=67s eventLoopDelayP99Ms=111.4 eventLoopDelayMaxMs=47546.6 eventLoopUtilization=0.829 cpuCoreRatio=0.431 active=0 waiting=0 queued=0
2026-05-04T10:36:30.465+08:00 [plugins] [openclaw] Tick timeout (67202ms since last tick), closing connection
2026-05-04T10:36:38.659+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=57629889-7855-421d-b88a-3281bb39a090 sessionId=d7c4da47-5bbf-469b-b2b1-4c80d92f7fa2 phase=attempt-dispatch totalMs=19853 stages=workspace:1ms@1ms,runtime-plugins:20ms@21ms,hooks:0ms@21ms,model-resolution:3826ms@3847ms,auth:7768ms@11615ms,context-engine:0ms@11615ms,attempt-dispatch:8238ms@19853ms
2026-05-04T10:37:06.915+08:00 [ws] closed before connect conn=f5a8be3c-dd39-4b58-84b0-52b2dbd984a1 peer=127.0.0.1:55978->127.0.0.1:18789 remote=127.0.0.1 fwd=n/a origin=n/a host=127.0.0.1:18789 ua=n/a code=1006 reason=n/a
2026-05-04T10:37:27.278+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=57629889-7855-421d-b88a-3281bb39a090 sessionId=d7c4da47-5bbf-469b-b2b1-4c80d92f7fa2 phase=stream-ready totalMs=48306 stages=workspace-sandbox:352ms@352ms,skills:1ms@353ms,core-plugin-tools:4153ms@4506ms,bootstrap-context:5512ms@10018ms,bundle-tools:6210ms@16228ms,system-prompt:15102ms@31330ms,session-resource-loader:2232ms@33562ms,agent-session:0ms@33562ms,stream-setup:14744ms@48306ms
[tools] read failed: ENOENT: no such file or directory, access '/Users/luxiangnan/edict/pending_approvals.json' raw_params={"path":"/Users/luxiangnan/edict/pending_approvals.json"}
2026-05-04T10:38:32.457+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=67b58b04-af55-4963-9982-a1427de42428 sessionId=7c3ccd8e-0ce6-4b13-8461-bf5eb8585c42 phase=attempt-dispatch totalMs=17829 stages=workspace:0ms@0ms,runtime-plugins:4ms@4ms,hooks:0ms@4ms,model-resolution:1950ms@1954ms,auth:7564ms@9518ms,context-engine:1ms@9519ms,attempt-dispatch:8310ms@17829ms
2026-05-04T10:39:05.119+08:00 [diagnostic] liveness warning: reasons=event_loop_delay,event_loop_utilization interval=40s eventLoopDelayP99Ms=22280.1 eventLoopDelayMaxMs=22280.1 eventLoopUtilization=1 cpuCoreRatio=0.896 active=0 waiting=0 queued=0
2026-05-04T10:39:05.323+08:00 [ws] closed before connect conn=5ea7ebc7-2ba1-4698-bf11-84e6554b7df8 peer=127.0.0.1:64260->127.0.0.1:18789 remote=127.0.0.1 fwd=n/a origin=n/a host=127.0.0.1:18789 ua=n/a code=1006 reason=n/a
2026-05-04T10:39:26.250+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=67b58b04-af55-4963-9982-a1427de42428 sessionId=7c3ccd8e-0ce6-4b13-8461-bf5eb8585c42 phase=stream-ready totalMs=53790 stages=workspace-sandbox:3ms@3ms,skills:1ms@4ms,core-plugin-tools:10037ms@10041ms,bootstrap-context:9ms@10050ms,bundle-tools:9101ms@19151ms,system-prompt:16705ms@35856ms,session-resource-loader:2195ms@38051ms,agent-session:1ms@38052ms,stream-setup:15738ms@53790ms
2026-05-04T10:40:26.497+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=5782c754-a146-4d4c-a34a-ff9c85ef18d5 sessionId=5782c754-a146-4d4c-a34a-ff9c85ef18d5 phase=attempt-dispatch totalMs=23589 stages=workspace:0ms@0ms,runtime-plugins:3ms@3ms,hooks:0ms@3ms,model-resolution:2020ms@2023ms,auth:13309ms@15332ms,context-engine:1ms@15333ms,attempt-dispatch:8256ms@23589ms
2026-05-04T10:41:15.213+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=5782c754-a146-4d4c-a34a-ff9c85ef18d5 sessionId=5782c754-a146-4d4c-a34a-ff9c85ef18d5 phase=stream-ready totalMs=48670 stages=workspace-sandbox:544ms@544ms,skills:0ms@544ms,core-plugin-tools:4283ms@4827ms,bootstrap-context:3995ms@8822ms,bundle-tools:6271ms@15093ms,system-prompt:16267ms@31360ms,session-resource-loader:1834ms@33194ms,agent-session:1ms@33195ms,stream-setup:15475ms@48670ms
2026-05-04T10:41:31.630+08:00 [diagnostic] liveness warning: reasons=event_loop_delay,event_loop_utilization interval=37s eventLoopDelayP99Ms=31927 eventLoopDelayMaxMs=31927 eventLoopUtilization=1 cpuCoreRatio=0.894 active=1 waiting=0 queued=0
2026-05-04T10:44:33.654+08:00 [diagnostic] liveness warning: reasons=event_loop_delay interval=30s eventLoopDelayP99Ms=21.8 eventLoopDelayMaxMs=1925.2 eventLoopUtilization=0.09 cpuCoreRatio=0.027 active=0 waiting=0 queued=0
2026-05-04T10:45:17.872+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=aedd9d7a-d475-4165-b424-a897151f1196 sessionId=aedd9d7a-d475-4165-b424-a897151f1196 phase=attempt-dispatch totalMs=17255 stages=workspace:0ms@0ms,runtime-plugins:1ms@1ms,hooks:0ms@1ms,model-resolution:2156ms@2157ms,auth:7528ms@9685ms,context-engine:1ms@9686ms,attempt-dispatch:7569ms@17255ms
2026-05-04T10:46:16.718+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=aedd9d7a-d475-4165-b424-a897151f1196 sessionId=aedd9d7a-d475-4165-b424-a897151f1196 phase=stream-ready totalMs=58802 stages=workspace-sandbox:8ms@8ms,skills:1ms@9ms,core-plugin-tools:4234ms@4243ms,bootstrap-context:29ms@4272ms,bundle-tools:5928ms@10200ms,system-prompt:17374ms@27574ms,session-resource-loader:3556ms@31130ms,agent-session:4ms@31134ms,stream-setup:27668ms@58802ms
2026-05-04T10:47:01.796+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=5cdf3a46-2f60-40c9-9970-f2b3522759c1 sessionId=5cdf3a46-2f60-40c9-9970-f2b3522759c1 phase=attempt-dispatch totalMs=16746 stages=workspace:0ms@0ms,runtime-plugins:1ms@1ms,hooks:0ms@1ms,model-resolution:1903ms@1904ms,auth:7286ms@9190ms,context-engine:0ms@9190ms,attempt-dispatch:7556ms@16746ms
2026-05-04T10:47:01.799+08:00 [ws] closed before connect conn=63c68e8f-d4b0-4f44-8ec7-4d0f1d27f215 peer=127.0.0.1:62497->127.0.0.1:18789 remote=127.0.0.1 fwd=n/a origin=n/a host=127.0.0.1:18789 ua=n/a code=1006 reason=n/a
2026-05-04T10:47:01.800+08:00 [diagnostic] liveness warning: reasons=event_loop_delay,event_loop_utilization,cpu interval=31s eventLoopDelayP99Ms=297 eventLoopDelayMaxMs=9286.2 eventLoopUtilization=0.999 cpuCoreRatio=1.015 active=0 waiting=0 queued=0
2026-05-04T10:47:48.125+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=5cdf3a46-2f60-40c9-9970-f2b3522759c1 sessionId=5cdf3a46-2f60-40c9-9970-f2b3522759c1 phase=stream-ready totalMs=46313 stages=workspace-sandbox:5ms@5ms,skills:0ms@5ms,core-plugin-tools:4198ms@4203ms,bootstrap-context:21ms@4224ms,bundle-tools:5828ms@10052ms,system-prompt:14971ms@25023ms,session-resource-loader:1144ms@26167ms,agent-session:0ms@26167ms,stream-setup:20146ms@46313ms
2026-05-04T10:48:05.820+08:00 [plugins] [openclaw] Tick timeout (64018ms since last tick), closing connection
2026-05-04T10:50:36.751+08:00 [diagnostic] liveness warning: reasons=event_loop_delay,event_loop_utilization,cpu interval=31s eventLoopDelayP99Ms=164.6 eventLoopDelayMaxMs=20988.3 eventLoopUtilization=1 cpuCoreRatio=1.013 active=0 waiting=0 queued=0
2026-05-04T10:50:44.308+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=5a31381b-9ddb-4c8b-a155-7095223d1824 sessionId=f92074f9-874e-4a4e-9ed9-103587002013 phase=attempt-dispatch totalMs=16288 stages=workspace:1ms@1ms,runtime-plugins:4ms@5ms,hooks:0ms@5ms,model-resolution:1790ms@1795ms,auth:6695ms@8490ms,context-engine:0ms@8490ms,attempt-dispatch:7798ms@16288ms
2026-05-04T10:51:47.625+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=5a31381b-9ddb-4c8b-a155-7095223d1824 sessionId=f92074f9-874e-4a4e-9ed9-103587002013 phase=stream-ready totalMs=63290 stages=workspace-sandbox:389ms@389ms,skills:1ms@390ms,core-plugin-tools:6418ms@6808ms,bootstrap-context:3998ms@10806ms,bundle-tools:5865ms@16671ms,system-prompt:22470ms@39141ms,session-resource-loader:1762ms@40903ms,agent-session:2ms@40905ms,stream-setup:22385ms@63290ms
2026-05-04T10:52:34.988+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=2a605751-e8d3-472d-8a65-9fb7690f9783 sessionId=4cdd49e4-4f44-4571-8960-baf95f5e00c5 phase=attempt-dispatch totalMs=17755 stages=workspace:0ms@0ms,runtime-plugins:3ms@3ms,hooks:0ms@3ms,model-resolution:1853ms@1856ms,auth:7721ms@9577ms,context-engine:0ms@9577ms,attempt-dispatch:8178ms@17755ms
2026-05-04T10:53:05.164+08:00 [ws] closed before connect conn=6998368e-622d-4f49-ac2b-9c145e955386 peer=127.0.0.1:53498->127.0.0.1:18789 remote=127.0.0.1 fwd=n/a origin=n/a host=127.0.0.1:18789 ua=n/a code=1006 reason=n/a
2026-05-04T10:53:05.433+08:00 [diagnostic] liveness warning: reasons=event_loop_delay,event_loop_utilization,cpu interval=30s eventLoopDelayP99Ms=21357.4 eventLoopDelayMaxMs=21357.4 eventLoopUtilization=1 cpuCoreRatio=0.903 active=0 waiting=0 queued=0
2026-05-04T10:53:38.351+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=2a605751-e8d3-472d-8a65-9fb7690f9783 sessionId=4cdd49e4-4f44-4571-8960-baf95f5e00c5 phase=stream-ready totalMs=63317 stages=workspace-sandbox:531ms@531ms,skills:1ms@532ms,core-plugin-tools:4496ms@5028ms,bootstrap-context:3484ms@8512ms,bundle-tools:6293ms@14805ms,system-prompt:21075ms@35880ms,session-resource-loader:2972ms@38852ms,agent-session:1ms@38853ms,stream-setup:24464ms@63317ms
2026-05-04T10:55:36.531+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=ccb4d1b2-0b75-4763-8932-78670d1eda8e sessionId=ccb4d1b2-0b75-4763-8932-78670d1eda8e phase=attempt-dispatch totalMs=22448 stages=workspace:1ms@1ms,runtime-plugins:3ms@4ms,hooks:0ms@4ms,model-resolution:1986ms@1990ms,auth:11569ms@13559ms,context-engine:0ms@13559ms,attempt-dispatch:8889ms@22448ms
2026-05-04T10:55:36.813+08:00 [diagnostic] liveness warning: reasons=event_loop_delay,event_loop_utilization interval=36s eventLoopDelayP99Ms=9059.7 eventLoopDelayMaxMs=13799.3 eventLoopUtilization=1 cpuCoreRatio=0.811 active=0 waiting=0 queued=0
2026-05-04T10:56:03.884+08:00 [ws] closed before connect conn=2eb228fe-cdf6-454f-acdc-d3ff070fdc92 peer=127.0.0.1:64589->127.0.0.1:18789 remote=127.0.0.1 fwd=n/a origin=n/a host=127.0.0.1:18789 ua=n/a code=1006 reason=n/a
2026-05-04T10:56:23.336+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=ccb4d1b2-0b75-4763-8932-78670d1eda8e sessionId=ccb4d1b2-0b75-4763-8932-78670d1eda8e phase=stream-ready totalMs=46747 stages=workspace-sandbox:496ms@496ms,skills:0ms@496ms,core-plugin-tools:4599ms@5095ms,bootstrap-context:3002ms@8097ms,bundle-tools:6341ms@14438ms,system-prompt:15844ms@30282ms,session-resource-loader:1852ms@32134ms,agent-session:1ms@32135ms,stream-setup:14612ms@46747ms
2026-05-04T11:00:15.772+08:00 [diagnostic] liveness warning: reasons=event_loop_delay interval=39s eventLoopDelayP99Ms=27.9 eventLoopDelayMaxMs=14420 eventLoopUtilization=0.411 cpuCoreRatio=0.282 active=0 waiting=0 queued=0
2026-05-04T11:00:24.123+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=cce67ae6-9079-443e-b817-fff2f2a5727f sessionId=cce67ae6-9079-443e-b817-fff2f2a5727f phase=attempt-dispatch totalMs=23027 stages=workspace:0ms@0ms,runtime-plugins:1ms@1ms,hooks:0ms@1ms,model-resolution:2101ms@2102ms,auth:12194ms@14296ms,context-engine:1ms@14297ms,attempt-dispatch:8730ms@23027ms
2026-05-04T11:01:17.077+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=cce67ae6-9079-443e-b817-fff2f2a5727f sessionId=cce67ae6-9079-443e-b817-fff2f2a5727f phase=stream-ready totalMs=52906 stages=workspace-sandbox:507ms@507ms,skills:0ms@507ms,core-plugin-tools:5137ms@5644ms,bootstrap-context:4360ms@10004ms,bundle-tools:6429ms@16433ms,system-prompt:16725ms@33158ms,session-resource-loader:1846ms@35004ms,agent-session:0ms@35004ms,stream-setup:17902ms@52906ms
2026-05-04T11:03:26.300+08:00 [diagnostic] liveness warning: reasons=event_loop_delay,event_loop_utilization interval=41s eventLoopDelayP99Ms=309.6 eventLoopDelayMaxMs=21843.9 eventLoopUtilization=0.982 cpuCoreRatio=0.629 active=0 waiting=0 queued=0
2026-05-04T11:03:37.270+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=1504c34d-b46b-4a7d-bdd4-524c439d01a2 sessionId=1504c34d-b46b-4a7d-bdd4-524c439d01a2 phase=attempt-dispatch totalMs=31979 stages=workspace:0ms@0ms,runtime-plugins:3ms@3ms,hooks:0ms@3ms,model-resolution:2611ms@2614ms,auth:18366ms@20980ms,context-engine:2ms@20982ms,attempt-dispatch:10997ms@31979ms
2026-05-04T11:04:03.107+08:00 [ws] closed before connect conn=3607bbc3-022f-4cd4-8165-a8ffbd998a52 peer=127.0.0.1:64167->127.0.0.1:18789 remote=127.0.0.1 fwd=n/a origin=n/a host=127.0.0.1:18789 ua=n/a code=1006 reason=n/a
2026-05-04T11:04:23.234+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=1504c34d-b46b-4a7d-bdd4-524c439d01a2 sessionId=1504c34d-b46b-4a7d-bdd4-524c439d01a2 phase=stream-ready totalMs=45960 stages=workspace-sandbox:34ms@34ms,skills:5ms@39ms,core-plugin-tools:5235ms@5274ms,bootstrap-context:98ms@5372ms,bundle-tools:6706ms@12078ms,system-prompt:16768ms@28846ms,session-resource-loader:1840ms@30686ms,agent-session:1ms@30687ms,stream-setup:15273ms@45960ms
2026-05-04T11:06:41.135+08:00 [diagnostic] liveness warning: reasons=event_loop_delay,event_loop_utilization,cpu interval=36s eventLoopDelayP99Ms=198 eventLoopDelayMaxMs=22934.5 eventLoopUtilization=1 cpuCoreRatio=0.961 active=0 waiting=0 queued=0
2026-05-04T11:06:54.742+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=b4777755-627f-4a2c-a303-15c3e9de4501 sessionId=d7c4da47-5bbf-469b-b2b1-4c80d92f7fa2 phase=attempt-dispatch totalMs=24033 stages=workspace:0ms@0ms,runtime-plugins:1ms@1ms,hooks:1ms@2ms,model-resolution:1861ms@1863ms,auth:8373ms@10236ms,context-engine:0ms@10236ms,attempt-dispatch:13797ms@24033ms
2026-05-04T11:07:47.988+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=b4777755-627f-4a2c-a303-15c3e9de4501 sessionId=d7c4da47-5bbf-469b-b2b1-4c80d92f7fa2 phase=stream-ready totalMs=53195 stages=workspace-sandbox:24ms@24ms,skills:1ms@25ms,core-plugin-tools:12838ms@12863ms,bootstrap-context:722ms@13585ms,bundle-tools:7892ms@21477ms,system-prompt:15700ms@37177ms,session-resource-loader:1183ms@38360ms,agent-session:4ms@38364ms,stream-setup:14831ms@53195ms
2026-05-04T11:08:00.704+08:00 [ws] closed before connect conn=5a33dd05-15af-439e-9186-f0162fd0ff34 peer=127.0.0.1:62842->127.0.0.1:18789 remote=127.0.0.1 fwd=n/a origin=n/a host=127.0.0.1:18789 ua=n/a code=1006 reason=n/a
2026-05-04T11:08:43.882+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=1bc1405a-cc73-4139-b61b-febf029bf78e sessionId=7c3ccd8e-0ce6-4b13-8461-bf5eb8585c42 phase=attempt-dispatch totalMs=27289 stages=workspace:0ms@0ms,runtime-plugins:3ms@3ms,hooks:0ms@3ms,model-resolution:1772ms@1775ms,auth:8761ms@10536ms,context-engine:1ms@10537ms,attempt-dispatch:16752ms@27289ms
2026-05-04T11:08:44.039+08:00 [diagnostic] liveness warning: reasons=event_loop_delay interval=43s eventLoopDelayP99Ms=893.9 eventLoopDelayMaxMs=22900.9 eventLoopUtilization=0.935 cpuCoreRatio=0.742 active=0 waiting=0 queued=0
2026-05-04T11:09:41.843+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=1bc1405a-cc73-4139-b61b-febf029bf78e sessionId=7c3ccd8e-0ce6-4b13-8461-bf5eb8585c42 phase=stream-ready totalMs=57950 stages=workspace-sandbox:573ms@573ms,skills:1ms@574ms,core-plugin-tools:12540ms@13114ms,bootstrap-context:5185ms@18299ms,bundle-tools:7599ms@25898ms,system-prompt:15288ms@41186ms,session-resource-loader:2349ms@43535ms,agent-session:0ms@43535ms,stream-setup:14415ms@57950ms
2026-05-04T11:10:29.486+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=4ec047f7-ba60-4041-a487-e76ebb72c62b sessionId=4ec047f7-ba60-4041-a487-e76ebb72c62b phase=attempt-dispatch totalMs=24905 stages=workspace:0ms@0ms,runtime-plugins:2ms@2ms,hooks:0ms@2ms,model-resolution:1775ms@1777ms,auth:11388ms@13165ms,context-engine:1ms@13166ms,attempt-dispatch:11739ms@24905ms
2026-05-04T11:11:04.790+08:00 [diagnostic] liveness warning: reasons=event_loop_delay,event_loop_utilization interval=35s eventLoopDelayP99Ms=22062 eventLoopDelayMaxMs=22062 eventLoopUtilization=1 cpuCoreRatio=0.825 active=0 waiting=0 queued=0
2026-05-04T11:11:04.978+08:00 [ws] closed before connect conn=9e656be2-382c-4eec-9610-5a1bbb3db51f peer=127.0.0.1:59269->127.0.0.1:18789 remote=127.0.0.1 fwd=n/a origin=n/a host=127.0.0.1:18789 ua=n/a code=1006 reason=n/a
2026-05-04T11:11:24.206+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=4ec047f7-ba60-4041-a487-e76ebb72c62b sessionId=4ec047f7-ba60-4041-a487-e76ebb72c62b phase=stream-ready totalMs=54666 stages=workspace-sandbox:1057ms@1057ms,skills:0ms@1057ms,core-plugin-tools:7819ms@8876ms,bootstrap-context:4113ms@12989ms,bundle-tools:8548ms@21537ms,system-prompt:16774ms@38311ms,session-resource-loader:1833ms@40144ms,agent-session:0ms@40144ms,stream-setup:14522ms@54666ms
2026-05-04T11:15:17.606+08:00 [diagnostic] liveness warning: reasons=event_loop_delay interval=39s eventLoopDelayP99Ms=467.7 eventLoopDelayMaxMs=12675.2 eventLoopUtilization=0.871 cpuCoreRatio=0.601 active=0 waiting=0 queued=0
2026-05-04T11:15:26.336+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=d2684226-fd2e-44de-b4f2-f5073759a885 sessionId=d2684226-fd2e-44de-b4f2-f5073759a885 phase=attempt-dispatch totalMs=21295 stages=workspace:0ms@0ms,runtime-plugins:2ms@2ms,hooks:0ms@2ms,model-resolution:1960ms@1962ms,auth:10593ms@12555ms,context-engine:0ms@12555ms,attempt-dispatch:8740ms@21295ms
2026-05-04T11:16:08.467+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=d2684226-fd2e-44de-b4f2-f5073759a885 sessionId=d2684226-fd2e-44de-b4f2-f5073759a885 phase=stream-ready totalMs=42128 stages=workspace-sandbox:4ms@4ms,skills:0ms@4ms,core-plugin-tools:4582ms@4586ms,bootstrap-context:28ms@4614ms,bundle-tools:6003ms@10617ms,system-prompt:15040ms@25657ms,session-resource-loader:2301ms@27958ms,agent-session:1ms@27959ms,stream-setup:14169ms@42128ms
2026-05-04T11:17:04.988+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=f1809ab8-4dce-4eec-a16c-90da9b861590 sessionId=f1809ab8-4dce-4eec-a16c-90da9b861590 phase=attempt-dispatch totalMs=27973 stages=workspace:0ms@0ms,runtime-plugins:1ms@1ms,hooks:0ms@1ms,model-resolution:1857ms@1858ms,auth:16998ms@18856ms,context-engine:0ms@18856ms,attempt-dispatch:9117ms@27973ms
2026-05-04T11:17:05.317+08:00 [ws] closed before connect conn=95266e53-f04c-4b2f-9da4-af6e8920448a peer=127.0.0.1:49187->127.0.0.1:18789 remote=127.0.0.1 fwd=n/a origin=n/a host=127.0.0.1:18789 ua=n/a code=1006 reason=n/a
2026-05-04T11:17:31.892+08:00 [diagnostic] liveness warning: reasons=event_loop_delay,event_loop_utilization,cpu interval=36s eventLoopDelayP99Ms=17515.4 eventLoopDelayMaxMs=17515.4 eventLoopUtilization=1 cpuCoreRatio=0.977 active=0 waiting=0 queued=0
2026-05-04T11:17:51.976+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=f1809ab8-4dce-4eec-a16c-90da9b861590 sessionId=f1809ab8-4dce-4eec-a16c-90da9b861590 phase=stream-ready totalMs=46943 stages=workspace-sandbox:375ms@375ms,skills:0ms@375ms,core-plugin-tools:4675ms@5050ms,bootstrap-context:4092ms@9142ms,bundle-tools:5775ms@14917ms,system-prompt:15135ms@30052ms,session-resource-loader:1984ms@32036ms,agent-session:1ms@32037ms,stream-setup:14906ms@46943ms
2026-05-04T11:18:04.199+08:00 [ws] closed before connect conn=48df2372-5691-4aa2-9336-b5552ee088f2 peer=127.0.0.1:52305->127.0.0.1:18789 remote=127.0.0.1 fwd=n/a origin=n/a host=127.0.0.1:18789 ua=n/a code=1006 reason=n/a
2026-05-04T11:19:25.384+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=d41bad55-3d09-4c41-8ef7-84752902289e sessionId=f92074f9-874e-4a4e-9ed9-103587002013 phase=attempt-dispatch totalMs=18260 stages=workspace:0ms@0ms,runtime-plugins:7ms@7ms,hooks:0ms@7ms,model-resolution:1928ms@1935ms,auth:7600ms@9535ms,context-engine:1ms@9536ms,attempt-dispatch:8724ms@18260ms
2026-05-04T11:19:25.482+08:00 [ws] closed before connect conn=5ad2956a-ba24-4f8d-8241-4ed3cccc75b4 peer=127.0.0.1:56083->127.0.0.1:18789 remote=127.0.0.1 fwd=n/a origin=n/a host=127.0.0.1:18789 ua=n/a code=1006 reason=n/a
2026-05-04T11:19:54.275+08:00 [diagnostic] liveness warning: reasons=event_loop_delay,event_loop_utilization,cpu interval=37s eventLoopDelayP99Ms=19428 eventLoopDelayMaxMs=19428 eventLoopUtilization=1 cpuCoreRatio=0.966 active=0 waiting=0 queued=0
2026-05-04T11:20:24.992+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=d41bad55-3d09-4c41-8ef7-84752902289e sessionId=f92074f9-874e-4a4e-9ed9-103587002013 phase=stream-ready totalMs=59605 stages=workspace-sandbox:798ms@798ms,skills:2ms@800ms,core-plugin-tools:4557ms@5357ms,bootstrap-context:4082ms@9439ms,bundle-tools:5914ms@15353ms,system-prompt:17797ms@33150ms,session-resource-loader:3351ms@36501ms,agent-session:27ms@36528ms,stream-setup:23077ms@59605ms
2026-05-04T11:21:06.297+08:00 [agent/embedded] [trace:embedded-run] startup stages: runId=da902474-3b1d-4246-87b4-8279e290b0ce sessionId=da902474-3b1d-4246-87b4-8279e290b0ce phase=attempt-dispatch totalMs=16862 stages=workspace:0ms@0ms,runtime-plugins:3ms@3ms,hooks:0ms@3ms,model-resolution:1867ms@1870ms,auth:7309ms@9179ms,context-engine:0ms@9179ms,attempt-dispatch:7683ms@16862ms
2026-05-04T11:21:06.379+08:00 [ws] closed before connect conn=946258ae-8e83-4e0d-b620-cb35df347512 peer=127.0.0.1:63343->127.0.0.1:18789 remote=127.0.0.1 fwd=n/a origin=n/a host=127.0.0.1:18789 ua=n/a code=1006 reason=n/a
2026-05-04T11:21:49.667+08:00 [agent/embedded] [trace:embedded-run] prep stages: runId=da902474-3b1d-4246-87b4-8279e290b0ce sessionId=da902474-3b1d-4246-87b4-8279e290b0ce phase=stream-ready totalMs=43279 stages=workspace-sandbox:87ms@87ms,skills:1ms@88ms,core-plugin-tools:4209ms@4297ms,bootstrap-context:133ms@4430ms,bundle-tools:5788ms@10218ms,system-prompt:14293ms@24511ms,session-resource-loader:1025ms@25536ms,agent-session:0ms@25536ms,stream-setup:17743ms@43279ms
2026-05-04T11:22:08.848+08:00 [diagnostic] liveness warning: reasons=event_loop_delay,event_loop_utilization interval=58s eventLoopDelayP99Ms=36071 eventLoopDelayMaxMs=36071 eventLoopUtilization=1 cpuCoreRatio=0.841 active=1 waiting=0 queued=0
[tools] exec failed: exec host=node requires a node id when multiple nodes are available (set tools.exec.node or exec.node). raw_params={"command":"process poll 30000","host":"node"}
