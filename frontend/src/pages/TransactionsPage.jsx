import { useState } from 'react'
import { Tab } from '@headlessui/react'
import clsx from 'clsx'
import TransactionTable from '../components/transactions/TransactionTable'
import TransactionFilters from '../components/transactions/TransactionFilters'
import MonthNavigation from '../components/transactions/MonthNavigation'
import DexChatbot from '../components/ai/DexChatbot'
import AILearningDashboard from '../components/ai/AILearningDashboard'
import { useFilters } from '../hooks/useFilters'
import { generateTransactionReport } from '../services/pdfService'

const TransactionsPage = () => {
  const [activeAccount, setActiveAccount] = useState('checking')
  const [temporaryCategories, setTemporaryCategories] = useState({})
  const { filters, cleanFilters, updateFilter, updateFilters, resetFilters, setMonth, navigateMonth, canNavigate } = useFilters()
  const [showLearningDashboard, setShowLearningDashboard] = useState(false)

  const accountTypes = [
    { id: 'checking', label: 'Checking Account', icon: '🏦' },
    { id: 'credit', label: 'Credit Account', icon: '💳' }
  ]

  // Update account type in filters when tab changes
  const handleAccountChange = (accountType) => {
    setActiveAccount(accountType)
    updateFilter('account_type', accountType)
  }

  // Handle temporary categorizations from AI
  const handleTemporaryCategorizations = (suggestions) => {
    const tempCategories = {}
    suggestions.forEach(suggestion => {
      tempCategories[suggestion.id] = suggestion.category
    })
    setTemporaryCategories(tempCategories)
  }

  // Handle filter changes from TransactionFilters component
  const handleFiltersChange = (newFilters) => {
    updateFilters(newFilters)
  }

  // Clear temporary categories when month changes
  const handleMonthChange = (newMonth) => {
    setTemporaryCategories({}) // Clear temporary categories
    setMonth(newMonth)
  }

  const handleNavigateMonth = (direction) => {
    setTemporaryCategories({}) // Clear temporary categories
    navigateMonth(direction)
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Transactions</h1>
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setShowLearningDashboard(true)}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center space-x-2"
          >
            <span>🧠</span>
            <span>AI Learning</span>
          </button>
          <button
            onClick={() => generateTransactionReport(transactions, filters.month)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
          >
            <span>📄</span>
            <span>Download PDF</span>
          </button>
        </div>
      </div>
      
      <MonthNavigation 
        currentMonth={filters.month}
        onMonthChange={handleMonthChange}
        onNavigate={handleNavigateMonth}
        canNavigate={canNavigate}
      />
      
      <TransactionFilters 
        filters={filters}
        onFiltersChange={handleFiltersChange}
        onClear={resetFilters}
      />
      
      <TransactionTable 
        filters={filters}
        accountType={filters.accountType}
      />

      <AILearningDashboard
        isOpen={showLearningDashboard}
        onClose={() => setShowLearningDashboard(false)}
      />

      <DexChatbot
        accountType={activeAccount}
        currentMonth={filters.month}
        onTemporaryCategorizations={handleTemporaryCategorizations}
      />
    </div>
  )
}

export default TransactionsPage 