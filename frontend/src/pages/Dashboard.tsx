import { useCallback, useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Activity, AlertTriangle, Cpu, Database, FlaskConical, Wifi } from 'lucide-react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import * as api from '../lib/api'
import type { Device, FleetAlert, Reading, Summary } from '../lib/types'

const METRICS = [
  { key: 'cpu_temp', label: 'CPU temp' },
  { key: 'supply_voltage', label: 'voltage' },
  { key: 'current_draw', label: 'current' },
  { key: 'free_heap', label: 'free heap' },
]

export default function Dashboard() {
  const [devices, setDevices] = useState<Device[]>([])
  const [selected, setSelected] = useState<number | null>(null)
  const [metric, setMetric] = useState('cpu_temp')
  const [readings, setReadings] = useState<Reading[]>([])
  const [summary, setSummary] = useState<Summary | null>(null)
  const [alerts, setAlerts] = useState<FleetAlert[]>([])

  useEffect(() => {
    api
      .getDevices()
      .then((ds) => {
        setDevices(ds)
        if (ds.length > 0) setSelected((prev) => prev ?? ds[0].id)
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    const load = () => {
      api.getSummary().then(setSummary).catch(() => {})
      api.getAlerts().then(setAlerts).catch(() => {})
    }
    load()
    const id = setInterval(load, 10_000)
    return () => clearInterval(id)
  }, [])

  useEffect(() => {
    if (selected == null) return
    const load = () => {
      api.getReadings(selected, metric, 60).then(setReadings).catch(() => {})
    }
    load()
    const id = setInterval(load, 5_000)
    return () => clearInterval(id)
  }, [selected, metric])

  const injectAnomaly = useCallback(() => {
    if (selected == null) return
    api.injectAnomaly(selected, metric, 12).catch(() => {})
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

  const selectedDevice = devices.find((d) => d.id === selected)
  const metricLabel = METRICS.find((m) => m.key === metric)?.label ?? metric

  const stats = [
    { label: 'Devices', value: summary?.devices_total, icon: Cpu, tint: 'text-sky-400' },
    { label: 'Online', value: summary?.devices_online, icon: Wifi, tint: 'text-emerald-400' },
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
            {devices.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name} · {d.bench} · fw {d.firmware_version}
              </option>
            ))}
          </select>
          {selectedDevice && (
            <span className="text-xs text-zinc-500">{selectedDevice.device_type}</span>
          )}
          <div className="flex gap-1">
            {METRICS.map((m) => (
              <button
                key={m.key}
                onClick={() => setMetric(m.key)}
                className={`rounded-md px-2 py-1 text-xs transition-colors ${
                  metric === m.key
                    ? 'bg-emerald-500/15 text-emerald-300'
                    : 'text-zinc-500 hover:bg-zinc-900 hover:text-zinc-200'
                }`}
              >
                {m.label}
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
                  formatter={(value) => [`${value} ${unit}`, metricLabel]}
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
                <span className="text-zinc-200">
                  {devices.find((d) => d.id === a.device_id)?.name ?? `device ${a.device_id}`}:{' '}
                  {a.message}
                </span>
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
