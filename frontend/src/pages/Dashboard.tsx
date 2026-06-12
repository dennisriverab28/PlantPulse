import { useCallback, useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Activity, AlertTriangle, Database, Factory, FlaskConical, Zap } from 'lucide-react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

interface Machine {
  id: number
  name: string
  line: string
  machine_type: string
  status: string
}

interface Reading {
  id: number
  metric: string
  value: number
  unit: string
  recorded_at: string
}

interface Summary {
  machines_total: number
  machines_running: number
  alerts_open: number
  readings_last_hour: number
}

interface PlantAlert {
  id: number
  machine_id: number | null
  metric: string
  severity: string
  message: string
  created_at: string
}

const METRICS = ['temperature', 'vibration', 'rpm', 'throughput']

export default function Dashboard() {
  const [machines, setMachines] = useState<Machine[]>([])
  const [selected, setSelected] = useState<number | null>(null)
  const [metric, setMetric] = useState('temperature')
  const [readings, setReadings] = useState<Reading[]>([])
  const [summary, setSummary] = useState<Summary | null>(null)
  const [alerts, setAlerts] = useState<PlantAlert[]>([])

  useEffect(() => {
    fetch('/api/machines')
      .then((r) => r.json())
      .then((ms: Machine[]) => {
        setMachines(ms)
        if (ms.length > 0) setSelected((prev) => prev ?? ms[0].id)
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    const load = () => {
      fetch('/api/dashboard/summary').then((r) => r.json()).then(setSummary).catch(() => {})
      fetch('/api/dashboard/alerts').then((r) => r.json()).then(setAlerts).catch(() => {})
    }
    load()
    const id = setInterval(load, 10_000)
    return () => clearInterval(id)
  }, [])

  useEffect(() => {
    if (selected == null) return
    const load = () => {
      fetch(`/api/machines/${selected}/readings?metric=${metric}&limit=60`)
        .then((r) => r.json())
        .then(setReadings)
        .catch(() => {})
    }
    load()
    const id = setInterval(load, 5_000)
    return () => clearInterval(id)
  }, [selected, metric])

  const injectAnomaly = useCallback(() => {
    if (selected == null) return
    fetch(`/api/machines/${selected}/anomaly`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ metric, ticks: 12 }),
    }).catch(() => {})
  }, [selected, metric])

  const unit = readings.length > 0 ? readings[readings.length - 1].unit : ''
  const chartData = readings.map((r) => ({
    time: new Date(r.recorded_at).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    }),
    value: r.value,
  }))

  const stats = [
    { label: 'Machines', value: summary?.machines_total, icon: Factory, tint: 'text-sky-400' },
    { label: 'Running', value: summary?.machines_running, icon: Zap, tint: 'text-emerald-400' },
    { label: 'Open alerts', value: summary?.alerts_open, icon: AlertTriangle, tint: 'text-amber-400' },
    { label: 'Readings / hr', value: summary?.readings_last_hour, icon: Database, tint: 'text-violet-400' },
  ]

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {stats.map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.07, duration: 0.35 }}
            className="rounded-xl border border-zinc-800 bg-zinc-950 p-4"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs uppercase tracking-wider text-zinc-500">{s.label}</span>
              <s.icon className={`h-4 w-4 ${s.tint}`} />
            </div>
            <div className="mt-2 text-2xl font-semibold tabular-nums">{s.value ?? '—'}</div>
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.35 }}
        className="rounded-xl border border-zinc-800 bg-zinc-950 p-5"
      >
        <div className="mb-4 flex flex-wrap items-center gap-3">
          <Activity className="h-4 w-4 text-emerald-400" />
          <h2 className="text-sm font-medium">Live telemetry</h2>
          <select
            value={selected ?? ''}
            onChange={(e) => setSelected(Number(e.target.value))}
            className="rounded-md border border-zinc-700 bg-zinc-900 px-2 py-1 text-xs"
          >
            {machines.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name} · {m.line}
              </option>
            ))}
          </select>
          <div className="flex gap-1">
            {METRICS.map((m) => (
              <button
                key={m}
                onClick={() => setMetric(m)}
                className={`rounded-md px-2 py-1 text-xs transition-colors ${
                  metric === m
                    ? 'bg-emerald-500/15 text-emerald-300'
                    : 'text-zinc-500 hover:bg-zinc-900 hover:text-zinc-200'
                }`}
              >
                {m}
              </button>
            ))}
          </div>
          <button
            onClick={injectAnomaly}
            className="ml-auto flex items-center gap-1.5 rounded-md border border-amber-500/30 bg-amber-500/10 px-2.5 py-1 text-xs text-amber-300 transition-colors hover:bg-amber-500/20"
            title="Push this metric out of band for ~1 minute and watch the alert fire"
          >
            <FlaskConical className="h-3.5 w-3.5" />
            inject anomaly
          </button>
        </div>

        <div className="h-72">
          {chartData.length === 0 ? (
            <div className="flex h-full items-center justify-center text-sm text-zinc-600">
              waiting for telemetry… (is the backend running?)
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 8, right: 12, bottom: 0, left: 0 }}>
                <CartesianGrid stroke="#27272a" strokeDasharray="3 3" />
                <XAxis dataKey="time" stroke="#52525b" fontSize={11} minTickGap={40} />
                <YAxis
                  stroke="#52525b"
                  fontSize={11}
                  domain={['auto', 'auto']}
                  width={60}
                  tickFormatter={(v: number) => `${v}`}
                />
                <Tooltip
                  contentStyle={{
                    background: '#18181b',
                    border: '1px solid #3f3f46',
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                  formatter={(value) => [`${value} ${unit}`, metric]}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#34d399"
                  strokeWidth={2}
                  dot={false}
                  isAnimationActive={false}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.35 }}
        className="rounded-xl border border-zinc-800 bg-zinc-950 p-5"
      >
        <h2 className="mb-3 text-sm font-medium">Open alerts</h2>
        {alerts.length === 0 ? (
          <p className="text-sm text-zinc-600">All clear — no open alerts.</p>
        ) : (
          <ul className="space-y-2">
            {alerts.map((a) => (
              <li
                key={a.id}
                className="flex items-center gap-3 rounded-lg border border-red-500/20 bg-red-500/5 px-3 py-2 text-sm"
              >
                <AlertTriangle className="h-4 w-4 shrink-0 text-red-400" />
                <span className="text-zinc-200">{a.message}</span>
                <span className="ml-auto text-xs text-zinc-500">
                  {new Date(a.created_at).toLocaleTimeString()}
                </span>
              </li>
            ))}
          </ul>
        )}
      </motion.div>
    </div>
  )
}
