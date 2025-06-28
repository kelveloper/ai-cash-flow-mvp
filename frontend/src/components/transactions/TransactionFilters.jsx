import { useState } from 'react'
import DatePicker from 'react-datepicker'
import 'react-datepicker/dist/react-datepicker.css'

const TransactionFilters = ({ filters, onFiltersChange, onClear }) => {
  const [dateRange, setDateRange] = useState([null, null])
  const [startDate, endDate] = dateRange

  const handleDateChange = (update) => {
    setDateRange(update)
    if (update[0] && update[1]) {
      const start = update[0].toISOString().split('T')[0]
      const end = update[1].toISOString().split('T')[0]
      onFiltersChange({
        ...filters,
        date: `${start},${end}`,
        month: '' // Clear month when using custom date range
      })
    } else if (!update[0] && !update[1]) {
      // Both dates cleared
      onFiltersChange({
        ...filters,
        date: ''
      })
    }
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow mb-6">
      {/* Detailed Filters */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Search */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Search Description
          </label>
          <input
            type="text"
            value={filters.search || ''}
            onChange={(e) => onFiltersChange({
              ...filters,
              search: e.target.value
            })}
            placeholder="Search transactions..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Category Dropdown */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Category
          </label>
          <select
            value={filters.category || ''}
            onChange={(e) => onFiltersChange({
              ...filters,
              category: e.target.value
            })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Categories</option>
            <option value="salary">Salary</option>
            <option value="rent">Rent</option>
            <option value="utilities">Utilities</option>
            <option value="coffee">Coffee</option>
            <option value="marketing">Marketing</option>
            <option value="maintenance">Maintenance</option>
            <option value="supplies">Supplies</option>
            <option value="catering">Catering</option>
            <option value="merchandise">Merchandise</option>
            <option value="pastry">Pastry</option>
            <option value="sandwich">Sandwich</option>
            <option value="misc">Miscellaneous</option>
          </select>
        </div>

        {/* Amount Range */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Amount Range
          </label>
          <div className="flex space-x-2">
            <input
              type="number"
              placeholder="Min"
              value={filters.minAmount || ''}
              onChange={(e) => onFiltersChange({
                ...filters,
                minAmount: e.target.value
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="number"
              placeholder="Max"
              value={filters.maxAmount || ''}
              onChange={(e) => onFiltersChange({
                ...filters,
                maxAmount: e.target.value
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Date Range Picker */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Custom Date Range
          </label>
          <DatePicker
            selectsRange={true}
            startDate={startDate}
            endDate={endDate}
            onChange={handleDateChange}
            placeholderText="Select date range"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            dateFormat="yyyy-MM-dd"
            isClearable={true}
          />
        </div>
      </div>

      {/* Clear Filters Button */}
      <div className="mt-4 flex justify-end">
        <button
          onClick={() => {
            setDateRange([null, null])
            onClear()
          }}
          className="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded hover:bg-gray-200 transition-colors"
        >
          Clear All Filters
        </button>
      </div>
    </div>
  )
}

export default TransactionFilters 