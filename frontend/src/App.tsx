import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Inventory from './pages/Inventory'
import SimulatorPage from './pages/SimulatorPage'
import Reports from './pages/Reports'
import Copilot from './pages/Copilot'

export default function App() {
  return (
    <BrowserRouter basename={import.meta.env.BASE_URL}>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/inventory" element={<Inventory />} />
          <Route path="/simulator" element={<SimulatorPage />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/copilot" element={<Copilot />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
