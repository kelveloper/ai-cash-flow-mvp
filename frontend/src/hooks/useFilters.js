import { useState, useMemo } from 'react'
import { format, startOfMonth, endOfMonth } from 'date-fns'

export const useFilters = () => {
  const [filters, setFilters] = useState({
    search: '',
    date: '',
    category: '',
    account_type: '',
    month: '2025-06', // Start with June 2025 (current month)
  })

  // Define the current month (June 2025)
  const CURRENT_MONTH = '2025-06'

  // Update a single filter
  const updateFilter = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }))
  }

  // Reset all filters except month
  const resetFilters = () => {
    setFilters(prev => ({
      search: '',
      date: '',
      category: '',
      account_type: '',
      month: prev.month, // Keep current month
    }))
  }

  // Update multiple filters at once
  const updateFilters = (newFilters) => {
    setFilters(newFilters)
  }

  // Set month and clear custom date range
  const setMonth = (month) => {
    setFilters(prev => ({
      ...prev,
      month,
      date: '', // Clear custom date range when using month navigation
    }))
  }

  // Navigate to previous/next month (with limits)
  const navigateMonth = (direction) => {
    try {
      const [year, month] = filters.month.split('-').map(Number)
      let newYear = year
      let newMonth = month
      
      if (direction === 'next') {
        // Don't allow navigation beyond current month
        if (filters.month >= CURRENT_MONTH) {
          return
        }
        newMonth += 1
        if (newMonth > 12) {
          newMonth = 1
          newYear += 1
        }
      } else {
        newMonth -= 1
        if (newMonth < 1) {
          newMonth = 12
          newYear -= 1
        }
      }
      
      const formattedMonth = `${newYear}-${newMonth.toString().padStart(2, '0')}`
      setMonth(formattedMonth)
    } catch (error) {
      console.error('Error in navigateMonth:', error)
    }
  }

  // Check if we can navigate in a given direction
  const canNavigate = (direction) => {
    if (direction === 'next') {
      return filters.month < CURRENT_MONTH
    }
    return true // Always allow going back
  }

  // Get clean filters for API (remove empty values)
  const cleanFilters = useMemo(() => {
    return Object.entries(filters).reduce((acc, [key, value]) => {
      if (value && value.trim() !== '') {
        acc[key] = value
      }
      return acc
    }, {})
  }, [filters])

  return {
    filters,
    cleanFilters,
    updateFilter,
    updateFilters,
    resetFilters,
    setMonth,
    navigateMonth,
    canNavigate,
  }
} 