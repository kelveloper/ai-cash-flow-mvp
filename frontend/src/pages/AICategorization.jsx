const AICategorization = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">AI Categorization</h1>
      
      <div className="bg-white p-8 rounded-lg shadow text-center">
        <div className="text-6xl mb-4">🤖</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">AI Categorization Center</h2>
        <p className="text-gray-600 mb-6">
          This dedicated AI categorization page is now integrated into the main Transactions page.
          You can access the AI assistant directly from the transactions view using the floating chat button.
        </p>
        <a 
          href="/transactions" 
          className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition-colors"
        >
          Go to Transactions →
        </a>
      </div>

      <div className="bg-blue-50 p-6 rounded-lg">
        <h3 className="text-lg font-medium text-blue-900 mb-2">💡 New AI Experience</h3>
        <p className="text-blue-800">
          The AI assistant is now seamlessly integrated with your transaction view. 
          You can categorize transactions, get insights, and ask questions without leaving the transactions page!
        </p>
      </div>
    </div>
  )
}

export default AICategorization 