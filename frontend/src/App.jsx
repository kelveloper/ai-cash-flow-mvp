import { Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import TransactionsPage from './pages/TransactionsPage'
import Dashboard from './pages/Dashboard'
import AICategorization from './pages/AICategorization'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/transactions" element={<TransactionsPage />} />
        <Route path="/ai-categorization" element={<AICategorization />} />
        {/* Legacy route redirects */}
        <Route path="/checking-transactions" element={<TransactionsPage />} />
        <Route path="/credit-transactions" element={<TransactionsPage />} />
      </Routes>
    </Layout>
  )
}

export default App 