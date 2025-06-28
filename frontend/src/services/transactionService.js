import api from './api'

export const transactionService = {
  // Get all transactions with optional filters and pagination
  getTransactions: async (params = {}) => {
    try {
      // Add default pagination to prevent large responses
      const defaultParams = {
        limit: 100, // Default to 100 transactions per request
        offset: 0,
        ...params
      }
      
      console.log(`[TransactionService] Fetching transactions with params:`, defaultParams)
      
      const response = await api.get('/transactions', { params: defaultParams })
      const transactions = response.data.transactions || []
      
      console.log(`[TransactionService] Retrieved ${transactions.length} transactions`)
      return transactions
    } catch (error) {
      console.error('[TransactionService] Error fetching transactions:', error)
      
      // Fallback strategy for timeouts - try with smaller limit
      if (error.code === 'ECONNABORTED' && params.limit > 50) {
        console.warn('[TransactionService] Timeout detected, retrying with smaller limit...')
        return this.getTransactions({
          ...params,
          limit: Math.min(params.limit || 100, 50)
        })
      }
      
      throw error
    }
  },

  // Get transactions for a specific month (optimized)
  getTransactionsForMonth: async (month, accountType = null, limit = 200) => {
    try {
      const params = {
        month,
        limit,
        offset: 0
      }
      
      if (accountType) {
        params.account_type = accountType
      }
      
      console.log(`[TransactionService] Fetching month transactions:`, params)
      
      const response = await api.get('/transactions', { params })
      const transactions = response.data.transactions || []
      
      console.log(`[TransactionService] Retrieved ${transactions.length} transactions for ${month}`)
      return transactions
    } catch (error) {
      console.error('[TransactionService] Error fetching month transactions:', error)
      throw error
    }
  },

  // Get account summary
  getAccountSummary: async () => {
    const response = await api.get('/account-summary')
    return response.data
  },

  // Get transaction categories
  getCategories: async () => {
    const response = await api.get('/categories')
    return response.data
  },

  // Create new transaction
  createTransaction: async (transaction) => {
    const response = await api.post('/transactions', transaction)
    return response.data
  },

  // Update transaction
  updateTransaction: async (id, updates) => {
    const response = await api.put(`/transactions/${id}`, updates)
    return response.data
  },

  // Delete transaction
  deleteTransaction: async (id) => {
    const response = await api.delete(`/transactions/${id}`)
    return response.data
  },

  // Switch data file
  switchData: async (filename) => {
    const response = await api.post(`/switch-data/${filename}`)
    return response.data
  },

  // Export data
  exportData: async (dataType) => {
    const response = await api.post(`/export-data/${dataType}`)
    return response.data
  },

  // Bulk update transaction categories
  updateTransactionCategories: async (updates) => {
    const response = await api.post('/update-transaction-categories', { updates })
    return response.data
  },

  // Generate month PDF
  generateMonthPdf: async (month, transactions = null, noChanges = false) => {
    const response = await api.post('/generate-month-pdf', {
      month,
      transactions,
      no_changes: noChanges
    })
    return response.data
  },

  // Temporary categorization methods
  updateTransactionCategoryTemporary: async (transactionId, category) => {
    const response = await api.post('/apply-categorizations', {
      categorizations: [{
        id: transactionId,
        category: category
      }]
    })
    return response.data
  },

  clearTemporaryCategorizations: async () => {
    const response = await api.post('/clear-temporary-categorizations')
    return response.data
  },

  getTemporaryCategorizationsStatus: async () => {
    const response = await api.get('/temporary-categorizations-status')
    return response.data
  }
} 