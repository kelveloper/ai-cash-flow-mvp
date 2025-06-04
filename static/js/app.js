// Chart initialization
let forecastChart = null;

// DOM Elements
const forecastPeriodSelect = document.getElementById('forecastPeriod');
const refreshBtn = document.getElementById('refreshBtn');
const insightsContainer = document.getElementById('insightsContainer');
const transactionDetails = document.getElementById('transactionDetails');
const dateRangeStart = document.getElementById('dateRangeStart');
const dateRangeEnd = document.getElementById('dateRangeEnd');
const categoryFilter = document.getElementById('categoryFilter');

// Initialize the dashboard
async function initDashboard() {
    await Promise.all([
        fetchForecast(),
        fetchInsights(),
        fetchTransactionDetails()
    ]);
    setupEventListeners();
    initializeDateRange();
}

// Initialize date range picker with default values
function initializeDateRange() {
    const today = new Date();
    const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate());
    
    dateRangeStart.value = lastMonth.toISOString().split('T')[0];
    dateRangeEnd.value = today.toISOString().split('T')[0];
}

// Fetch forecast data
async function fetchForecast() {
    try {
        const startDate = dateRangeStart.value;
        const endDate = dateRangeEnd.value;
        const category = categoryFilter.value;
        
        const response = await fetch(`/api/forecast?start_date=${startDate}&end_date=${endDate}&category=${category}`);
        const data = await response.json();
        updateForecastChart(data);
    } catch (error) {
        console.error('Error fetching forecast:', error);
        showError('Failed to load forecast data');
    }
}

// Fetch XAI insights
async function fetchInsights() {
    try {
        const response = await fetch('/api/insights');
        const data = await response.json();
        updateInsights(data);
    } catch (error) {
        console.error('Error fetching insights:', error);
        showError('Failed to load insights');
    }
}

// Fetch transaction details
async function fetchTransactionDetails() {
    try {
        const response = await fetch('/api/transactions');
        const data = await response.json();
        updateTransactionDetails(data);
    } catch (error) {
        console.error('Error fetching transaction details:', error);
        showError('Failed to load transaction details');
    }
}

// Update forecast chart
function updateForecastChart(data) {
    const ctx = document.getElementById('forecastChart').getContext('2d');
    
    if (forecastChart) {
        forecastChart.destroy();
    }

    forecastChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels || [],
            datasets: [
                {
                    label: 'Income',
                    data: data.income || [],
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                    yAxisID: 'y',
                    tension: 0.1
                },
                {
                    label: 'Expenses',
                    data: data.expenses || [],
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    yAxisID: 'y',
                    tension: 0.1
                },
                {
                    label: 'Net Cash Flow',
                    data: data.net_cash_flow || [],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    yAxisID: 'y1',
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Cash Flow Forecast'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += new Intl.NumberFormat('en-US', {
                                    style: 'currency',
                                    currency: 'USD'
                                }).format(context.parsed.y);
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Amount ($)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Net Cash Flow ($)'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            }
        }
    });
}

// Update insights display
function updateInsights(data) {
    insightsContainer.innerHTML = data.insights?.map(insight => `
        <div class="insight-card">
            <h3>${insight.title}</h3>
            <p>${insight.description}</p>
        </div>
    `).join('') || 'No insights available';
}

// Update transaction details display
function updateTransactionDetails(data) {
    transactionDetails.innerHTML = `
        <table class="transaction-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Amount</th>
                    <th>Type</th>
                    <th>Category</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
                ${data.map(transaction => `
                    <tr>
                        <td>${transaction.date}</td>
                        <td class="${transaction.type.toLowerCase()}">${transaction.amount}</td>
                        <td>${transaction.type}</td>
                        <td>${transaction.category}</td>
                        <td>${transaction.description}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// Show error message
function showError(message) {
    // TODO: Implement error display
    console.error(message);
}

// Setup event listeners
function setupEventListeners() {
    refreshBtn.addEventListener('click', async () => {
        await fetchForecast();
        await fetchInsights();
    });

    forecastPeriodSelect.addEventListener('change', async () => {
        await fetchForecast();
        await fetchInsights();
    });

    dateRangeStart.addEventListener('change', fetchForecast);
    dateRangeEnd.addEventListener('change', fetchForecast);
    categoryFilter.addEventListener('change', fetchForecast);
}

// Initialize the dashboard when the page loads
document.addEventListener('DOMContentLoaded', initDashboard);

async function switchDataFile(filename) {
    try {
        const response = await fetch(`/api/switch-data/${filename}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`Failed to switch data file: ${response.statusText}`);
        }
        
        // Refresh the dashboard data
        await Promise.all([
            fetchForecast(),
            fetchInsights()
        ]);
        
        // Show success message
        showNotification(`Switched to ${filename}`, 'success');
    } catch (error) {
        console.error('Error switching data file:', error);
        showNotification('Failed to switch data file', 'error');
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Add to document
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Add notification styles
const style = document.createElement('style');
style.textContent = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem;
        border-radius: 4px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    }
    
    .notification.success {
        background-color: #28a745;
    }
    
    .notification.error {
        background-color: #dc3545;
    }
    
    .notification.info {
        background-color: #17a2b8;
    }
    
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style); 