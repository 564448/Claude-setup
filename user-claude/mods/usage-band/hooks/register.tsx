import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Snapshot } from '../types'

const ORANGE = '#D97757'
const BAR_WIDTH = 10

const snapshot = atom({ plugin: 'usage-band', key: 'snapshot' } as const, null)

// "claude-sonnet-5-5" -> "Sonnet5.5"; an alias such as "sonnet" is only capitalised.
const prettyModel = (id: string) => {
  const m = id.match(/(?:claude-)?([a-z]+)-(\d+)(?:-(\d+))?/)
  if (!m) return id.charAt(0).toUpperCase() + id.slice(1)
  return m[1].charAt(0).toUpperCase() + m[1].slice(1) + m[2] + (m[3] ? `.${m[3]}` : '')
}

const resetText = (iso?: string) => {
  if (!iso) return ''
  const d = new Date(iso)
  const day = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][d.getDay()]
  const pad = (n: number) => String(n).padStart(2, '0')
  return ` (resets ${day} ${pad(d.getHours())}:${pad(d.getMinutes())})`
}

export const register: Register = on => {
  on('session.measure', async ($, e, next) => {
    const snap: Snapshot = { contextPercent: e.context.percent ?? null, limits: e.rateLimits }
    await update($, snapshot, () => snap)

    return next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey) return next(e)

    let snap = await read($, snapshot)
    if (snap === null) {
      const u = await $.session.usage()
      snap = { contextPercent: u.context.percent ?? null, limits: u.rateLimits }
    }

    const model = prettyModel(await $.session.model())
    const effort = (await $.settings.read({ key: 'effortLevel' })) as string | undefined
    const { Box, Text } = $.ui.resolve(e)

    const meter = (label: string, pct: number, resets?: string) => {
      const filled = Math.max(0, Math.min(BAR_WIDTH, Math.round((pct / 100) * BAR_WIDTH)))
      return (
        <Text key={label}>
          <Text dimColor>{label} </Text>
          <Text color={ORANGE}>{'█'.repeat(filled)}</Text>
          <Text dimColor>{'░'.repeat(BAR_WIDTH - filled)} </Text>
          <Text color={ORANGE}>{Math.round(pct)}%</Text>
          <Text dimColor>{resetText(resets)}</Text>
        </Text>
      )
    }

    const sep = <Text dimColor> | </Text>
    const left: unknown[] = [<Text key="model" color={ORANGE}>{model + (effort ? `-${effort}` : '')}</Text>]
    for (const [kind, label] of [['five_hour', '5h'], ['seven_day', '7d']] as const) {
      const l = snap.limits.find(x => x.kind === kind)
      if (l) left.push(sep, meter(label, l.percentUsed, l.resetsAt))
    }

    return (
      <Box flexDirection="column">
        <Text dimColor>{'─'.repeat(e.props.bodyColumns)}</Text>
        <Box justifyContent="space-between">
          <Box>{left as never}</Box>
          {snap.contextPercent !== null ? meter('context', snap.contextPercent) : <Text> </Text>}
        </Box>
      </Box>
    )
  })
}
