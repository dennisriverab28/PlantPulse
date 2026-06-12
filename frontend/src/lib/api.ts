// Single data-access point. On the GitHub Pages demo (VITE_DEMO=true) there is
// no backend, so calls are served by the in-browser simulator instead.

import * as demo from './demo'
import type { Device, FleetAlert, Reading, Summary } from './types'

export const IS_DEMO = import.meta.env.VITE_DEMO === 'true'

export async function getDevices(): Promise<Device[]> {
  if (IS_DEMO) return demo.getDevices()
  return fetch('/api/devices').then((r) => r.json())
}

export async function getReadings(deviceId: number, metric: string, limit = 60): Promise<Reading[]> {
  if (IS_DEMO) return demo.getReadings(deviceId, metric, limit)
  return fetch(`/api/devices/${deviceId}/readings?metric=${metric}&limit=${limit}`).then((r) =>
    r.json(),
  )
}

export async function getSummary(): Promise<Summary> {
  if (IS_DEMO) return demo.getSummary()
  return fetch('/api/dashboard/summary').then((r) => r.json())
}

export async function getAlerts(): Promise<FleetAlert[]> {
  if (IS_DEMO) return demo.getAlerts()
  return fetch('/api/dashboard/alerts').then((r) => r.json())
}

export async function injectAnomaly(deviceId: number, metric: string, ticks = 12): Promise<void> {
  if (IS_DEMO) {
    demo.injectAnomaly(deviceId, metric, ticks)
    return
  }
  await fetch(`/api/devices/${deviceId}/anomaly`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ metric, ticks }),
  })
}
