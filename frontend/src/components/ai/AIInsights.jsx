import React from 'react';

const AIInsights = ({ transactions }) => {
  // Simple insights based on transaction data
  const insights = [
    {
      title: 'Top Spending Category',
      value: 'Groceries',
      description: 'You spent the most on groceries this month.',
      icon: '🛒',
    },
    {
      title: 'Largest Transaction',
      value: '$1,200.00',
      description: 'Your largest transaction was for rent.',
      icon: '💸',
    },
    {
      title: 'Recurring Subscriptions',
      value: '3',
      description: 'You have 3 active subscriptions.',
      icon: '🔄',
    },
  ];

  return (
    <div className="bg-white rounded-2xl shadow-lg p-8">
      <h3 className="text-2xl font-semibold text-gray-900 mb-6">AI Insights</h3>
      <div className="space-y-6">
        {insights.map((insight, index) => (
          <div key={index} className="flex items-start space-x-4">
            <div className="text-3xl bg-gray-100 p-3 rounded-full">{insight.icon}</div>
            <div>
              <p className="font-semibold text-gray-800">{insight.title}</p>
              <p className="text-xl font-bold text-gray-900">{insight.value}</p>
              <p className="text-sm text-gray-500">{insight.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AIInsights; 