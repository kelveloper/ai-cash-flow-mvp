import api from './api'

export const aiService = {
  // Categorize a single transaction description (basic)
  categorizeTransaction: async (description) => {
    const response = await api.post('/categorize-transaction', { description })
    return response.data
  },

  // Categorize a single transaction with enhanced AI (NEW - with merchant enrichment)
  categorizeTransactionEnhanced: async (description, amount = null) => {
    const response = await api.post('/categorize-transaction-enhanced', { 
      description,
      amount 
    })
    return response.data
  },

  // Categorize all transactions for a specific month
  categorizeMonth: async (month) => {
    const response = await api.post('/categorize-month', { month })
    return response.data
  },

  // Generate enhanced categorization PDF report
  generateCategorizationPDF: async (month, accountType, withChanges = false, categorizeResult = null, currentTransactions = null) => {
    const response = await api.post('/generate-categorization-pdf', {
      month,
      accountType,
      withChanges,
      categorizeResult,
      currentTransactions
    }, {
      responseType: 'blob'
    })
    return response.data
  },

  // Get forecast data
  getForecast: async (startDate, endDate, category = null) => {
    const params = {
      start_date: startDate,
      end_date: endDate,
    }
    if (category) {
      params.category = category
    }
    
    const response = await api.get('/forecast', { params })
    return response.data
  },

  // Get AI insights
  getInsights: async (category = null) => {
    const params = category ? { category } : {}
    const response = await api.get('/insights', { params })
    return response.data
  },

  // Apply categorization suggestions temporarily (will reset when app restarts)
  applyCategorizations: async (suggestions) => {
    const response = await api.post('/apply-categorizations', { 
      suggestions: suggestions 
    })
    return response.data
  }
} 