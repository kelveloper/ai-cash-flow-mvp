// DOM Elements
const transactionList = document.getElementById('transactionList');
const loadingSpinner = document.getElementById('loadingSpinner');
const errorMessage = document.getElementById('errorMessage');
const successMessage = document.getElementById('successMessage');
const totalBalance = document.getElementById('totalBalance');
const monthlyIncome = document.getElementById('monthlyIncome');
const monthlyExpenses = document.getElementById('monthlyExpenses');
const savingsRate = document.getElementById('savingsRate');

// Initial balance on Jan 1, 2019 (when Maria started)
const INITIAL_BALANCE = 35000.00;  // Maria's initial investment

// Utility Functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
                                        style: 'currency',
                                        currency: 'USD'
    }).format(amount);
}

function formatDate(dateStr) {
    const date = new Date(dateStr + 'T00:00:00'); // Add time to ensure consistent timezone handling
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function showLoading() {
    loadingSpinner.classList.remove('hidden');
}

function hideLoading() {
    loadingSpinner.classList.add('hidden');
    }

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
    setTimeout(() => {
        errorMessage.classList.add('hidden');
    }, 5000);
}

function showSuccess(message) {
    successMessage.textContent = message;
    successMessage.classList.remove('hidden');
    setTimeout(() => {
        successMessage.classList.add('hidden');
    }, 5000);
}

// Data Loading Functions
let allTransactions = [];
async function loadDashboardData() {
    try {
        showLoading();
        const response = await fetch('/api/transactions');
        const data = await response.json();
        
        if (!data || !data.transactions) {
            throw new Error('Invalid data format received');
        }
        
        allTransactions = data.transactions;
        console.log('Loaded transactions:', allTransactions);

        // Filter for checking account only
        const checkingTransactions = allTransactions.filter(t => t.account_type === 'Checking Account');
        console.log('Checking Account transactions:', checkingTransactions);

        // Sort by date ascending (oldest first)
        checkingTransactions.sort((a, b) => new Date(a.date) - new Date(b.date));

        // Calculate running balance starting from initial balance
        let runningBalance = INITIAL_BALANCE;
        checkingTransactions.forEach(t => {
            if (t.status === 'posted') {
                runningBalance += parseFloat(t.amount);
            }
        });

        totalBalance.textContent = formatCurrency(runningBalance);

        // Sort by date descending for display
        checkingTransactions.sort((a, b) => new Date(b.date) - new Date(a.date));

        // Render recent transactions
        renderRecentTransactions(checkingTransactions);
        hideLoading();
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showError('Failed to load dashboard data');
        totalBalance.textContent = 'No data';
        hideLoading();
    }
}

function renderRecentTransactions(transactions) {
    const recentTransactionsList = document.getElementById('recentTransactions');
    recentTransactionsList.innerHTML = '';

    // Filter for checking account only
    const checkingTransactions = transactions.filter(t => t.account_type === 'Checking Account');

    // Show only the 6 most recent checking account transactions
    const recentTransactions = checkingTransactions.slice(0, 6);

    recentTransactions.forEach(transaction => {
        const li = document.createElement('li');
        li.className = 'py-3';
        li.innerHTML = `
            <div class="flex items-center justify-between">
                <div>
                    <p class="font-medium text-gray-900">${transaction.description}</p>
                    <p class="text-sm text-gray-500">${formatDate(transaction.date)}</p>
                </div>
                <div class="text-right">
                    <p class="font-medium ${transaction.amount < 0 ? 'text-red-600' : 'text-green-600'}">
                        ${formatCurrency(transaction.amount)}
                    </p>
                    <p class="text-sm text-gray-500">${transaction.status}</p>
                </div>
            </div>
        `;
        recentTransactionsList.appendChild(li);
    });
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();
    
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            const filtered = allTransactions.filter(t =>
                t.description.toLowerCase().includes(query) ||
                t.category.toLowerCase().includes(query) ||
                (t.amount + '').toLowerCase().includes(query) ||
                t.status.toLowerCase().includes(query)
            );
            updateTransactionList(filtered);
        });
    }
    
    const dateRangeInput = document.getElementById('date-range');
    if (dateRangeInput) {
        dateRangeInput.addEventListener('input', function() {
            const selectedDate = this.value;
            if (!selectedDate) {
                updateTransactionList(allTransactions);
                return;
        }
            const filtered = allTransactions.filter(t =>
                t.date && t.date.startsWith(selectedDate)
            );
            updateTransactionList(filtered);
        });
    }
    
    const dateFilter = document.getElementById('date-filter');
    if (dateFilter) {
        dateFilter.addEventListener('change', function() {
            renderRecentTransactions(allTransactions);
        });
    }
}); 