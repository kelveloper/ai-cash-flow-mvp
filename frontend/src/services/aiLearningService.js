class AILearningService {
  constructor() {
    // In-memory storage for learning patterns
    this.learningPatterns = new Map()
    this.manualCorrections = []
    this.suggestedChanges = []
  }

  // Learn from a manual category edit
  learnFromEdit(transaction, oldCategory, newCategory) {
    console.log(`🧠 AI Learning: ${transaction.description} changed from ${oldCategory} to ${newCategory}`)
    
    // Store the manual correction
    const correction = {
      id: Date.now(),
      transaction,
      oldCategory,
      newCategory,
      description: transaction.description,
      amount: transaction.amount,
      timestamp: new Date().toISOString()
    }
    
    this.manualCorrections.push(correction)
    
    // Extract learning patterns from the description
    const patterns = this.extractPatterns(transaction.description, newCategory)
    patterns.forEach(pattern => {
      if (!this.learningPatterns.has(pattern)) {
        this.learningPatterns.set(pattern, {
          category: newCategory,
          confidence: 1,
          examples: []
        })
      } else {
        // Strengthen the pattern
        const existing = this.learningPatterns.get(pattern)
        existing.confidence += 0.5
        existing.category = newCategory // Update to latest correction
      }
      
      this.learningPatterns.get(pattern).examples.push({
        description: transaction.description,
        amount: transaction.amount,
        timestamp: correction.timestamp
      })
    })
    
    console.log(`🧠 Learning patterns updated:`, Array.from(this.learningPatterns.entries()))
    
    return correction
  }

  // Extract meaningful patterns from transaction description
  extractPatterns(description, category) {
    const patterns = new Set()
    const words = description.toLowerCase().split(/\s+/)
    
    // Add full description pattern (exact match)
    patterns.add(description.toLowerCase())
    
    // Add significant words (filter out common words)
    const stopWords = new Set(['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an'])
    words.forEach(word => {
      if (word.length > 3 && !stopWords.has(word)) {
        patterns.add(word)
      }
    })
    
    // Add merchant patterns (common patterns like store names)
    const merchantPatterns = [
      /(\w+)\s*(whse|store|market|cafe|restaurant|gas|pharmacy)/i,
      /^(\w+)\*/i, // Square/Stripe patterns like "SQ *MERCHANT"
      /(\w+)\.com/i,
      /(\w+)\s*#\d+/i // Store numbers like "TARGET #123"
    ]
    
    merchantPatterns.forEach(pattern => {
      const match = description.match(pattern)
      if (match && match[1]) {
        patterns.add(match[1].toLowerCase())
      }
    })
    
    return Array.from(patterns)
  }

  // Analyze transactions and suggest changes based on learned patterns
  analyzeSimilarTransactions(allTransactions) {
    const suggestions = []
    
    allTransactions.forEach(transaction => {
      // Skip transactions that already have manual edits
      if (this.manualCorrections.some(c => c.transaction.id === transaction.id)) {
        return
      }
      
      const suggestedCategory = this.predictCategory(transaction.description)
      
      if (suggestedCategory && 
          suggestedCategory.category !== transaction.category && 
          suggestedCategory.confidence >= 0.7) {
        
        suggestions.push({
          transaction,
          currentCategory: transaction.category,
          suggestedCategory: suggestedCategory.category,
          confidence: suggestedCategory.confidence,
          reason: suggestedCategory.reason,
          examples: suggestedCategory.examples
        })
      }
    })
    
    this.suggestedChanges = suggestions
    console.log(`🤖 AI found ${suggestions.length} suggested changes:`, suggestions)
    
    return suggestions
  }

  // Predict category for a transaction description based on learned patterns
  predictCategory(description) {
    let bestMatch = null
    let highestScore = 0
    
    for (const [pattern, data] of this.learningPatterns.entries()) {
      let score = 0
      
      // Exact description match gets highest score
      if (description.toLowerCase() === pattern) {
        score = data.confidence * 2
      }
      // Partial word matches
      else if (description.toLowerCase().includes(pattern)) {
        score = data.confidence * 1.5
      }
      // Word boundary matches (whole words)
      else if (new RegExp(`\\b${pattern}\\b`, 'i').test(description)) {
        score = data.confidence * 1.2
      }
      
      if (score > highestScore && score >= 0.7) {
        highestScore = score
        bestMatch = {
          category: data.category,
          confidence: Math.min(score / 2, 1), // Normalize confidence
          reason: `Similar to: ${data.examples[0]?.description || pattern}`,
          examples: data.examples.slice(0, 3) // Show top 3 examples
        }
      }
    }
    
    return bestMatch
  }

  // Get learning statistics
  getLearningStats() {
    return {
      totalCorrections: this.manualCorrections.length,
      learningPatterns: this.learningPatterns.size,
      suggestedChanges: this.suggestedChanges.length,
      recentCorrections: this.manualCorrections.slice(-5),
      topPatterns: Array.from(this.learningPatterns.entries())
        .sort((a, b) => b[1].confidence - a[1].confidence)
        .slice(0, 10)
        .map(([pattern, data]) => ({
          pattern,
          category: data.category,
          confidence: data.confidence,
          examples: data.examples.length
        }))
    }
  }

  // Apply a suggested change
  applySuggestedChange(suggestionId, transactions) {
    const suggestion = this.suggestedChanges.find((s, index) => index === suggestionId)
    if (!suggestion) return null

    // Learn from this application (treat as manual correction)
    this.learnFromEdit(
      suggestion.transaction,
      suggestion.currentCategory,
      suggestion.suggestedCategory
    )

    // Remove from suggestions
    this.suggestedChanges.splice(suggestionId, 1)

    return {
      transactionId: suggestion.transaction.id,
      newCategory: suggestion.suggestedCategory,
      oldCategory: suggestion.currentCategory
    }
  }

  // Reset learning (for testing or fresh start)
  resetLearning() {
    this.learningPatterns.clear()
    this.manualCorrections = []
    this.suggestedChanges = []
    console.log('🧠 AI Learning reset')
  }

  // Export learning data (for persistence if needed later)
  exportLearningData() {
    return {
      patterns: Array.from(this.learningPatterns.entries()),
      corrections: this.manualCorrections,
      timestamp: new Date().toISOString()
    }
  }

  // Import learning data (for persistence if needed later)
  importLearningData(data) {
    this.learningPatterns = new Map(data.patterns || [])
    this.manualCorrections = data.corrections || []
    this.suggestedChanges = []
    console.log('🧠 AI Learning data imported')
  }
}

// Create a singleton instance
export const aiLearningService = new AILearningService()
export default aiLearningService 