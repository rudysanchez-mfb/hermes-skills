---
name: hermes-relay-ops
description: Use when setting up, pairing, or troubleshooting hermes-relay.
---

# Hermes-Relay Ops

Scope: the hermes-relay plugin on a Hermes host — persistence, dashboard ingress, pairing, TTL policy, troubleshooting. Record full host state and history in the project knowledge base, not in this skill.

## When to Use

- Installing or enabling the hermes-relay plugin, or making the relay server persistent.
- Pairing or re-pairing the Android app, or answering "is it paired?"
- The user says they picked a TTL or "never expire" in the app.
- The Relay row won't go green, dashboard ingress looks broken, or `hermes relay doctor` warns.

## Persistence — the plugin manager ships no service

`hermes plugins install Codename-11/hermes-relay/plugin --enable` installs code, CLI, dashboard metadata, and agent tools; it does **not** install a systemd unit (only legacy `install.sh` does). A `hermes relay start --no-ssl` run from a shell dies with that shell.

Rule: author `~/.config/systemd/user/hermes-relay.service` with an absolute `ExecStart` to the real venv binary (`command -v hermes`), `Restart=always`, `WorkingDirectory=%h`; then `daemon-reload`, kill the manual PID, `enable --now`. Confirm `loginctl show-user $USER -p Linger` is `yes`.

## Dashboard ingress — restart the dashboard after any plugin install/update

Backend plugin routes mount at Dashboard startup only, so a dashboard process older than the plugin has no `/api/plugins/<name>/...` route.

Rule: `systemctl --user restart hermes-dashboard.service` after installing or updating the plugin.

## Never judge ingress by HTTP status code

Every `/api/plugins/<anything>` — bogus plugin names included — returns `401 {"reason":"no_cookie","login_url":"/login"}`. A 401 proves nothing about whether the route exists.

Rule: verify the mount by checking `dashboard/__pycache__/*.pyc` mtimes fall between the dashboard's start time and `HERMES_DASHBOARD_READY` in `journalctl --user -u hermes-dashboard`.

Rule: `session_rejected: no_cookie` on `/api/plugins/hermes-relay/transport/health` in `~/.hermes/logs/dashboard-auth.log` is a benign pre-auth probe — the app logs it immediately before pairing successfully. Do not call it a blocker or a bug.

## Proven pairing state

Rule: read the relay's own counters, never the app's UI claim — `curl -s localhost:8767/relay/info` (`paired_device_count`, `session_count`) and `/health` (`clients`, `sessions`). Device records live in `~/.hermes/hermes-relay-sessions.json`; `~/.hermes/pairing/` stays empty and is not the truth source.

Rule: a phone connected through dashboard ingress never appears on port 8767 under its own IP. The dashboard holds the ESTAB socket to `127.0.0.1:8767` and proxies; `clients: 1` on loopback is the phone.

## TTL policy — the phone cannot author its own session policy

Session TTL and grants come only from host-side pairing-code metadata (`server.pairing.consume_code`), written by the loopback-only `/pairing/register`, `/pairing/approve`, `/pairing/mint`. Fields the phone sends (`ttl_seconds`, `grants`) are accepted for wire compatibility and deliberately discarded.

Rule: selecting "Never expire" in the Android app yields library defaults — 30-day session, bridge capped at 7 days. Never tell the user their app picker controls expiry.

Rule: to grant never, mint host-side: `hermes pair --ttl never --grants chat=never,terminal=never,bridge=never,tui=never,voice:config=never,voice:stt=never,voice:tts=never,voice:realtime=never`. `never` maps to 0 seconds then `math.inf`; the receipt prints `Pair: indefinitely`.

Rule: explicit grants are still clamped to overall session expiry — an infinite channel inside a 30-day session still dies at 30 days.

Rule: re-pairing replaces the prior session and trusted credential for the same `device_id`; no duplicates accumulate.

## Do not restart the gateway just to clear doctor warnings

`hermes-gateway.service` parents the agent's MCP children (council, quality-gate, gbrain, firecrawl) and owns Telegram/WhatsApp. Restarting it mid-session orphans those tools.

Rule: `gateway-heartbeat: start_mismatch` is cosmetic; defer the gateway restart to a planned window. Same for `api-capabilities` (Direct API is optional and loopback-bound) and `dashboard-nous-session: terminal` (only matters on Nous inference).

## App navigation

Settings → Connections → server card → **Advanced → Pair Relay** for the QR / enter-code / show-code flow. **Overview** has Re-pair. **Security → Relay sessions** lists and revokes devices. `hermes pair --register-code <code>` serves the app's *Show Relay code* reverse flow.

## Uninstall order

`hermes relay compat remove --all` → `hermes plugins remove hermes-relay` → `systemctl --user disable --now hermes-relay` → delete the authored unit.
