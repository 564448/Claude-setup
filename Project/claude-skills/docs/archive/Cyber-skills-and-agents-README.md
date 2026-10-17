# Skills & Agents — Cyber

Claude Code skills/agents relevant to the Cyber project (Kali VM lab).

## remote_vm_kali

Connects to the Kali VM used in this project.

- Trigger: asking to remote/SSH/SCP into "the Kali VM" or "kali"
- Host: `192.168.41.128` (static IP set on the VM's `eth0`)
- User: `kali`
- Auth: SSH key (`~/.ssh/id_ed25519_kali`, alias `kali-vm`) preferred; password (`kali`/`kali`) as fallback for manual remoting
- Skill file: `Project/claude-skills/skills/general/remote_vm_kali/SKILL.md` (linked into `~/.claude/skills/remote_vm_kali`)
