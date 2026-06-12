export interface Device {
  id: number
  name: string
  bench: string
  device_type: string
  firmware_version: string
  status: string
}

export interface Reading {
  id: number
  metric: string
  value: number
  unit: string
  recorded_at: string
}

export interface Summary {
  devices_total: number
  devices_online: number
  alerts_open: number
  readings_last_hour: number
}

export interface FleetAlert {
  id: number
  device_id: number | null
  metric: string
  severity: string
  message: string
  created_at: string
}
