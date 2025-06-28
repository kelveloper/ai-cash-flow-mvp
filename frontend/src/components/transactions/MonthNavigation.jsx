import { format } from 'date-fns'

const MonthNavigation = ({ currentMonth, onMonthChange, onNavigate, canNavigate }) => {
  const formatMonth = (monthString) => {
    // Parse the month string (YYYY-MM) to avoid timezone issues
    const [year, month] = monthString.split('-')
    const date = new Date(parseInt(year), parseInt(month) - 1, 1) // Month is 0-indexed in Date constructor
    return format(date, 'MMMM yyyy')
  }

  return (
    <div className="flex items-center space-x-4">
      <button
        onClick={() => onNavigate('previous')}
        className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
        title="Previous month"
      >
        ← Previous
      </button>
      
      <div className="flex items-center space-x-2">
        <span className="text-lg font-medium text-gray-900">
          {formatMonth(currentMonth)}
        </span>
      </div>

      {canNavigate && canNavigate('next') && (
        <button
          onClick={() => onNavigate('next')}
          className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
          title="Next month"
        >
          Next →
        </button>
      )}
    </div>
  )
}

export default MonthNavigation 