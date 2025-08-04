// DoubleMoney Admin Panel JavaScript
// Handles all admin-specific functionality

class AdminPanel {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeDataTables();
        this.setupModalHandlers();
        this.initializeCharts();
        this.setupRealTimeUpdates();
    }

    setupEventListeners() {
        // Confirmation dialogs for dangerous actions
        this.setupConfirmationDialogs();
        
        // Form submissions
        this.setupFormHandlers();
        
        // Search functionality
        this.setupSearchHandlers();
        
        // Bulk actions
        this.setupBulkActions();
        
        // Quick stats refresh
        this.setupStatsRefresh();
    }

    setupConfirmationDialogs() {
        // Handle confirmation dialogs for delete/dangerous actions
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a[onclick*="confirm"]');
            if (link) {
                e.preventDefault();
                const onclickValue = link.getAttribute('onclick');
                const confirmMatch = onclickValue.match(/confirm\(['"]([^'"]+)['"]\)/);
                
                if (confirmMatch) {
                    const message = confirmMatch[1];
                    if (confirm(message)) {
                        // Remove the onclick and navigate
                        link.removeAttribute('onclick');
                        window.location.href = link.href;
                    }
                }
            }
        });
    }

    setupFormHandlers() {
        // Wallet form validation
        const walletForm = document.querySelector('form[action*="add_wallet"]');
        if (walletForm) {
            this.handleWalletForm(walletForm);
        }

        // Settings form
        const settingsForm = document.querySelector('form[action*="settings"]');
        if (settingsForm) {
            this.handleSettingsForm(settingsForm);
        }

        // Password reset form
        const passwordForms = document.querySelectorAll('form[action*="reset_password"]');
        passwordForms.forEach(form => {
            this.handlePasswordResetForm(form);
        });
    }

    handleWalletForm(form) {
        const currencySelect = form.querySelector('select[name="currency"]');
        const networkSelect = form.querySelector('select[name="network"]');
        const addressInput = form.querySelector('input[name="address"]');

        // Auto-select network based on currency
        if (currencySelect && networkSelect) {
            currencySelect.addEventListener('change', () => {
                const currency = currencySelect.value;
                if (currency === 'USDC') {
                    networkSelect.value = 'ERC20';
                } else if (currency === 'USDT') {
                    networkSelect.value = 'TRC20';
                }
            });
        }

        // Validate wallet address format
        if (addressInput) {
            addressInput.addEventListener('input', () => {
                this.validateWalletAddress(addressInput, networkSelect);
            });
        }

        // Form submission validation
        form.addEventListener('submit', (e) => {
            if (!this.validateWalletForm(form)) {
                e.preventDefault();
            }
        });
    }

    validateWalletAddress(input, networkSelect) {
        const address = input.value.trim();
        const network = networkSelect ? networkSelect.value : '';

        input.classList.remove('is-valid', 'is-invalid');

        if (address.length === 0) return;

        let isValid = false;

        if (network === 'ERC20') {
            // Ethereum address validation (42 chars, starts with 0x)
            isValid = /^0x[a-fA-F0-9]{40}$/.test(address);
        } else if (network === 'TRC20') {
            // Tron address validation (34 chars, starts with T)
            isValid = /^T[1-9A-HJ-NP-Za-km-z]{33}$/.test(address);
        }

        if (isValid) {
            input.classList.add('is-valid');
        } else {
            input.classList.add('is-invalid');
        }

        return isValid;
    }

    validateWalletForm(form) {
        const address = form.querySelector('input[name="address"]').value.trim();
        const currency = form.querySelector('select[name="currency"]').value;
        const network = form.querySelector('select[name="network"]').value;

        if (!address || !currency || !network) {
            this.showNotification('Please fill in all fields', 'error');
            return false;
        }

        const addressInput = form.querySelector('input[name="address"]');
        const networkSelect = form.querySelector('select[name="network"]');
        
        if (!this.validateWalletAddress(addressInput, networkSelect)) {
            this.showNotification('Invalid wallet address format', 'error');
            return false;
        }

        return true;
    }

    handleSettingsForm(form) {
        // Validate URL formats
        const urlInputs = form.querySelectorAll('input[type="url"]');
        urlInputs.forEach(input => {
            input.addEventListener('input', () => {
                this.validateUrl(input);
            });
        });
    }

    validateUrl(input) {
        const url = input.value.trim();
        
        input.classList.remove('is-valid', 'is-invalid');
        
        if (url === '') {
            return true; // Empty is allowed
        }

        try {
            new URL(url);
            input.classList.add('is-valid');
            return true;
        } catch (e) {
            input.classList.add('is-invalid');
            return false;
        }
    }

    handlePasswordResetForm(form) {
        const passwordInput = form.querySelector('input[name="new_password"]');
        
        if (passwordInput) {
            passwordInput.addEventListener('input', () => {
                this.validatePassword(passwordInput);
            });
        }
    }

    validatePassword(input) {
        const password = input.value;
        
        input.classList.remove('is-valid', 'is-invalid');
        
        if (password.length >= 6) {
            input.classList.add('is-valid');
            return true;
        } else if (password.length > 0) {
            input.classList.add('is-invalid');
            return false;
        }
        
        return false;
    }

    setupSearchHandlers() {
        // Live search functionality
        const searchInputs = document.querySelectorAll('input[type="search"]');
        searchInputs.forEach(input => {
            let searchTimeout;
            
            input.addEventListener('input', () => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.performSearch(input);
                }, 500);
            });
        });
    }

    performSearch(input) {
        const form = input.closest('form');
        if (form && form.method.toLowerCase() === 'get') {
            form.submit();
        }
    }

    setupBulkActions() {
        // Checkbox selection for bulk actions
        const selectAllCheckbox = document.querySelector('input[type="checkbox"][data-select-all]');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                const checkboxes = document.querySelectorAll('input[type="checkbox"][data-item-id]');
                checkboxes.forEach(checkbox => {
                    checkbox.checked = e.target.checked;
                });
                this.updateBulkActionButtons();
            });
        }

        // Individual checkboxes
        const itemCheckboxes = document.querySelectorAll('input[type="checkbox"][data-item-id]');
        itemCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateBulkActionButtons();
            });
        });
    }

    updateBulkActionButtons() {
        const selectedItems = document.querySelectorAll('input[type="checkbox"][data-item-id]:checked');
        const bulkActionButtons = document.querySelectorAll('[data-bulk-action]');
        
        const hasSelection = selectedItems.length > 0;
        
        bulkActionButtons.forEach(button => {
            button.disabled = !hasSelection;
            if (hasSelection) {
                button.textContent = button.textContent.replace(/\(\d+\)/, `(${selectedItems.length})`);
            }
        });
    }

    setupStatsRefresh() {
        // Auto-refresh stats every 30 seconds
        setInterval(() => {
            this.refreshStats();
        }, 30000);

        // Manual refresh button
        const refreshButton = document.querySelector('[data-action="refresh-stats"]');
        if (refreshButton) {
            refreshButton.addEventListener('click', () => {
                this.refreshStats();
            });
        }
    }

    refreshStats() {
        // Update statistics without full page reload
        const statsCards = document.querySelectorAll('.admin-stats-card');
        statsCards.forEach(card => {
            card.style.opacity = '0.7';
        });

        // In a real implementation, this would fetch new stats via AJAX
        // For now, we'll just simulate a refresh
        setTimeout(() => {
            statsCards.forEach(card => {
                card.style.opacity = '1';
            });
            this.showNotification('Statistics updated', 'info');
        }, 1000);
    }

    initializeDataTables() {
        // Add sorting functionality to tables
        const tables = document.querySelectorAll('table');
        tables.forEach(table => {
            this.makeSortable(table);
        });
    }

    makeSortable(table) {
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            if (header.textContent.trim() && !header.querySelector('input')) {
                header.style.cursor = 'pointer';
                header.addEventListener('click', () => {
                    this.sortTable(table, index);
                });
            }
        });
    }

    sortTable(table, columnIndex) {
        const tbody = table.querySelector('tbody');
        if (!tbody) return;

        const rows = Array.from(tbody.querySelectorAll('tr'));
        const isNumeric = this.isColumnNumeric(table, columnIndex);
        const isAscending = !table.getAttribute('data-sort-asc') || table.getAttribute('data-sort-asc') === 'false';

        rows.sort((a, b) => {
            const aValue = this.getCellValue(a, columnIndex);
            const bValue = this.getCellValue(b, columnIndex);

            if (isNumeric) {
                return isAscending ? aValue - bValue : bValue - aValue;
            } else {
                return isAscending ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
            }
        });

        // Update table
        rows.forEach(row => tbody.appendChild(row));
        table.setAttribute('data-sort-asc', !isAscending);

        // Update header indicators
        const headers = table.querySelectorAll('th');
        headers.forEach(h => h.classList.remove('sorted-asc', 'sorted-desc'));
        headers[columnIndex].classList.add(isAscending ? 'sorted-asc' : 'sorted-desc');
    }

    isColumnNumeric(table, columnIndex) {
        const rows = table.querySelectorAll('tbody tr');
        for (let i = 0; i < Math.min(5, rows.length); i++) {
            const value = this.getCellValue(rows[i], columnIndex);
            if (isNaN(value) && isNaN(Date.parse(value))) {
                return false;
            }
        }
        return true;
    }

    getCellValue(row, columnIndex) {
        const cell = row.cells[columnIndex];
        if (!cell) return '';
        
        const text = cell.textContent.trim();
        // Remove currency symbols and commas for numeric comparison
        const cleaned = text.replace(/[$,#%]/g, '');
        const numeric = parseFloat(cleaned);
        
        return isNaN(numeric) ? text : numeric;
    }

    setupModalHandlers() {
        // Generic modal handlers for user details, wallet details, etc.
        document.addEventListener('show.bs.modal', (e) => {
            const modal = e.target;
            const button = e.relatedTarget;
            
            if (button) {
                this.handleModalShow(modal, button);
            }
        });
    }

    handleModalShow(modal, button) {
        const userId = button.getAttribute('data-user-id');
        const walletId = button.getAttribute('data-wallet-id');
        const userPhone = button.getAttribute('data-user-phone');

        // Handle user details modal
        if (modal.id === 'userDetailsModal' && userId) {
            this.loadUserDetails(modal, userId);
        }

        // Handle wallet details modal
        if (modal.id === 'walletDetailsModal' && walletId) {
            this.loadWalletDetails(modal, walletId);
        }

        // Handle password reset modal
        if (modal.id === 'resetPasswordModal' && userId) {
            const form = modal.querySelector('form');
            const phoneDisplay = modal.querySelector('#resetUserPhone');
            
            if (form) {
                form.action = `/admin/user/${userId}/reset_password`;
            }
            if (phoneDisplay && userPhone) {
                phoneDisplay.textContent = userPhone;
            }
        }
    }

    loadUserDetails(modal, userId) {
        const content = modal.querySelector('#userDetailsContent');
        if (!content) return;

        content.innerHTML = `
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;

        // In a real implementation, this would fetch user details via AJAX
        setTimeout(() => {
            content.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <h6>Basic Information</h6>
                        <p><strong>User ID:</strong> ${userId}</p>
                        <p><strong>Status:</strong> <span class="badge bg-success">Active</span></p>
                        <p><strong>Registration:</strong> 2024-01-15</p>
                    </div>
                    <div class="col-md-6">
                        <h6>Investment Summary</h6>
                        <p><strong>Total Invested:</strong> $5,000</p>
                        <p><strong>Active Investments:</strong> 2</p>
                        <p><strong>Completed Investments:</strong> 3</p>
                    </div>
                </div>
                <div class="mt-3">
                    <h6>Referral Information</h6>
                    <p><strong>Referral Code:</strong> <code>REF${userId}</code></p>
                    <p><strong>Total Referrals:</strong> 12</p>
                    <p><strong>Active Referrals:</strong> 8</p>
                </div>
            `;
        }, 500);
    }

    loadWalletDetails(modal, walletId) {
        const content = modal.querySelector('#walletDetailsContent');
        if (!content) return;

        content.innerHTML = `
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;

        // In a real implementation, this would fetch wallet details via AJAX
        setTimeout(() => {
            content.innerHTML = `
                <div class="row">
                    <div class="col-12">
                        <h6>Wallet Information</h6>
                        <p><strong>Wallet ID:</strong> ${walletId}</p>
                        <p><strong>Created:</strong> 2024-01-15 10:30:00</p>
                        <p><strong>Last Used:</strong> 2024-01-20 14:45:00</p>
                        <p><strong>Total Transactions:</strong> 5</p>
                        <p><strong>Total Volume:</strong> $25,000</p>
                    </div>
                </div>
                <div class="mt-3">
                    <h6>Associated Investments</h6>
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Investment ID</th>
                                    <th>Amount</th>
                                    <th>Status</th>
                                    <th>Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>#123</td>
                                    <td>$5,000</td>
                                    <td><span class="badge bg-success">Completed</span></td>
                                    <td>2024-01-20</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }, 500);
    }

    initializeCharts() {
        // Initialize charts if Chart.js is available
        if (typeof Chart !== 'undefined') {
            this.createStatsCharts();
        }
    }

    createStatsCharts() {
        // Example chart creation - investment trend chart
        const chartCanvas = document.getElementById('investmentChart');
        if (chartCanvas) {
            new Chart(chartCanvas, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Investments',
                        data: [12, 19, 3, 5, 2, 3],
                        borderColor: 'var(--bs-primary)',
                        backgroundColor: 'rgba(var(--bs-primary-rgb), 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
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
    }

    setupRealTimeUpdates() {
        // Set up WebSocket or polling for real-time updates
        // For now, we'll use polling every 30 seconds
        setInterval(() => {
            this.checkForUpdates();
        }, 30000);
    }

    checkForUpdates() {
        // Check for new pending investments, referral payouts, etc.
        // This would typically make an AJAX call to get update counts
        
        // Example: Update notification badges
        const pendingBadges = document.querySelectorAll('[data-update="pending-investments"]');
        pendingBadges.forEach(badge => {
            // In real implementation, this would come from server
            const currentCount = parseInt(badge.textContent) || 0;
            // Simulate potential update
            if (Math.random() < 0.1) { // 10% chance of update
                badge.textContent = currentCount + 1;
                badge.classList.add('pulse');
                setTimeout(() => badge.classList.remove('pulse'), 2000);
            }
        });
    }

    // Utility function to show notifications
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 350px;';
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.remove('show');
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 150);
            }
        }, 5000);
    }

    getNotificationIcon(type) {
        switch (type) {
            case 'success': return 'check-circle';
            case 'error': 
            case 'danger': return 'exclamation-triangle';
            case 'warning': return 'exclamation-circle';
            case 'info': 
            default: return 'info-circle';
        }
    }

    // Export data functionality
    exportData(type, format = 'csv') {
        // This would generate and download data exports
        console.log(`Exporting ${type} as ${format}`);
        this.showNotification(`Exporting ${type} data...`, 'info');
    }

    // Backup functionality
    createBackup() {
        this.showNotification('Creating system backup...', 'info');
        
        // Simulate backup process
        setTimeout(() => {
            this.showNotification('Backup created successfully', 'success');
        }, 3000);
    }
}

// Global functions for backward compatibility
window.copyToClipboard = function(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            if (window.adminPanel) {
                adminPanel.showNotification('Copied to clipboard!', 'success');
            }
        }).catch(err => {
            console.error('Could not copy text: ', err);
        });
    }
};

// Initialize admin panel
let adminPanel;
document.addEventListener('DOMContentLoaded', function() {
    adminPanel = new AdminPanel();
});

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdminPanel;
}
