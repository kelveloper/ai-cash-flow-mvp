// Debug logging
console.log('Debug: transactions.js loaded');

// DOM Elements
const transactionsTable = document.getElementById('transactionsTable');
const searchInput = document.getElementById('search');
const dateRangeInput = document.getElementById('date-range');
const categorySelect = document.getElementById('category');
const statusSelect = document.getElementById('status');
const sortHeaders = document.querySelectorAll('th[data-sort]');
const prevMonthBtn = document.getElementById('prevMonth');
const nextMonthBtn = document.getElementById('nextMonth');
const currentMonthLabel = document.getElementById('currentMonthLabel');

// Debug log DOM elements
console.log('Debug: DOM Elements found:', {
    transactionsTable,
    searchInput,
    dateRangeInput,
    categorySelect,
    statusSelect,
    sortHeaders: sortHeaders.length,
    prevMonthBtn,
    nextMonthBtn,
    currentMonthLabel
});

// State
let allTransactions = [];
let currentSort = {
    column: 'date',
    direction: 'desc'
};
let currentMonth = null; // e.g. '2025-06'
let currentFilters = {
    search: '',
    date: '',
    category: '',
    status: ''
};

// Store the currently edited transaction id (or index) and original category
let editingCategory = null;
let originalCategory = null;

let currentLimit = 100;
let currentOffset = 0;
let totalTransactions = 0;

// Utility Functions
function escapeHtml(text) {
    return text.replace(/[&<>'"]/g, char => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        "'": '&#39;',
        '"': '&quot;'
    }[char]));
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

function formatCategory(category) {
    if (!category) return '';
    return category
        .replace(/[_-]/g, ' ')
        .replace(/\b\w/g, c => c.toUpperCase());
}

function getMonthYear(date) {
    const d = new Date(date);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
}

function getMonthLabel(monthYear) {
    // monthYear is in the format 'YYYY-MM'
    const [year, month] = monthYear.split('-');
    const d = new Date(year, parseInt(month) - 1, 1); // JS months are 0-based
    return `${d.toLocaleString('en-US', { month: 'long' })} ${d.getFullYear()}`;
}

function isCurrentMonth(monthYear) {
    const now = new Date();
    const currentMonthYear = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
    return monthYear === currentMonthYear;
}

function updateMonthNavigation() {
    if (!currentMonth) return;
    
    // Hide next month button if we're on current month
    if (nextMonthBtn) {
        if (isCurrentMonth(currentMonth)) {
            nextMonthBtn.style.display = 'none';
            // Adjust current month label position when next button is hidden
            currentMonthLabel.style.marginRight = '100px';
        } else {
            nextMonthBtn.style.display = 'block';
            // Reset current month label position when next button is visible
            currentMonthLabel.style.marginRight = '0';
        }
    }
}

function getAccountTypeFilter() {
    // Determine which account type to filter by based on the page
    if (window.location.pathname.includes('credit-transactions')) {
        return 'Credit Account';
    } else if (window.location.pathname.includes('checking-transactions')) {
        return 'Checking Account';
    }
    return null; // No filter for other pages
}

// Fetch and render a page of transactions (CSV mode)
async function loadTransactions() {
    try {
        const response = await fetch('/api/transactions');
        const data = await response.json();
        if (!data || !data.transactions) {
            throw new Error('Invalid data format received');
        }
        allTransactions = data.transactions;
        console.log('Loaded transactions:', allTransactions.slice(0, 10)); // Show first 10 for brevity
        // Find the most recent month with data
        if (allTransactions.length > 0) {
            // Get all unique months in the data
            const months = Array.from(new Set(allTransactions.map(t => {
                const d = new Date(t.date);
                return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
            })));
            months.sort();
            currentMonth = months[months.length - 1];
            console.log('Set currentMonth to:', currentMonth);
        }
        renderMonthlyTransactions();
    } catch (error) {
        console.error('Error loading transactions:', error);
        document.getElementById('pendingTransactionsTable').innerHTML = `<div class='text-red-600'>Failed to load transactions.</div>`;
        document.getElementById('postedTransactionsTable').innerHTML = '';
    }
}

