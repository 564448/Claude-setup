---
name: remote_vm_kali
description: Use when the user asks to remote/SSH/SCP into "the Kali VM" or "kali" — connects to kali@192.168.41.128, preferring the pre-authorized SSH key, with password auth (kali/kali) as fallback.
---

# Remote into Kali VM

Connection details:
- Host: `192.168.41.128` (static IP, set directly on the VM's `eth0` via NetworkManager, so it stays the same across reboots as long as the VM is on this VMware network)
- User: `kali`
- Auth (in priority order):
  1. **SSH key** at `~/.ssh/id_ed25519_kali` (already installed in the VM's `~/.ssh/authorized_keys`, no password needed). An SSH config alias `kali-vm` is also set up, so `ssh kali-vm` works directly.
  2. **Password** `kali` / `kali`, if the user explicitly wants to remote in manually with a password, or if the key is unavailable/rejected.

## Usage

Preferred (key auth via alias):
```bash
ssh kali-vm "<command>"
scp <local-file(s)> kali-vm:<remote-path>/
scp kali-vm:<remote-path> <local-destination>
```

Equivalent explicit key auth:
```bash
ssh -i ~/.ssh/id_ed25519_kali kali@192.168.41.128 "<command>"
```

Password auth (only when the user asks to connect manually with a password):
```bash
ssh kali@192.168.41.128 "<command>"
```
This will prompt interactively for the password (`kali`) — for non-interactive/scripted use, use `paramiko` (Python) instead of `sshpass`/`plink`, since neither is installed in this environment.

## Troubleshooting

If key auth fails with a permission/publickey error, do not silently fall back to password auth without telling the user — the key may have been removed from the VM's `authorized_keys`. Ask how to proceed.

If the VM's IP has changed (e.g. moved to a different network, or the static config was reset), ask the user for the current IP rather than assuming `192.168.41.128` still applies.

If "Host key verification failed" occurs, the VM's host key may have changed (e.g. after a reinstall): confirm with the user before removing the old entry from `~/.ssh/known_hosts`.
