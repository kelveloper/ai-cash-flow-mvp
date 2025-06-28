import { format } from 'date-fns'

const TransactionRow = ({ transaction, accountType, onEdit }) => {
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(Math.abs(amount))
  }

  const getAmountColor = (amount, type) => {
    if (type === 'INCOME') return 'text-green-600'
    return 'text-red-600'
  }

  return (
    <tr className={`hover:bg-gray-50 ${
      transaction.ai_categorized 
        ? 'bg-purple-50 hover:bg-purple-100 border-l-4 border-purple-400' 
        : ''
    }`}>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
        {format(new Date(transaction.date), 'MMM dd, yyyy')}
      </td>
      <td className="px-6 py-4 text-sm text-gray-900">
        <div className="max-w-xs truncate">{transaction.description}</div>
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          transaction.ai_categorized 
            ? 'bg-purple-100 text-purple-800 border border-purple-300 shadow-sm' 
            : transaction.isTemporary || transaction.temp_categorized
            ? 'bg-green-100 text-green-800 border border-green-300' 
            : 'bg-blue-100 text-blue-800'
        }`}>
          {transaction.ai_categorized && '⭐ '}
          {(transaction.isTemporary || transaction.temp_categorized) && !transaction.ai_categorized && '✨ '}
          {transaction.category_display || transaction.category}
        </span>
      </td>
      <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getAmountColor(transaction.amount, transaction.type)}`}>
        {transaction.type === 'INCOME' ? '+' : '-'}{formatCurrency(transaction.amount)}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          transaction.status === 'POSTED' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
        }`}>
          {transaction.status}
        </span>
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        <button 
          onClick={() => onEdit && onEdit(transaction)}
          className="text-blue-600 hover:text-blue-900 hover:underline"
        >
          Edit
        </button>
      </td>
    </tr>
  )
}

export default TransactionRow 