// Render transactions for a specific month
function renderMonthlyTransactions() {
    if (!currentMonth) return;
    // Get filtered transactions
    const filteredTransactions = filterTransactions();
    
    // Debug logs for current month and dates
    console.log('Month being displayed:', currentMonth);
    console.log('Dates of filtered transactions:', filteredTransactions.map(t => t.date));
    
    // Filter for current month
    const [year, month] = currentMonth.split('-');
    const monthTransactions = filteredTransactions.filter(t => {
        const d = new Date(t.date);
        const isMatch = d.getFullYear() === parseInt(year) && (d.getMonth() + 1) === parseInt(month);
        if (t.description.toLowerCase().includes('rent')) {
            console.log('Checking rent transaction:', t, 'Parsed date:', d, 'isMatch:', isMatch);
        }
        return isMatch;
    });
    if (currentMonth === '2025-06') {
        console.log('All transactions for June 2025:', monthTransactions);
    }
    
    // Show only pending transactions from the last 30 days
    const now = new Date();
    let pending = filteredTransactions.filter(t => {
        if (t.status !== 'pending') return false;
        const d = new Date(t.date);
        return (now - d) / (1000 * 60 * 60 * 24) <= 30;
    });
    
    // Only posted for the current month
    let posted = monthTransactions.filter(t => t.status === 'posted');
    
    // Sort both by date descending
    pending = pending.sort((a, b) => new Date(b.date) - new Date(a.date));
    posted = posted.sort((a, b) => new Date(b.date) - new Date(a.date));
    
    // Render statement label
    const statementLabel = document.getElementById('statementLabel');
    const endOfMonth = new Date(year, month, 0); // last day of month
    statementLabel.textContent = `Statement Ending ${endOfMonth.toLocaleString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}`;
    
    // Update current month label
    if (currentMonthLabel) {
        currentMonthLabel.textContent = getMonthLabel(currentMonth);
    }
    
    // Update month navigation
    updateMonthNavigation();
    
    // Get the table containers
    const pendingTableContainer = document.getElementById('pendingTransactionsTable');
    const postedTableContainer = document.getElementById('postedTransactionsTable');
    // Get the Pending Transactions section wrapper
    const pendingSectionWrapper = pendingTableContainer.closest('.bg-white.rounded-xl.shadow.p-4.mb-4');

    // Show or hide the pending section based on current month
    if (isCurrentMonth(currentMonth)) {
        pendingSectionWrapper.style.display = '';
    } else {
        pendingSectionWrapper.style.display = 'none';
    }

    // Clear existing content
    pendingTableContainer.innerHTML = '';
    postedTableContainer.innerHTML = '';
    
    // Update the table headers for both pending and posted tables
    const tableHeader = `
        <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
        </tr>
    `;
    
    // Update pending transactions table
    if (pending.length > 0 && isCurrentMonth(currentMonth)) {
        const table = document.createElement('table');
        table.className = 'min-w-full divide-y divide-gray-200';
        const thead = document.createElement('thead');
        thead.className = 'bg-gray-50';
        thead.innerHTML = tableHeader;
        table.appendChild(thead);
        const tbody = document.createElement('tbody');
        pending.forEach((t, index) => {
            tbody.appendChild(renderTransaction(t, index));
        });
        table.appendChild(tbody);
        pendingTableContainer.appendChild(table);
    } else {
        pendingTableContainer.innerHTML = `<div class='text-gray-500'>There are no pending transactions.</div>`;
    }
    
    // Update posted transactions table
    if (posted.length > 0) {
        const table = document.createElement('table');
        table.className = 'min-w-full divide-y divide-gray-200';
        const thead = document.createElement('thead');
        thead.className = 'bg-gray-50';
        thead.innerHTML = tableHeader;
        table.appendChild(thead);
        const tbody = document.createElement('tbody');
        posted.forEach((t, index) => {
            tbody.appendChild(renderTransaction(t, index));
        });
        table.appendChild(tbody);
        postedTableContainer.appendChild(table);
    } else {
        postedTableContainer.innerHTML = `<div class='text-gray-500'>There are no posted transactions for this statement.</div>`;
    }
}

