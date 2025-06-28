import { useState, useEffect } from 'react'
import { aiService } from '../../services/aiService'

const DexChatbot = ({ accountType, currentMonth, onTemporaryCategorizations }) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [lastCategorized, setLastCategorized] = useState(null)
  const [categorizeResult, setCategorizeResult] = useState(null)
  const [showConfirmDialog, setShowConfirmDialog] = useState(false)
  const [isPDFLoading, setIsPDFLoading] = useState(false)
  const [currentTransactions, setCurrentTransactions] = useState(null)
  const [showPreviewModal, setShowPreviewModal] = useState(false)
  const [previewChanges, setPreviewChanges] = useState(null)
  const [isLoadingPreview, setIsLoadingPreview] = useState(false)

  // Reset categorization result when month or account type changes
  useEffect(() => {
    setCategorizeResult(null)
    setLastCategorized(null)
    setCurrentTransactions(null)
  }, [currentMonth, accountType])

  const fetchCurrentTransactions = async () => {
    try {
      console.log(`[DexChatbot] Fetching transactions for month=${currentMonth}, accountType=${accountType}`)
      const response = await fetch(`/api/transactions?month=${currentMonth}&account_type=${accountType}`)
      if (response.ok) {
        const data = await response.json()
        console.log('[DexChatbot] API response:', data)
        // Extract transactions array from the response object
        const transactionsArray = Array.isArray(data?.transactions) ? data.transactions : []
        console.log(`[DexChatbot] Extracted ${transactionsArray.length} transactions`)
        setCurrentTransactions(transactionsArray)
        return transactionsArray
      } else {
        console.error('[DexChatbot] API response not OK:', response.status, response.statusText)
      }
    } catch (error) {
      console.error('Error fetching current transactions:', error)
      setCurrentTransactions([])
    }
    return []
  }

  const handleCategorizeRequest = async () => {
    // First, fetch current transactions to show in confirmation dialog
    await fetchCurrentTransactions()
    setShowConfirmDialog(true)
  }

  const handleConfirmCategorization = async () => {
    setShowConfirmDialog(false)
    setIsLoading(true)
    try {
      const result = await aiService.categorizeMonth(currentMonth)
      setCategorizeResult(result)
      setLastCategorized(new Date())
      
      // Apply temporary categorizations to the backend AND UI
      if (result.suggestions && result.suggestions.length > 0) {
        console.log(`🚀 Applying ${result.suggestions.length} temporary categorizations...`)
        
        // Apply to backend temporarily
        await aiService.applyCategorizations(result.suggestions)
        
        // Also apply to UI if callback exists
        if (onTemporaryCategorizations) {
          onTemporaryCategorizations(result.suggestions)
        }
        
        console.log('✅ Temporary categorizations applied successfully!')
      }

      // Automatically generate PDF with changes
      await generatePDFReport(true, result)
    } catch (error) {
      console.error('Error categorizing transactions:', error)
      setCategorizeResult({ error: 'Failed to categorize transactions. Please try again.' })
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeclineCategorization = async () => {
    setShowConfirmDialog(false)
    // Generate PDF with current state (no changes)
    await generatePDFReport(false)
  }

  const generatePDFReport = async (withChanges = false, categorizeResult = null) => {
    setIsPDFLoading(true)
    try {
      let endpoint = '/api/generate-categorization-pdf'
      let requestBody = {
        month: currentMonth,
        accountType: accountType,
        withChanges: withChanges
      }

      if (withChanges && categorizeResult) {
        requestBody.categorizeResult = categorizeResult
      }

      if (currentTransactions && Array.isArray(currentTransactions)) {
        requestBody.currentTransactions = currentTransactions
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      })

      if (!response.ok) {
        throw new Error('Failed to generate PDF report')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${currentMonth}_${accountType}_categorization_report.pdf`
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error generating PDF:', error)
      setCategorizeResult({ error: 'Failed to generate PDF report. Please try again.' })
    } finally {
      setIsPDFLoading(false)
    }
  }

  const formatMonth = (monthStr) => {
    // Parse the month string (YYYY-MM format) and create date in UTC to avoid timezone issues
    const [year, month] = monthStr.split('-')
    const date = new Date(parseInt(year), parseInt(month) - 1, 1) // month is 0-indexed
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
  }

  const getCategoryStats = () => {
    // Add comprehensive validation
    if (!currentTransactions || !Array.isArray(currentTransactions) || currentTransactions.length === 0) {
      return null
    }
    
    const categories = {}
    const uncategorized = []
    
    try {
      currentTransactions.forEach(transaction => {
        if (!transaction || typeof transaction !== 'object') {
          return // Skip invalid transactions
        }
        
        const category = transaction.category || 'uncategorized'
        
        // Use the same logic as backend: case-insensitive check for categories that can be AI processed
        const categoryLower = category.toLowerCase()
        const isUncategorized = !category || 
                               categoryLower === 'misc' || 
                               categoryLower === 'miscellaneous' || 
                               categoryLower === 'uncategorized' || 
                               categoryLower === ''
        
        if (isUncategorized) {
          uncategorized.push(transaction)
        } else {
          categories[category] = (categories[category] || 0) + 1
        }
      })
      
      return {
        total: currentTransactions.length,
        categorized: Object.values(categories).reduce((sum, count) => sum + count, 0),
        uncategorized: uncategorized.length,
        uncategorizedTransactions: uncategorized,
        categories: categories
      }
    } catch (error) {
      console.error('Error calculating category stats:', error)
      return {
        total: 0,
        categorized: 0,
        uncategorized: 0,
        uncategorizedTransactions: [],
        categories: {}
      }
    }
  }

  const handleShowPreview = async () => {
    setIsLoadingPreview(true)
    setShowPreviewModal(true)
    
    try {
      // Get preview of what would be categorized
      const result = await aiService.categorizeMonth(currentMonth)
      setPreviewChanges(result)
    } catch (error) {
      console.error('Error getting preview:', error)
      setPreviewChanges({ error: 'Failed to load preview' })
    } finally {
      setIsLoadingPreview(false)
    }
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Confirmation Dialog */}
      {showConfirmDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  Categorize Transactions for {formatMonth(currentMonth)}?
                </h3>
                <button
                  onClick={() => setShowConfirmDialog(false)}
                  className="text-gray-500 hover:text-gray-700 text-xl"
                >
                  ✕
                </button>
              </div>
              
              {currentTransactions && (
                <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                  <h4 className="font-medium text-sm text-gray-900 mb-2">Current Status:</h4>
                  {(() => {
                    const stats = getCategoryStats()
                    return stats ? (
                      <div className="text-sm text-gray-600 space-y-1">
                        <p>• Total transactions: {stats.total}</p>
                        <p>• Already categorized: {stats.categorized}</p>
                        <p>• Uncategorized: {stats.uncategorized}</p>
                        {stats.uncategorized > 0 && (
                          <p className="text-blue-600 font-medium">
                            <button
                              onClick={handleShowPreview}
                              className="text-blue-600 hover:text-blue-800 underline cursor-pointer"
                            >
                              ✨ AI will analyze {stats.uncategorized} transactions (click to preview which will be categorized)
                            </button>
                          </p>
                        )}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-600">Loading transaction data...</p>
                    )
                  })()}
                </div>
              )}

              <div className="text-sm text-gray-600 mb-6">
                <p className="mb-2">Choose an option:</p>
                <div className="space-y-2">
                  <div className="flex items-start space-x-2">
                    <span className="text-green-600 font-bold">YES:</span>
                    <span>Apply AI categorization and generate a detailed PDF report showing all changes</span>
                  </div>
                  <div className="flex items-start space-x-2">
                    <span className="text-blue-600 font-bold">NO:</span>
                    <span>Keep current categories and generate a PDF report of the existing categorization</span>
                  </div>
                </div>
              </div>

              <div className="flex space-x-3">
                <button
                  onClick={handleConfirmCategorization}
                  disabled={isLoading || isPDFLoading}
                  className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isLoading ? 'Processing...' : 'Yes, Categorize'}
                </button>
                <button
                  onClick={handleDeclineCategorization}
                  disabled={isLoading || isPDFLoading}
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isPDFLoading ? 'Generating PDF...' : 'No, Just Report'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Chat Window */}
      {isExpanded && (
        <div className="mb-4 w-96 bg-white rounded-lg shadow-xl border border-gray-200 flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-blue-50 rounded-t-lg">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                D
              </div>
              <div>
                <h3 className="font-medium text-gray-900">Dex AI Assistant</h3>
                <p className="text-xs text-gray-500">Financial Helper</p>
              </div>
            </div>
            <button
              onClick={() => setIsExpanded(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>

          {/* Content */}
          <div className="p-4 space-y-4">
            {/* Current Context */}
            <div className="bg-gray-50 p-3 rounded-lg">
              <h4 className="font-medium text-sm text-gray-900 mb-1">Current Context</h4>
              <p className="text-sm text-gray-600">
                <span className="capitalize">{accountType}</span> Account • {formatMonth(currentMonth)}
              </p>
            </div>

            {/* Action Buttons */}
            <div className="space-y-3">
              <h4 className="font-medium text-sm text-gray-900">AI Actions</h4>
              
              {/* Categorize Month Button */}
              <button
                onClick={handleCategorizeRequest}
                disabled={isLoading || isPDFLoading}
                className="w-full p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-left"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-sm">
                      {isLoading || isPDFLoading ? 'Processing...' : 'Smart Categorization'}
                    </div>
                    <div className="text-xs text-blue-100 mt-1">
                      AI categorize + detailed PDF report for {formatMonth(currentMonth)}
                    </div>
                  </div>
                  <div className="text-lg">
                    {isLoading || isPDFLoading ? (
                      <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full"></div>
                    ) : (
                      '🎯'
                    )}
                  </div>
                </div>
              </button>

              {/* Generate Report Only Button */}
              <button
                onClick={() => generatePDFReport(false)}
                disabled={isLoading || isPDFLoading}
                className="w-full p-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors text-left"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-sm">Generate Report Only</div>
                    <div className="text-xs text-gray-500 mt-1">
                      PDF report of current categorization
                    </div>
                  </div>
                  <div className="text-lg">📊</div>
                </div>
              </button>

              {/* Get Insights Button */}
              <button
                className="w-full p-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors text-left"
                onClick={() => {
                  // Placeholder for future insights functionality
                  alert('Advanced insights feature coming soon!')
                }}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-sm">Get Spending Insights</div>
                    <div className="text-xs text-gray-500 mt-1">
                      Analyze patterns and trends
                    </div>
                  </div>
                  <div className="text-lg">🔮</div>
                </div>
              </button>
            </div>

            {/* Results */}
            {categorizeResult && (
              <div className="border-t border-gray-200 pt-4">
                <h4 className="font-medium text-sm text-gray-900 mb-2">Last Result</h4>
                {categorizeResult.error ? (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-700">{categorizeResult.error}</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                      <p className="text-sm text-green-800 font-medium mb-1">
                        ✅ Categorization Complete!
                      </p>
                      <p className="text-sm text-green-700">
                        Successfully categorized {categorizeResult.categorized_count || 0} transactions
                      </p>
                      <p className="text-xs text-green-600 mt-1">
                        PDF report generated and downloaded automatically
                      </p>
                      {lastCategorized && (
                        <p className="text-xs text-green-600">
                          Completed at {lastCategorized.toLocaleTimeString('en-US', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          })}
                        </p>
                      )}
                      
                      {/* Category breakdown */}
                      {categorizeResult.suggestions && categorizeResult.suggestions.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-green-200">
                          <p className="text-xs text-green-600 font-medium mb-1">Categories applied:</p>
                          <div className="flex flex-wrap gap-1">
                            {[...new Set(categorizeResult.suggestions.map(s => s.category))]
                              .slice(0, 6)
                              .map(category => (
                                <span key={category} className="inline-block bg-green-100 text-green-700 px-2 py-0.5 rounded text-xs">
                                  {category}
                                </span>
                              ))}
                            {[...new Set(categorizeResult.suggestions.map(s => s.category))].length > 6 && (
                              <span className="inline-block bg-green-100 text-green-700 px-2 py-0.5 rounded text-xs">
                                +{[...new Set(categorizeResult.suggestions.map(s => s.category))].length - 6} more
                              </span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Chat Toggle Button */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-14 h-14 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 flex items-center justify-center transition-all"
      >
        {isExpanded ? '✕' : '🤖'}
      </button>

      {/* Preview Changes Modal */}
      {showPreviewModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  🔮 AI Categorization Preview for {formatMonth(currentMonth)}
                </h3>
                <button
                  onClick={() => setShowPreviewModal(false)}
                  className="text-gray-500 hover:text-gray-700 text-xl"
                >
                  ✕
                </button>
              </div>

              {isLoadingPreview ? (
                <div className="text-center py-8">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <p className="mt-2 text-gray-600">Analyzing transactions...</p>
                </div>
              ) : previewChanges?.error ? (
                <div className="text-center py-8 text-red-600">
                  <p>❌ {previewChanges.error}</p>
                </div>
              ) : previewChanges?.suggestions && previewChanges.suggestions.length > 0 ? (
                <div>
                  <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                    <p className="text-blue-800 text-sm">
                      📊 Found {previewChanges.suggestions.length} transactions that will be categorized with AI confidence ≥ 30%
                    </p>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full border-collapse border border-gray-300">
                      <thead>
                        <tr className="bg-gray-50">
                          <th className="border border-gray-300 px-3 py-2 text-left text-sm">Description</th>
                          <th className="border border-gray-300 px-3 py-2 text-left text-sm">Amount</th>
                          <th className="border border-gray-300 px-3 py-2 text-left text-sm">Current</th>
                          <th className="border border-gray-300 px-3 py-2 text-left text-sm">AI Prediction</th>
                          <th className="border border-gray-300 px-3 py-2 text-left text-sm">Confidence</th>
                        </tr>
                      </thead>
                      <tbody>
                        {previewChanges.suggestions.map((suggestion, index) => {
                          // Find the corresponding transaction
                          const transaction = getCategoryStats()?.uncategorizedTransactions?.find(
                            t => t.id === suggestion.id
                          )
                          return (
                            <tr key={index} className="hover:bg-gray-50">
                              <td className="border border-gray-300 px-3 py-2 text-sm">
                                {transaction?.description || 'Unknown'}
                              </td>
                              <td className="border border-gray-300 px-3 py-2 text-sm">
                                ${Math.abs(transaction?.amount || 0).toFixed(2)}
                              </td>
                              <td className="border border-gray-300 px-3 py-2 text-sm">
                                <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs">
                                  {suggestion.original_category || 'misc'}
                                </span>
                              </td>
                              <td className="border border-gray-300 px-3 py-2 text-sm">
                                <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                                  {suggestion.category}
                                </span>
                              </td>
                              <td className="border border-gray-300 px-3 py-2 text-sm">
                                <span className={`px-2 py-1 rounded text-xs ${
                                  suggestion.confidence >= 0.7 
                                    ? 'bg-green-100 text-green-800' 
                                    : suggestion.confidence >= 0.5
                                    ? 'bg-yellow-100 text-yellow-800'
                                    : 'bg-orange-100 text-orange-800'
                                }`}>
                                  {(suggestion.confidence * 100).toFixed(1)}%
                                </span>
                              </td>
                            </tr>
                          )
                        })}
                      </tbody>
                    </table>
                  </div>

                  <div className="mt-4 p-3 bg-gray-50 rounded text-sm text-gray-600">
                    <p><strong>Confidence Levels:</strong></p>
                    <p>• <span className="px-1 bg-green-100 text-green-800 rounded">70%+</span> High confidence</p>
                    <p>• <span className="px-1 bg-yellow-100 text-yellow-800 rounded">50-69%</span> Medium confidence</p>
                    <p>• <span className="px-1 bg-orange-100 text-orange-800 rounded">30-49%</span> Low confidence</p>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-600">
                  <p>🤔 No categorization changes predicted</p>
                  <p className="text-sm mt-2">All transactions may already have good categories or AI confidence is too low.</p>
                </div>
              )}

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowPreviewModal(false)}
                  className="px-4 py-2 text-gray-600 bg-gray-100 rounded hover:bg-gray-200"
                >
                  Close Preview
                </button>
                {previewChanges?.suggestions && previewChanges.suggestions.length > 0 && (
                  <button
                    onClick={() => {
                      setShowPreviewModal(false)
                      handleConfirmCategorization()
                    }}
                    className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                  >
                    Apply These Changes
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default DexChatbot 