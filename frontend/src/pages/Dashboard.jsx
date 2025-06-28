import { useAccountSummary, useTransactions } from '../hooks/useTransactions'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import ErrorMessage from '../components/ui/ErrorMessage'
import { Link } from 'react-router-dom'
import AIInsights from '../components/ai/AIInsights'

const Dashboard = () => {
  const { data: summary, isLoading: summaryLoading, error: summaryError } = useAccountSummary()
  
  // Get recent checking account transactions (current month, limit to 6)
  const currentMonth = new Date().toISOString().slice(0, 7) // YYYY-MM format
  const { data: recentTransactions, isLoading: transactionsLoading } = useTransactions({
    account_type: 'checking',
    month: currentMonth
  })
  
  // Get credit account transactions to calculate rewards
  const { data: creditTransactions } = useTransactions({
    account_type: 'credit',
    month: currentMonth
  })

  if (summaryLoading) {
    return <LoadingSpinner message="Loading dashboard..." />
  }

  if (summaryError) {
    return <ErrorMessage message="Failed to load dashboard data" />
  }

  // Get top 6 most recent transactions
  const topRecentTransactions = recentTransactions?.slice(0, 6) || []
  
  // HARDCODED CREDIT BALANCE for dashboard showcase  
  const creditBalance = 12847.91  // Random amount in $15K range
  
  const creditRewards = creditTransactions?.reduce((total, transaction) => {
    // Calculate 2X rewards for credit purchases (2% of expenses) - only positive amounts
    if (transaction.type === 'expense' && transaction.amount > 0) {
      return total + (transaction.amount * 0.02)
    }
    return total
  }, 0) || 0

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Main Layout: Two columns */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left Column: Account Cards */}
          <div className="lg:col-span-1 space-y-4">
            
            {/* Checking Account Card */}
            <div className="bg-gradient-to-br from-slate-700 to-slate-900 rounded-2xl p-6 text-white shadow-xl">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-lg font-light tracking-wider">QUICKSILVER</h2>
                  <p className="text-sm opacity-75">...6151</p>
                </div>
              </div>
              
              <div className="mb-6">
                <p className="text-4xl font-light mb-2">
                  ${Math.abs(summary?.current_balance || 0).toLocaleString()}
                  <span className="text-xl">{((summary?.current_balance || 0) % 1).toFixed(2).slice(1)}</span>
                </p>
                <p className="text-sm font-light opacity-75">CURRENT BALANCE</p>
              </div>
              
              <div className="mb-4">
                <div className="text-center">
                  <p className="text-lg font-light opacity-75">
                    Available Balance: ${Math.abs(summary?.current_balance || 0).toLocaleString()}
                  </p>
                </div>
              </div>
              
              <Link to="/transactions" className="block">
                <button className="w-full border-2 border-white/30 rounded-lg py-2 px-4 text-white font-medium hover:bg-white/10 transition-colors mb-3">
                  View Account
                </button>
              </Link>
              
              <button className="flex items-center space-x-2 text-white/80 hover:text-white transition-colors">
                <span className="text-lg">💳</span>
                <span className="text-sm">Get your Virtual Card</span>
              </button>
            </div>

            {/* Credit Account Card */}
            <div className="bg-gradient-to-br from-blue-900 via-purple-900 to-blue-800 rounded-2xl p-6 text-white shadow-xl relative overflow-hidden">
              {/* Background decoration */}
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-yellow-400/20 to-orange-500/20 rounded-full -translate-y-16 translate-x-16"></div>
              
              <div className="relative">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h2 className="text-lg font-light tracking-wider">VENTURE REWARDS</h2>
                    <p className="text-sm opacity-75">...4782</p>
                  </div>
                </div>
                
                <div className="mb-4">
                  <p className="text-4xl font-light mb-2">
                    ${Math.abs(creditBalance).toLocaleString()}
                    <span className="text-xl">{((Math.abs(creditBalance) % 1).toFixed(2).slice(1))}</span>
                  </p>
                  <p className="text-sm font-light opacity-75">CURRENT BALANCE</p>
                </div>
                
                <div className="flex justify-between items-end mb-4">
                  <div>
                    <p className="text-xl font-light">
                      $25,000<span className="text-base">.00</span>
                    </p>
                    <p className="text-xs opacity-75">CREDIT LIMIT</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xl font-light">
                      ${creditRewards.toFixed(0)}<span className="text-base">.{((creditRewards % 1) * 100).toFixed(0).padStart(2, '0')}</span>
                    </p>
                    <p className="text-xs opacity-75">REWARDS EARNED ›</p>
                  </div>
                </div>
                
                <Link to="/transactions" className="block">
                  <button className="w-full border-2 border-white/30 rounded-lg py-2 px-4 text-white font-medium hover:bg-white/10 transition-colors mb-3">
                    View Credit Account
                  </button>
                </Link>
                
                <button className="flex items-center space-x-2 text-white/80 hover:text-white transition-colors">
                  <span className="text-lg">💎</span>
                  <span className="text-sm">Redeem Rewards</span>
                </button>
              </div>
            </div>
          </div>

          {/* Right Column: Recent Transactions */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-2xl font-semibold text-gray-900">Recent Transactions</h3>
                <Link to="/transactions" className="text-blue-600 hover:text-blue-800 font-medium">
                  View More
                </Link>
              </div>
              
              {transactionsLoading ? (
                <div className="flex justify-center py-8">
                  <LoadingSpinner message="Loading transactions..." />
                </div>
              ) : topRecentTransactions.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-gray-500 text-lg">You have no recent transactions.</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-200">
                  {topRecentTransactions.map(transaction => (
                    <div key={transaction.id} className="py-4 flex justify-between items-center">
                      <div>
                        <p className="font-medium text-gray-800">{transaction.description}</p>
                        <p className="text-sm text-gray-500">{new Date(transaction.date).toLocaleDateString()}</p>
                      </div>
                      <p className={`font-semibold ${transaction.amount > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {transaction.amount > 0 ? '+' : '-'}${Math.abs(transaction.amount).toFixed(2)}
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {/* AI Insights Panel */}
              <div className="mt-8">
                <AIInsights transactions={recentTransactions} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard 