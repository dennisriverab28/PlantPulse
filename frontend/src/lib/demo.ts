// In-browser stand-in for the FastAPI backend, used on the GitHub Pages demo.
// Mirrors backend/app/simulator/engine.py: sinusoidal duty cycles + noise,
// deterministic per timestamp so polling doesn't rewrite history.

import type { Device, FleetAlert, Reading, Summary } from './types'

const TICK_S = 5
const WINDOW = 60

const PROFILES: Record<string, { base: number; amplitude: number; noise: number; unit: string; period: number }> = {
  cpu_temp: { base: 52, amplitude: 6, noise: 1.2, unit: '°C', period: 3600 },
  supply_voltage: { base: 3.3, amplitude: 0.04, noise: 0.015, unit: 'V', period: 1800 },
  current_draw: { base: 180, amplitude: 45, noise: 10, unit: 'mA', period: 900 },
  free_heap: { base: 148, amplitude: 16, noise: 5, unit: 'KB', period: 7200 },
}

const DEVICES: Device[] = [
  { id: 1, name: 'EDGE-01', bench: 'Bench A', device_type: 'ESP32 edge gateway', firmware_version: 'v2.4.1', status: 'online' },
  { id: 2, name: 'HIL-02', bench: 'Bench A', device_type: 'STM32 HIL test rig', firmware_version: 'v1.9.0', status: 'online' },
  { id: 3, name: 'SENSE-03', bench: 'Bench B', device_type: 'nRF52 sensor node', firmware_version: 'v3.1.2', status: 'online' },
  { id: 4, name: 'VISION-04', bench: 'Bench B', device_type: 'i.MX8 vision module', firmware_version: 'v0.8.7', status: 'online' },
]

// Active anomaly windows and raised alerts, keyed by device+metric.
const anomalies = new Map<string, { from: number; until: number }>()
const alerts: FleetAlert[] = []

function hashNoise(seed: number): number {
  const x = Math.sin(seed) * 10000
  return x - Math.floor(x)
}

// Irwin–Hall approximation of a standard normal (sum of 4 uniforms).
function gauss(seed: number): number {
  let sum = 0
  for (let i = 0; i < 4; i++) sum += hashNoise(seed + i * 7919)
  return (sum - 2) * 1.73
}

function valueAt(deviceId: number, metric: string, tSec: number): number {
  const p = PROFILES[metric]
  const phase = deviceId * 1.7
  let v =
    p.base +
    p.amplitude * Math.sin((2 * Math.PI * tSec) / p.period + phase) +
    p.noise * gauss(deviceId * 1_000_003 + tSec * 31 + metric.length * 101)
  const a = anomalies.get(`${deviceId}:${metric}`)
  if (a && tSec >= a.from && tSec <= a.until) {
    v += 6 * p.noise + 0.5 * p.amplitude
  }
  return Math.round(v * 1000) / 1000
}

export function getDevices(): Device[] {
  return DEVICES
}

export function getReadings(deviceId: number, metric: string, limit: number): Reading[] {
  const p = PROFILES[metric]
  if (!p) return []
  const now = Math.floor(Date.now() / 1000 / TICK_S) * TICK_S
  const n = Math.min(limit, WINDOW)
  const out: Reading[] = []
  for (let i = n - 1; i >= 0; i--) {
    const t = now - i * TICK_S
    out.push({
      id: t,
      metric,
      value: valueAt(deviceId, metric, t),
      unit: p.unit,
      recorded_at: new Date(t * 1000).toISOString(),
    })
  }
  return out
}

export function getSummary(): Summary {
  return {
    devices_total: DEVICES.length,
    devices_online: DEVICES.length,
    alerts_open: alerts.length,
    readings_last_hour: DEVICES.length * Object.keys(PROFILES).length * (3600 / TICK_S),
  }
}

export function getAlerts(): FleetAlert[] {
  return [...alerts].reverse()
}

export function injectAnomaly(deviceId: number, metric: string, ticks: number): void {
  if (!PROFILES[metric]) return
  const now = Math.floor(Date.now() / 1000 / TICK_S) * TICK_S
  anomalies.set(`${deviceId}:${metric}`, { from: now, until: now + ticks * TICK_S })
  if (!alerts.some((a) => a.device_id === deviceId && a.metric === metric)) {
    const value = valueAt(deviceId, metric, now + TICK_S)
    alerts.push({
      id: alerts.length + 1,
      device_id: deviceId,
      metric,
      severity: 'critical',
      message: `${metric} out of band: ${value} ${PROFILES[metric].unit}`,
      created_at: new Date().toISOString(),
    })
  }
}
