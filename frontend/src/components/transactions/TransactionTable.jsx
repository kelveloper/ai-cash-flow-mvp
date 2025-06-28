import { useState, useMemo, useEffect } from 'react'
import { useTransactions } from '../../hooks/useTransactions'
import { transactionService } from '../../services/transactionService'
import TransactionRow from './TransactionRow'
import TransactionEditModal from './TransactionEditModal'
import LoadingSpinner from '../ui/LoadingSpinner'
import ErrorMessage from '../ui/ErrorMessage'

const TemporaryCategorizeStatus = ({ onRefresh }) => {
  const [status, setStatus] = useState(null)
  const [isClearing, setIsClearing] = useState(false)
  const [showDetailsModal, setShowDetailsModal] = useState(false)

  const checkStatus = async () => {
    try {
      const statusData = await transactionService.getTemporaryCategorizationsStatus()
      setStatus(statusData)
    } catch (error) {
      console.error('Failed to get temporary status:', error)
    }
  }

  const clearAllTemporary = async () => {
    if (!window.confirm('Are you sure you want to clear all temporary changes? This will reset everything back to the original database state.')) {
      return
    }

    setIsClearing(true)
    try {
      await transactionService.clearTemporaryCategorizations()
      await checkStatus()
      onRefresh() // Refresh the transaction table
      setShowDetailsModal(false) // Close details modal if open
    } catch (error) {
      console.error('Failed to clear temporary changes:', error)
    } finally {
      setIsClearing(false)
    }
  }

  useEffect(() => {
    checkStatus()
  }, [])

  if (!status || status.active_count === 0) {
    return null
  }

  return (
    <>
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <span className="text-2xl mr-2">⚠️</span>
            <div>
              <h3 className="font-semibold text-yellow-800">Temporary Changes Active</h3>
              <p className="text-yellow-700 text-sm">
                {status.active_count} transaction{status.active_count !== 1 ? 's have' : ' has'} temporary category changes. 
                These will reset when the app restarts.
              </p>
            </div>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setShowDetailsModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
            >
              View Details
            </button>
            <button
              onClick={clearAllTemporary}
              disabled={isClearing}
              className="px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700 disabled:opacity-50 text-sm"
            >
              {isClearing ? 'Clearing...' : 'Reset All Changes'}
            </button>
          </div>
        </div>
      </div>

      {/* Details Modal */}
      {showDetailsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-6xl max-h-[90vh] overflow-y-auto">
                         <div className="flex justify-between items-center mb-4">
               <div className="flex items-center space-x-3">
                 <button
                   onClick={() => setShowDetailsModal(false)}
                   className="flex items-center space-x-2 px-3 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                 >
                   <span>←</span>
                   <span>Back</span>
                 </button>
                 <h2 className="text-xl font-semibold">Smart Categorization Details</h2>
               </div>
               <button
                 onClick={() => setShowDetailsModal(false)}
                 className="text-gray-500 hover:text-gray-700 text-xl"
               >
                 ✕
               </button>
             </div>

            <div className="mb-4 p-3 bg-blue-50 rounded text-sm text-blue-700">
              <p>📊 <strong>Smart Categorization Results:</strong> These changes were made by AI analysis and will reset when you stop the app.</p>
            </div>

            {status.detailed_changes && status.detailed_changes.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full border-collapse border border-gray-300">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="border border-gray-300 px-3 py-2 text-left">Date</th>
                      <th className="border border-gray-300 px-3 py-2 text-left">Description</th>
                      <th className="border border-gray-300 px-3 py-2 text-left">Amount</th>
                      <th className="border border-gray-300 px-3 py-2 text-left">Account</th>
                      <th className="border border-gray-300 px-3 py-2 text-left">Original Category</th>
                      <th className="border border-gray-300 px-3 py-2 text-left">New Category</th>
                    </tr>
                  </thead>
                  <tbody>
                    {status.detailed_changes.map((change, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="border border-gray-300 px-3 py-2 text-sm">
                          {change.date ? new Date(change.date).toLocaleDateString() : 'N/A'}
                        </td>
                        <td className="border border-gray-300 px-3 py-2 text-sm">
                          {change.description}
                        </td>
                        <td className="border border-gray-300 px-3 py-2 text-sm">
                          ${Math.abs(change.amount).toFixed(2)}
                        </td>
                        <td className="border border-gray-300 px-3 py-2 text-sm">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            change.account_type === 'checking' 
                              ? 'bg-blue-100 text-blue-800' 
                              : 'bg-purple-100 text-purple-800'
                          }`}>
                            {change.account_type === 'checking' ? '🏦 Checking' : '💳 Credit'}
                          </span>
                        </td>
                        <td className="border border-gray-300 px-3 py-2 text-sm">
                          <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs">
                            {change.original_category}
                          </span>
                        </td>
                        <td className="border border-gray-300 px-3 py-2 text-sm">
                          <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                            {change.new_category}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No detailed changes available.</p>
            )}

                         <div className="flex justify-between items-center mt-6">
               <button
                 onClick={() => setShowDetailsModal(false)}
                 className="flex items-center space-x-2 px-4 py-2 text-gray-600 bg-gray-100 rounded hover:bg-gray-200"
               >
                 <span>←</span>
                 <span>Back to Transactions</span>
               </button>
               <button
                 onClick={clearAllTemporary}
                 disabled={isClearing}
                 className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
               >
                 {isClearing ? 'Clearing...' : 'Reset All Changes'}
               </button>
             </div>
          </div>
        </div>
      )}
    </>
  )
}

const TransactionTable = ({ filters, accountType, temporaryCategories = {} }) => {
  const [sortConfig, setSortConfig] = useState({ key: 'date', direction: 'desc' })
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage, setItemsPerPage] = useState(25)
  const [editModalOpen, setEditModalOpen] = useState(false)
  const [editingTransaction, setEditingTransaction] = useState(null)
  const { data: transactions, isLoading, error, refetch } = useTransactions(filters)

  // Apply temporary categories and sort transactions
  const sortedTransactions = useMemo(() => {
    if (!transactions) return []
    
    // Apply temporary categories to transactions
    const transactionsWithTempCategories = transactions.map(transaction => ({
      ...transaction,
      category: temporaryCategories[transaction.id] || transaction.category,
      isTemporary: !!temporaryCategories[transaction.id]
    }))
    
    const sortedArray = [...transactionsWithTempCategories].sort((a, b) => {
      const aValue = a[sortConfig.key]
      const bValue = b[sortConfig.key]
      
      if (sortConfig.direction === 'asc') {
        return aValue > bValue ? 1 : -1
      } else {
        return aValue < bValue ? 1 : -1
      }
    })
    
    return sortedArray
  }, [transactions, sortConfig, temporaryCategories])

  // Paginate transactions
  const paginatedTransactions = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage
    const endIndex = startIndex + itemsPerPage
    return sortedTransactions.slice(startIndex, endIndex)
  }, [sortedTransactions, currentPage, itemsPerPage])

  // Calculate pagination info
  const totalPages = Math.ceil(sortedTransactions.length / itemsPerPage)
  const startItem = (currentPage - 1) * itemsPerPage + 1
  const endItem = Math.min(currentPage * itemsPerPage, sortedTransactions.length)

  const handleSort = (key) => {
    let direction = 'asc'
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc'
    }
    setSortConfig({ key, direction })
    setCurrentPage(1) // Reset to first page when sorting
  }

  const handlePageChange = (page) => {
    setCurrentPage(page)
    // Scroll to top of table
    document.querySelector('[data-transaction-table]')?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleItemsPerPageChange = (newItemsPerPage) => {
    setItemsPerPage(newItemsPerPage)
    setCurrentPage(1)
  }

  const getSortIcon = (columnKey) => {
    if (sortConfig.key !== columnKey) return '↕️'
    return sortConfig.direction === 'asc' ? '↑' : '↓'
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount)
  }

  const exportToCSV = (transactions, accountType) => {
    // Create CSV headers
    const headers = ['Date', 'Description', 'Category', 'Type', 'Amount', 'Status']
    
    // Create CSV rows
    const csvContent = [
      headers.join(','),
      ...transactions.map(t => [
        t.date,
        `"${t.description.replace(/"/g, '""')}"`, // Escape quotes in description
        t.category,
        t.type,
        t.amount,
        t.status
      ].join(','))
    ].join('\n')
    
    // Create and download file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    
    // Generate filename with current month
    const monthStr = filters.month || new Date().toISOString().slice(0, 7)
    const filename = `${accountType}_transactions_${monthStr}.csv`
    
    link.setAttribute('href', url)
    link.setAttribute('download', filename)
    link.style.visibility = 'hidden'
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleEditTransaction = (transaction) => {
    setEditingTransaction(transaction)
    setEditModalOpen(true)
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-8">
        <LoadingSpinner message="Loading transactions..." />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-8">
        <ErrorMessage 
          message="Failed to load transactions" 
          onRetry={() => refetch()}
        />
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden" data-transaction-table>
      {/* Table Header */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            {accountType === 'checking' ? 'Checking Account' : 'Credit Account'} Transactions
          </h3>
          <div className="flex items-center space-x-3">
            {/* Legend */}
            <div className="flex items-center space-x-3 text-xs">
              <div className="flex items-center space-x-1">
                <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-purple-100 text-purple-800 border border-purple-300">
                  ⭐ Dex AI
                </span>
              </div>
              <div className="flex items-center space-x-1">
                <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-green-100 text-green-800 border border-green-300">
                  ✨ Manual
                </span>
              </div>
              <div className="flex items-center space-x-1">
                <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-blue-100 text-blue-800">
                  Original
                </span>
              </div>
            </div>
            
            {/* Counters */}
            {(() => {
              const aiCategorizedCount = sortedTransactions.filter(t => t.ai_categorized).length
              const manualEditCount = Object.keys(temporaryCategories).length
              
              return (
                <div className="flex items-center space-x-2">
                  {aiCategorizedCount > 0 && (
                    <div className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium border border-purple-300">
                      ⭐ {aiCategorizedCount} Dex categorized
                    </div>
                  )}
                  {manualEditCount > 0 && (
                    <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium border border-green-300">
                      ✨ {manualEditCount} manual edits
                    </div>
                  )}
                </div>
              )
            })()}
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="px-6 py-3 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-700">
              Showing {startItem}-{endItem} of {sortedTransactions.length} transactions
            </span>
            
            <div className="flex items-center space-x-2">
              <label className="text-sm text-gray-600">Show:</label>
              <select
                value={itemsPerPage}
                onChange={(e) => handleItemsPerPageChange(Number(e.target.value))}
                className="border border-gray-300 rounded px-2 py-1 text-sm"
              >
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
              <span className="text-sm text-gray-600">per page</span>
            </div>
          </div>
          
          {/* Export button */}
          <button 
            onClick={() => exportToCSV(sortedTransactions, accountType)}
            className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 flex items-center space-x-1"
          >
            <span>📥</span>
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Table */}
      {sortedTransactions.length === 0 ? (
        <div className="p-8 text-center">
          <p className="text-gray-500">No transactions found for the selected filters.</p>
        </div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('date')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Date</span>
                      <span>{getSortIcon('date')}</span>
                    </div>
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('description')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Description</span>
                      <span>{getSortIcon('description')}</span>
                    </div>
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('category')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Category</span>
                      <span>{getSortIcon('category')}</span>
                    </div>
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('amount')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Amount</span>
                      <span>{getSortIcon('amount')}</span>
                    </div>
                  </th>
                  <th 
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('status')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Status</span>
                      <span>{getSortIcon('status')}</span>
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {paginatedTransactions.map((transaction, index) => (
                  <TransactionRow 
                    key={transaction.id || index} 
                    transaction={transaction}
                    accountType={accountType}
                    onEdit={(t) => {
                      handleEditTransaction(t)
                    }}
                  />
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-700">
                  Page {currentPage} of {totalPages}
                </div>
                
                <div className="flex items-center space-x-1">
                  {/* Previous button */}
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  
                  {/* Page numbers */}
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    let pageNum
                    if (totalPages <= 5) {
                      pageNum = i + 1
                    } else if (currentPage <= 3) {
                      pageNum = i + 1
                    } else if (currentPage >= totalPages - 2) {
                      pageNum = totalPages - 4 + i
                    } else {
                      pageNum = currentPage - 2 + i
                    }
                    
                    return (
                      <button
                        key={pageNum}
                        onClick={() => handlePageChange(pageNum)}
                        className={`px-3 py-1 text-sm border rounded ${
                          currentPage === pageNum
                            ? 'bg-blue-500 text-white border-blue-500'
                            : 'border-gray-300 hover:bg-gray-50'
                        }`}
                      >
                        {pageNum}
                      </button>
                    )
                  })}
                  
                  {/* Next button */}
                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {editModalOpen && editingTransaction && (
        <TransactionEditModal
          isOpen={editModalOpen}
          onClose={() => {
            setEditModalOpen(false)
            setEditingTransaction(null)
          }}
          transaction={editingTransaction}
          allTransactions={sortedTransactions}
          onSave={() => {
            // Refresh the transaction data after successful edit
            refetch()
          }}
        />
      )}

      <TemporaryCategorizeStatus onRefresh={refetch} />
    </div>
  )
}

export default TransactionTable 