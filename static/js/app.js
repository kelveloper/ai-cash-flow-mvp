// Chart initialization
let forecastChart = null;

// DOM Elements
const forecastPeriodSelect = document.getElementById('forecastPeriod');
const refreshBtn = document.getElementById('refreshBtn');
const insightsContainer = document.getElementById('insightsContainer');
const transactionDetails = document.getElementById('transactionDetails');

// Initialize the dashboard
async function initDashboard() {
    await fetchForecast();
    await fetchInsights();
    setupEventListeners();
}

// Fetch forecast data
async function fetchForecast() {
    try {
        const response = await fetch('/api/forecast');
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
            datasets: [{
                label: 'Projected Cash Flow',
                data: data.values || [],
                borderColor: '#3498db',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Cash Flow Forecast'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
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
}

// Initialize the dashboard when the page loads
document.addEventListener('DOMContentLoaded', initDashboard); 