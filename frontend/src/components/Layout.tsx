import { NavLink, Outlet } from 'react-router-dom'
import { Bot, Boxes, FileText, Gauge, LayoutDashboard, Radio } from 'lucide-react'
import { IS_DEMO } from '../lib/api'

const NAV = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/inventory', label: 'Inventory', icon: Boxes },
  { to: '/simulator', label: 'Simulator', icon: Radio },
  { to: '/reports', label: 'Reports', icon: FileText },
  { to: '/copilot', label: 'AI Copilot', icon: Bot },
]

export default function Layout() {
  return (
    <div className="flex min-h-screen">
      <aside className="flex w-60 flex-col border-r border-zinc-800 bg-zinc-950 px-3 py-5">
        <div className="mb-8 flex items-center gap-2 px-2">
          <Gauge className="h-7 w-7 text-emerald-400" />
          <span className="text-lg font-semibold tracking-tight">PlantPulse</span>
        </div>
        <nav className="flex flex-col gap-1">
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                  isActive
                    ? 'bg-emerald-500/10 text-emerald-300'
                    : 'text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100'
                }`
              }
            >
              <Icon className="h-4 w-4" />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-auto px-3 text-xs text-zinc-600">v0.1.0 · slice 0</div>
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-zinc-800 px-6 py-4">
          <h1 className="text-sm font-medium text-zinc-300">Embedded Fleet Operations Hub</h1>
          {IS_DEMO && (
            <a
              href="https://github.com/dennisriverab28/PlantPulse"
              className="rounded-full border border-amber-500/30 bg-amber-500/10 px-3 py-1 text-xs text-amber-300 transition-colors hover:bg-amber-500/20"
            >
              in-browser demo — full stack runs via docker compose →
            </a>
          )}
          <div className="flex items-center gap-2 text-xs text-zinc-400">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400" />
            </span>
            live telemetry
          </div>
        </header>
        <main className="flex-1 bg-zinc-900/40 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
