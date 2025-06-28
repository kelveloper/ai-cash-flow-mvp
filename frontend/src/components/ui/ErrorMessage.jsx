const ErrorMessage = ({ message, onRetry, showRetry = true }) => {
  return (
    <div className="flex flex-col items-center justify-center p-4 text-center">
      <div className="text-red-500 text-4xl mb-2">⚠️</div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">Something went wrong</h3>
      <p className="text-sm text-gray-600 mb-4">{message}</p>
      {showRetry && onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Try Again
        </button>
      )}
    </div>
  )
}

export default ErrorMessage 