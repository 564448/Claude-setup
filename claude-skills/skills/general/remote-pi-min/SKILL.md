---
name: remote-pi-min
description: Use when the user asks to remote/SSH/SCP into "the Raspberry Pi" or "min" — connects to min@masterpi.local using the pre-authorized SSH key, no password needed.
---

# Remote into Raspberry Pi "min"

Connection details:
- Host: `masterpi.local` (mDNS hostname — resolves automatically regardless of the Pi's current IP, as long as you're on the same local network. Fallback IP if mDNS fails: `172.20.10.11`, but confirm with the user since it may have changed.)
- User: `min`
- Auth: SSH key at `~/.ssh/id_ed25519` (already installed in the Pi's `~/.ssh/authorized_keys`, so no password prompt is needed)

## Usage

Run commands over SSH:
```bash
ssh min@masterpi.local "<command>"
```

Copy files to the Pi:
```bash
scp <local-file(s)> min@masterpi.local:<remote-path>/
```

Copy files from the Pi:
```bash
scp min@masterpi.local:<remote-path> <local-destination>
```

If `masterpi.local` fails to resolve (e.g. "Could not resolve hostname"), the client machine may lack mDNS support, or you may not be on the same local network as the Pi — ask the user for the Pi's current IP instead.

If a connection fails with "Host key verification failed" for `masterpi.local` specifically, it likely just needs its host key added: run `ssh-keyscan -t ed25519 masterpi.local >> ~/.ssh/known_hosts` and retry.

If a connection fails with a permission/publickey error, do not fall back to password auth silently — tell the user the key may have been removed from the Pi's `authorized_keys` and ask how to proceed.
