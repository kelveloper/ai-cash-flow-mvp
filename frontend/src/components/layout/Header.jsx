import { useNavigate, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { transactionService } from '../../services/transactionService'

const TemporaryChangesBadge = () => {
  const [tempStatus, setTempStatus] = useState(null)

  const checkStatus = async () => {
    try {
      const status = await transactionService.getTemporaryCategorizationsStatus()
      setTempStatus(status)
    } catch (error) {
      console.error('Failed to check temporary status:', error)
    }
  }

  useEffect(() => {
    checkStatus()
    // Check status every 10 seconds
    const interval = setInterval(checkStatus, 10000)
    return () => clearInterval(interval)
  }, [])

  if (!tempStatus || tempStatus.active_count === 0) {
    return null
  }

  return (
    <div className="flex items-center bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm">
      <span className="mr-1">⚠️</span>
      <span>{tempStatus.active_count} temporary change{tempStatus.active_count !== 1 ? 's' : ''}</span>
    </div>
  )
}

const Header = () => {
  const navigate = useNavigate()
  const location = useLocation()
  
  // Only show home button if not on dashboard
  const showHomeButton = location.pathname !== '/'

  return (
    <header className="bg-white shadow p-4 flex items-center justify-between">
      <div className="flex items-center">
        <TemporaryChangesBadge />
      </div>
      <h1 className="text-7xl font-extrabold text-blue-900 tracking-tight">
        Capital Two
      </h1>
      <div className="flex items-center">
        {showHomeButton && (
          <button
            onClick={() => navigate('/')}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors shadow-sm"
            title="Back to Dashboard"
          >
            <span className="text-lg">🏠</span>
            <span>Home</span>
          </button>
        )}
      </div>
    </header>
  )
}

export default Header 