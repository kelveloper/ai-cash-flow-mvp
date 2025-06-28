import { useState, useEffect } from 'react'
import { transactionService } from '../../services/transactionService'
import aiLearningService from '../../services/aiLearningService'

const TransactionEditModal = ({ transaction, isOpen, onClose, onSave, allTransactions = [] }) => {
  const [category, setCategory] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [suggestions, setSuggestions] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false)

  // Categories for dropdown - using Capital One format
  const categories = [
    'Dining & Restaurants', 'Groceries', 'Shopping & Merchandise', 'Gas & Automotive', 
    'Phone, Cable & Utilities', 'Bills & Utilities', 'Travel', 'Entertainment', 
    'Home & Rent/Mortgage', 'Home Maintenance', 'Healthcare', 'Education', 
    'Personal', 'Other'
  ]

  useEffect(() => {
    if (transaction && isOpen) {
      setCategory(transaction.category || '')
      setError('')
      setSuggestions([])
      setShowSuggestions(false)
    }
  }, [transaction, isOpen])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!category.trim()) {
      setError('Please select a category')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      // Update the transaction TEMPORARILY instead of permanently
      await transactionService.updateTransactionCategoryTemporary(transaction.id, category)
      
      // Learn from this manual edit (only if category actually changed)
      if (category !== transaction.category) {
        console.log('🧠 Learning from manual edit...')
        aiLearningService.learnFromEdit(transaction, transaction.category, category)
        
        // Analyze all transactions for similar patterns
        const newSuggestions = aiLearningService.analyzeSimilarTransactions(allTransactions)
        setSuggestions(newSuggestions)
        
        if (newSuggestions.length > 0) {
          setShowSuggestions(true)
        }
      }
      
      onSave()
      
      // If no suggestions, close the modal
      if (!showSuggestions) {
        onClose()
      }
    } catch (err) {
      setError(err.message || 'Failed to update transaction')
    } finally {
      setIsLoading(false)
    }
  }

  const handleApplySuggestion = async (suggestionIndex) => {
    try {
      const result = aiLearningService.applySuggestedChange(suggestionIndex, allTransactions)
      if (result) {
        // Update the transaction temporarily via API
        await transactionService.updateTransactionCategoryTemporary(result.transactionId, result.newCategory)
        
        // Remove from suggestions list
        setSuggestions(prev => prev.filter((_, index) => index !== suggestionIndex))
        
        // Refresh the transaction table
        onSave()
      }
    } catch (err) {
      console.error('Failed to apply suggestion:', err)
    }
  }

  const handleDismissSuggestion = (suggestionIndex) => {
    setSuggestions(prev => prev.filter((_, index) => index !== suggestionIndex))
  }

  const handleDismissAllSuggestions = () => {
    setSuggestions([])
    setShowSuggestions(false)
    onClose()
  }

  if (!isOpen || !transaction) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">
            {showSuggestions ? '🤖 AI Suggestions' : '✏️ Edit Transaction'}
          </h2>
          <button
            onClick={showSuggestions ? handleDismissAllSuggestions : onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>

        {!showSuggestions ? (
          // Original edit form
          <>
            <div className="mb-4 p-4 bg-gray-50 rounded">
              <p className="text-sm text-gray-600 mb-2">Transaction Details:</p>
              <p className="font-medium">{transaction.description}</p>
              <p className="text-sm text-gray-500">
                ${Math.abs(transaction.amount)} • {new Date(transaction.date).toLocaleDateString()}
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Category
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Select a category</option>
                  {categories.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              {error && (
                <p className="text-red-600 text-sm">{error}</p>
              )}

              <div className="bg-yellow-50 p-3 rounded text-sm text-yellow-800 border border-yellow-200">
                ⚠️ <strong>Temporary Changes:</strong> This change will be temporary and will reset when you stop the app. Original data in Supabase/CSV remains unchanged.
              </div>

              <div className="bg-blue-50 p-3 rounded text-sm text-blue-700">
                💡 <strong>AI Learning:</strong> When you change this category, the AI will learn from your choice and suggest similar changes to other transactions.
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 text-gray-600 bg-gray-100 rounded hover:bg-gray-200"
                  disabled={isLoading}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                  disabled={isLoading}
                >
                  {isLoading ? 'Learning...' : 'Save & Learn'}
                </button>
              </div>
            </form>
          </>
        ) : (
          // AI Suggestions panel
          <div className="space-y-4">
            <div className="bg-green-50 p-4 rounded border border-green-200">
              <div className="flex items-center mb-2">
                <span className="text-2xl mr-2">🧠</span>
                <div>
                  <h3 className="font-semibold text-green-800">AI Learning Complete!</h3>
                  <p className="text-green-700 text-sm">
                    Based on your edit, I found {suggestions.length} similar transactions that might need the same category change.
                  </p>
                </div>
              </div>
            </div>

            {suggestions.length > 0 && (
              <div className="space-y-3">
                <h4 className="font-medium text-gray-800">Suggested Changes:</h4>
                {suggestions.map((suggestion, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{suggestion.transaction.description}</p>
                        <p className="text-sm text-gray-600">
                          ${Math.abs(suggestion.transaction.amount)} • {new Date(suggestion.transaction.date).toLocaleDateString()}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">{suggestion.reason}</p>
                      </div>
                      <div className="ml-4 text-right">
                        <span className="inline-block px-2 py-1 text-xs bg-red-100 text-red-700 rounded">
                          {suggestion.currentCategory}
                        </span>
                        <span className="mx-2">→</span>
                        <span className="inline-block px-2 py-1 text-xs bg-green-100 text-green-700 rounded">
                          {suggestion.suggestedCategory}
                        </span>
                      </div>
                    </div>
                    
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-blue-600">
                        Confidence: {Math.round(suggestion.confidence * 100)}%
                      </span>
                      <div className="space-x-2">
                        <button
                          onClick={() => handleDismissSuggestion(index)}
                          className="text-xs px-3 py-1 text-gray-600 bg-gray-200 rounded hover:bg-gray-300"
                        >
                          Dismiss
                        </button>
                        <button
                          onClick={() => handleApplySuggestion(index)}
                          className="text-xs px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
                        >
                          Apply Change
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div className="flex justify-end space-x-3 pt-4 border-t">
              <button
                onClick={handleDismissAllSuggestions}
                className="px-4 py-2 text-gray-600 bg-gray-100 rounded hover:bg-gray-200"
              >
                Done
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default TransactionEditModal 