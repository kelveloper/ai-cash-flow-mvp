import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { transactionService } from '../services/transactionService'

export const useTransactions = (filters = {}) => {
  return useQuery({
    queryKey: ['transactions', filters],
    queryFn: () => transactionService.getTransactions(filters),
    staleTime: 1000 * 60 * 2, // 2 minutes
    retry: (failureCount, error) => {
      // Retry up to 2 times for timeouts, but not for other errors
      if (error?.code === 'ECONNABORTED' && failureCount < 2) {
        console.warn(`[useTransactions] Retrying after timeout (attempt ${failureCount + 1})`)
        return true
      }
      return false
    },
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 5000), // Exponential backoff
  })
}

// Specialized hook for month-specific transactions
export const useMonthTransactions = (month, accountType = null) => {
  return useQuery({
    queryKey: ['transactions', 'month', month, accountType],
    queryFn: () => transactionService.getTransactionsForMonth(month, accountType),
    staleTime: 1000 * 60 * 5, // 5 minutes for month data
    enabled: !!month, // Only run when month is provided
    retry: (failureCount, error) => {
      if (error?.code === 'ECONNABORTED' && failureCount < 2) {
        console.warn(`[useMonthTransactions] Retrying after timeout (attempt ${failureCount + 1})`)
        return true
      }
      return false
    },
  })
}

export const useAccountSummary = () => {
  return useQuery({
    queryKey: ['account-summary'],
    queryFn: transactionService.getAccountSummary,
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: 1, // Only retry once for account summary
  })
}

export const useCategories = () => {
  return useQuery({
    queryKey: ['categories'],
    queryFn: transactionService.getCategories,
    staleTime: 1000 * 60 * 10, // 10 minutes
    retry: 1,
  })
}

export const useCreateTransaction = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: transactionService.createTransaction,
    onSuccess: () => {
      // Invalidate and refetch transactions
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      queryClient.invalidateQueries({ queryKey: ['account-summary'] })
    },
  })
}

export const useUpdateTransaction = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, updates }) => transactionService.updateTransaction(id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      queryClient.invalidateQueries({ queryKey: ['account-summary'] })
    },
  })
}

export const useDeleteTransaction = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: transactionService.deleteTransaction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      queryClient.invalidateQueries({ queryKey: ['account-summary'] })
    },
  })
}

export const useBulkUpdateCategories = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: transactionService.updateTransactionCategories,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
    },
  })
}

export const useSwitchData = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: transactionService.switchData,
    onSuccess: () => {
      // Invalidate all data when switching datasets
      queryClient.invalidateQueries()
    },
  })
} 