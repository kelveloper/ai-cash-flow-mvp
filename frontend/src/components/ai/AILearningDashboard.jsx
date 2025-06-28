import { useState, useEffect } from 'react'
import aiLearningService from '../../services/aiLearningService'

const AILearningDashboard = ({ isOpen, onClose }) => {
  const [stats, setStats] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    if (isOpen) {
      const learningStats = aiLearningService.getLearningStats()
      setStats(learningStats)
    }
  }, [isOpen])

  if (!isOpen || !stats) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-6xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">🧠 AI Learning Dashboard</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-xl"
          >
            ✕
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 mb-6">
          {[
            { id: 'overview', label: 'Overview', icon: '📊' },
            { id: 'patterns', label: 'Learning Patterns', icon: '🔍' },
            { id: 'corrections', label: 'Recent Corrections', icon: '✏️' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 text-sm font-medium border-b-2 ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <div className="text-2xl font-bold text-blue-600">{stats.totalCorrections}</div>
                <div className="text-sm text-blue-800">Manual Corrections</div>
              </div>
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <div className="text-2xl font-bold text-green-600">{stats.learningPatterns}</div>
                <div className="text-sm text-green-800">Learning Patterns</div>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                <div className="text-2xl font-bold text-purple-600">{stats.suggestedChanges}</div>
                <div className="text-sm text-purple-800">Active Suggestions</div>
              </div>
              <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                <div className="text-2xl font-bold text-orange-600">
                  {stats.learningPatterns > 0 ? Math.round((stats.totalCorrections / stats.learningPatterns) * 100) / 100 : 0}
                </div>
                <div className="text-sm text-orange-800">Avg Corrections/Pattern</div>
              </div>
            </div>

            {/* Learning Status */}
            <div className="bg-gray-50 p-6 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">🤖 AI Learning Status</h3>
              {stats.totalCorrections === 0 ? (
                <div className="text-center py-8">
                  <div className="text-4xl mb-2">🌱</div>
                  <p className="text-gray-600">
                    AI learning hasn't started yet. Edit some transaction categories to teach the AI your preferences!
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Learning Progress</span>
                    <span className="text-sm font-medium text-gray-900">
                      {stats.totalCorrections} corrections made
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${Math.min((stats.totalCorrections / 20) * 100, 100)}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-500">
                    {stats.totalCorrections < 20 
                      ? `${20 - stats.totalCorrections} more corrections needed for optimal learning`
                      : 'AI has sufficient data for reliable suggestions!'
                    }
                  </p>
                </div>
              )}
            </div>

            {/* Top Patterns Preview */}
            {stats.topPatterns.length > 0 && (
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <h3 className="text-lg font-semibold mb-3">🏆 Top Learning Patterns</h3>
                <div className="space-y-2">
                  {stats.topPatterns.slice(0, 5).map((pattern, index) => (
                    <div key={index} className="flex justify-between items-center py-2 border-b border-gray-100 last:border-b-0">
                      <div className="flex-1">
                        <span className="text-sm font-medium">{pattern.pattern}</span>
                        <span className="mx-2">→</span>
                        <span className="text-sm text-blue-600">{pattern.category}</span>
                      </div>
                      <div className="text-right">
                        <div className="text-xs text-gray-500">
                          Confidence: {pattern.confidence.toFixed(1)}
                        </div>
                        <div className="text-xs text-gray-400">
                          {pattern.examples} examples
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Patterns Tab */}
        {activeTab === 'patterns' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">🔍 All Learning Patterns</h3>
              <button
                onClick={() => {
                  aiLearningService.resetLearning()
                  setStats(aiLearningService.getLearningStats())
                }}
                className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200"
              >
                Reset Learning
              </button>
            </div>

            {stats.topPatterns.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-4xl mb-4">🤔</div>
                <p className="text-gray-600">No learning patterns yet. Start editing transactions to build AI knowledge!</p>
              </div>
            ) : (
              <div className="grid gap-3">
                {stats.topPatterns.map((pattern, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex-1">
                        <div className="font-medium text-gray-900">{pattern.pattern}</div>
                        <div className="text-sm text-gray-600">
                          Learned Category: <span className="font-medium text-blue-600">{pattern.category}</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-gray-900">
                          Confidence: {pattern.confidence.toFixed(1)}
                        </div>
                        <div className="text-xs text-gray-500">
                          {pattern.examples} example{pattern.examples !== 1 ? 's' : ''}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full"
                          style={{ width: `${Math.min((pattern.confidence / 5) * 100, 100)}%` }}
                        ></div>
                      </div>
                      <span className="ml-2 text-xs text-gray-400">
                        Strength
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Corrections Tab */}
        {activeTab === 'corrections' && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">✏️ Recent Manual Corrections</h3>
            
            {stats.recentCorrections.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-4xl mb-4">📝</div>
                <p className="text-gray-600">No manual corrections yet. Edit transaction categories to see them here!</p>
              </div>
            ) : (
              <div className="space-y-3">
                {stats.recentCorrections.map((correction, index) => (
                  <div key={correction.id} className="border border-gray-200 rounded-lg p-4 bg-white">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex-1">
                        <div className="font-medium text-gray-900">{correction.description}</div>
                        <div className="text-sm text-gray-600">
                          ${Math.abs(correction.amount)} • {new Date(correction.timestamp).toLocaleString()}
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="inline-block px-2 py-1 text-xs bg-red-100 text-red-700 rounded">
                          {correction.oldCategory}
                        </span>
                        <span className="mx-2">→</span>
                        <span className="inline-block px-2 py-1 text-xs bg-green-100 text-green-700 rounded">
                          {correction.newCategory}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="flex justify-between items-center pt-6 border-t border-gray-200">
          <div className="text-sm text-gray-500">
            💡 AI learning is stored in memory and resets when you refresh the page
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

export default AILearningDashboard 