// Highlight matching text
function highlightText(text, searchTerm) {
    if (!searchTerm) return escapeHtml(text);
    // Escape HTML special characters in text
    const escapedText = escapeHtml(text);
    // Escape regex special characters in searchTerm
    const escapedSearchTerm = searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(escapedSearchTerm, 'gi');
    // Add inline style for padding, text color, border, and border-radius for visibility
    const result = escapedText.replace(
        regex,
        match => `<span class="bg-yellow-200" style="padding:0 2px;color:#92400e;border:2px solid #fde047;border-radius:4px;">${match}</span>`
    );
    return result;
}

// Helper to get unique categories from allTransactions
function getUniqueCategories() {
    return Array.from(new Set(allTransactions.map(t => t.category).filter(Boolean))).sort();
}

// Render a single transaction
function renderTransaction(transaction, rowIndex) {
    if (transaction.description.toLowerCase().includes('rent')) {
        console.log('Rendering rent-related transaction:', transaction);
    }
    const date = new Date(transaction.date);
    const formattedDate = date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        year: 'numeric'
    });
    
    const amount = parseFloat(transaction.amount);
    const formattedAmount = amount.toLocaleString('en-US', {
        style: 'currency',
        currency: 'USD'
    });
    
    const isNegative = amount < 0;
    const amountClass = isNegative ? 'text-red-600' : 'text-green-600';
    
    // Highlight matching text only in description
    const highlightedDescription = highlightText(transaction.description, currentFilters.search);
    
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-gray-50';
    
    const dateCell = document.createElement('td');
    dateCell.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-500';
    dateCell.textContent = formattedDate;
    
    const descCell = document.createElement('td');
    descCell.className = 'px-6 py-4 whitespace-nowrap';
    
    const descDiv = document.createElement('div');
    descDiv.className = 'text-sm font-medium text-gray-900';
    descDiv.innerHTML = highlightedDescription;
    descCell.appendChild(descDiv);
    
    // Category cell in its own column
    const categoryCell = document.createElement('td');
    categoryCell.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-500';
    
    if (editingCategory && editingCategory.rowIndex === rowIndex) {
        console.log('DEBUG: Rendering Save/Cancel for row', rowIndex, transaction);
        // Show dropdown and Save/Cancel inline
        const wrapper = document.createElement('div');
        wrapper.style.display = 'flex';
        wrapper.style.alignItems = 'center';
        wrapper.style.gap = '0.5rem';
        wrapper.style.overflow = 'visible';
        wrapper.style.minWidth = '180px';
        
        const select = document.createElement('select');
        select.className = 'border rounded px-1 py-0.5 text-sm mr-2';
        getUniqueCategories().forEach(cat => {
            const option = document.createElement('option');
            option.value = cat;
            option.textContent = cat;
            if (cat === transaction.category) option.selected = true;
            select.appendChild(option);
        });
        wrapper.appendChild(select);
        
        const saveBtn = document.createElement('button');
        saveBtn.textContent = 'Save';
        saveBtn.className = 'ml-1 px-2 py-0.5 bg-blue-100 text-blue-900 border border-blue-600 rounded text-xs font-semibold';
        saveBtn.onclick = async (e) => {
            e.stopPropagation();
            if (!transaction.id) {
                alert('Transaction ID not found. Cannot update.');
                return;
            }
            const newCategory = select.value;
            try {
                const response = await fetch(`/api/transactions/${transaction.id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ category: newCategory })
                });
                if (!response.ok) {
                    const error = await response.json();
                    alert('Failed to update category: ' + (error.detail || response.statusText));
                    return;
                }
                transaction.category = newCategory;
                editingCategory = null;
                originalCategory = null;
                renderMonthlyTransactions();
                alert('Category updated successfully!');
            } catch (err) {
                alert('Error updating category: ' + err.message);
            }
        };
        wrapper.appendChild(saveBtn);
        
        const cancelBtn = document.createElement('button');
        cancelBtn.textContent = 'Cancel';
        cancelBtn.className = 'ml-1 px-2 py-0.5 bg-gray-100 text-gray-800 border border-gray-400 rounded text-xs font-semibold';
        cancelBtn.onclick = (e) => {
            e.stopPropagation();
            transaction.category = originalCategory;
            editingCategory = null;
            originalCategory = null;
            renderMonthlyTransactions();
        };
        wrapper.appendChild(cancelBtn);
        
        categoryCell.innerHTML = '';
        categoryCell.appendChild(wrapper);
    } else {
        // Show as text, click to edit
        categoryCell.textContent = transaction.category;
        categoryCell.style.cursor = 'pointer';
        categoryCell.title = 'Click to edit category';
        categoryCell.onclick = (e) => {
            e.stopPropagation();
            console.log('DEBUG: Entering edit mode for row', rowIndex, transaction);
            editingCategory = { rowIndex };
            originalCategory = transaction.category;
            renderMonthlyTransactions();
        };
    }
    
    const amountCell = document.createElement('td');
    amountCell.className = `px-6 py-4 whitespace-nowrap text-sm ${amountClass}`;
    amountCell.textContent = formattedAmount;
    
    const statusCell = document.createElement('td');
    statusCell.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-500';
    statusCell.textContent = transaction.status;
    
    tr.appendChild(dateCell);
    tr.appendChild(descCell);
    tr.appendChild(categoryCell);
    tr.appendChild(amountCell);
    tr.appendChild(statusCell);
    
    return tr;
}

// Filtering
function filterTransactions() {
    const accountType = getAccountTypeFilter();
    const filtered = allTransactions.filter(transaction => {
        const searchTerm = currentFilters.search.toLowerCase();
        const dateFilter = currentFilters.date;
        const categoryFilter = currentFilters.category;
        const statusFilter = currentFilters.status;
        
        const matchesSearch = !searchTerm || 
            transaction.description.toLowerCase().includes(searchTerm);
            
        const matchesDate = !dateFilter || 
            transaction.date.startsWith(dateFilter);
            
        const matchesCategory = !categoryFilter || 
            transaction.category.toLowerCase() === categoryFilter.toLowerCase();
            
        const matchesStatus = !statusFilter || 
            transaction.status === statusFilter;
            
        const matchesAccount = accountType ? transaction.account_type === accountType : true;
        
        return matchesSearch && matchesDate && matchesCategory && matchesStatus && matchesAccount;
    });
    return filtered;
}

// Sorting
function sortTransactions(transactions) {
    return [...transactions].sort((a, b) => {
        let valueA = a[currentSort.column];
        let valueB = b[currentSort.column];
        
        // Handle numeric values
        if (currentSort.column === 'amount') {
            valueA = parseFloat(valueA);
            valueB = parseFloat(valueB);
        }
        
        // Handle date values
        if (currentSort.column === 'date') {
            valueA = new Date(valueA);
            valueB = new Date(valueB);
        }
        
        if (valueA < valueB) {
            return currentSort.direction === 'asc' ? -1 : 1;
        }
        if (valueA > valueB) {
            return currentSort.direction === 'asc' ? 1 : -1;
        }
        return 0;
    });
}

// Render pagination controls
function renderPaginationControls() {
    let controls = document.getElementById('paginationControls');
    if (!controls) {
        controls = document.createElement('div');
        controls.id = 'paginationControls';
        controls.style.margin = '16px 0';
        controls.style.display = 'flex';
        controls.style.justifyContent = 'center';
        controls.style.gap = '1rem';
        document.querySelector('.main-content')?.prepend(controls);
    }
    controls.innerHTML = '';
    const page = Math.floor(currentOffset / currentLimit) + 1;
    const totalPages = Math.ceil(totalTransactions / currentLimit);
    const prevBtn = document.createElement('button');
    prevBtn.textContent = 'Previous';
    prevBtn.disabled = currentOffset === 0;
    prevBtn.onclick = () => loadTransactionsPage(currentLimit, Math.max(0, currentOffset - currentLimit));
    controls.appendChild(prevBtn);
    const pageInfo = document.createElement('span');
    pageInfo.textContent = `Page ${page} of ${totalPages} (Total: ${totalTransactions})`;
    controls.appendChild(pageInfo);
    const nextBtn = document.createElement('button');
    nextBtn.textContent = 'Next';
    nextBtn.disabled = currentOffset + currentLimit >= totalTransactions;
    nextBtn.onclick = () => loadTransactionsPage(currentLimit, currentOffset + currentLimit);
    controls.appendChild(nextBtn);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    console.log('Debug: DOMContentLoaded event fired');
    
    loadTransactions();
    
    // Previous Month Button
    if (prevMonthBtn) {
        prevMonthBtn.addEventListener('click', () => {
            console.log('Debug: Previous month button clicked');
            if (!currentMonth) {
                console.warn('Debug: No current month set');
                return;
            }
            let [year, month] = currentMonth.split('-').map(Number);
            month--;
            if (month === 0) {
                month = 12;
                year--;
            }
            currentMonth = `${year}-${String(month).padStart(2, '0')}`;
            console.log('Debug: New current month:', currentMonth);
            renderMonthlyTransactions();
            updateMonthNavigation();
        });
        console.log('Debug: Previous month button listener added');
    } else {
        console.warn('Debug: Previous month button not found');
    }

    // Next Month Button
    if (nextMonthBtn) {
        nextMonthBtn.addEventListener('click', () => {
            console.log('Debug: Next month button clicked');
            if (!currentMonth) {
                console.warn('Debug: No current month set');
                return;
            }
            let [year, month] = currentMonth.split('-').map(Number);
            month++;
            if (month > 12) {
                month = 1;
                year++;
            }
            currentMonth = `${year}-${String(month).padStart(2, '0')}`;
            console.log('Debug: New current month:', currentMonth);
            renderMonthlyTransactions();
            updateMonthNavigation();
        });
        console.log('Debug: Next month button listener added');
    } else {
        console.warn('Debug: Next month button not found');
    }

    // Update current month label
    if (currentMonthLabel) {
        currentMonthLabel.textContent = currentMonth ? getMonthLabel(currentMonth) : '';
    }

    // Search input - real-time filtering
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            console.log('Debug: Search input changed:', e.target.value);
            currentFilters.search = e.target.value;
            console.log('Debug: Updated currentFilters:', currentFilters);
            renderMonthlyTransactions();
        });
        console.log('Debug: Search input listener added');
    } else {
        console.warn('Debug: Search input not found');
    }
    
    // Date range input
    if (dateRangeInput) {
        dateRangeInput.addEventListener('change', (e) => {
            console.log('Debug: Date range changed:', e.target.value);
            currentFilters.date = e.target.value;
            renderMonthlyTransactions();
        });
        console.log('Debug: Date range input listener added');
    } else {
        console.warn('Debug: Date range input not found');
    }
    
    // Category select
    if (categorySelect) {
        categorySelect.addEventListener('change', (e) => {
            console.log('Debug: Category changed:', e.target.value);
            currentFilters.category = e.target.value;
            renderMonthlyTransactions();
        });
        console.log('Debug: Category select listener added');
    } else {
        console.warn('Debug: Category select not found');
    }
    
    // Status select
    if (statusSelect) {
        statusSelect.addEventListener('change', (e) => {
            console.log('Debug: Status changed:', e.target.value);
            currentFilters.status = e.target.value;
            renderMonthlyTransactions();
        });
        console.log('Debug: Status select listener added');
    } else {
        console.warn('Debug: Status select not found');
    }
    
    // Sort headers
    if (sortHeaders.length > 0) {
    sortHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const column = header.dataset.sort;
            
            if (currentSort.column === column) {
                currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
            } else {
                currentSort.column = column;
                currentSort.direction = 'desc';
            }
            
            renderMonthlyTransactions();
        });
    });
        console.log('Debug: Sort headers listeners added');
    } else {
        console.warn('Debug: No sort headers found');
    }

    // Export Data Button
    const exportBtn = document.getElementById('export-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            // Get filtered transactions for the current month (as shown on the page)
            const filteredTransactions = filterTransactions();
            if (!currentMonth) return;
            const [year, month] = currentMonth.split('-');
            // Only include transactions for the current month
            const monthTransactions = filteredTransactions.filter(t => {
                const d = new Date(t.date);
                return d.getFullYear() === parseInt(year) && (d.getMonth() + 1) === parseInt(month);
            });
            // Include both posted and (if current month) pending
            let exportRows = [];
            if (isCurrentMonth(currentMonth)) {
                // Pending: last 30 days, status 'pending'
                const now = new Date();
                const pending = filteredTransactions.filter(t => {
                    if (t.status !== 'pending') return false;
                    const d = new Date(t.date);
                    return (now - d) / (1000 * 60 * 60 * 24) <= 30;
                });
                exportRows = [...pending, ...monthTransactions.filter(t => t.status === 'posted')];
            } else {
                // Only posted for past months
                exportRows = monthTransactions.filter(t => t.status === 'posted');
            }
            // Convert to CSV
            const csvRows = [];
            // Header
            csvRows.push(['Date', 'Description', 'Amount', 'Category', 'Status'].join(','));
            // Data
            exportRows.forEach(t => {
                csvRows.push([
                    '"' + t.date + '"',
                    '"' + (t.description || '').replace(/"/g, '""') + '"',
                    t.amount,
                    '"' + (t.category || '').replace(/"/g, '""') + '"',
                    '"' + (t.status || '') + '"'
                ].join(','));
            });
            const csvContent = csvRows.join('\n');
            // Download
            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'transactions.csv';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
    }
}); 

function updateMonthDisplay(month) {
    console.log('[DEBUG] Updating month display:', month);
    window.currentMonth = month; // Update the global currentMonth variable
    const monthLabel = document.getElementById('statementLabel');
    if (monthLabel) {
        const [year, monthNum] = month.split('-');
        const date = new Date(year, parseInt(monthNum) - 1, 1);
        monthLabel.textContent = date.toLocaleString('en-US', { month: 'long', year: 'numeric' });
    }
    // Dispatch event for Dex to update
    window.dispatchEvent(new Event('dex-month-changed'));
}

// Update the loadPrevious and loadNext functions to use updateMonthDisplay
function loadPrevious() {
    if (currentMonth) {
        const [year, month] = currentMonth.split('-');
        const date = new Date(year, parseInt(month) - 1, 1);
        date.setMonth(date.getMonth() - 1);
        const newMonth = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
        updateMonthDisplay(newMonth);
        loadTransactions(newMonth);
    }
}

function loadNext() {
    if (currentMonth) {
        const [year, month] = currentMonth.split('-');
        const date = new Date(year, parseInt(month) - 1, 1);
        date.setMonth(date.getMonth() + 1);
        const newMonth = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
        updateMonthDisplay(newMonth);
        loadTransactions(newMonth);
    }
} 