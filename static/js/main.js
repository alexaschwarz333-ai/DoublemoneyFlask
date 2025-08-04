// DoubleMoney Main JavaScript
// Core functionality for the investment platform

class DoubleMoney {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeTooltips();
        this.handleFormValidation();
        this.setupLanguageSelector();
        this.initializeAnimations();
    }

    setupEventListeners() {
        // Navigation toggle for mobile
        this.setupMobileNavigation();
        
        // Form submissions
        this.setupFormHandlers();
        
        // Copy functionality
        this.setupCopyButtons();
        
        // Share functionality
        this.setupShareButtons();
        
        // Investment preview (if on deposit page)
        if (document.querySelector('.investment-preview')) {
            this.setupInvestmentPreview();
        }
    }

    setupMobileNavigation() {
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');

        if (navbarToggler && navbarCollapse) {
            navbarToggler.addEventListener('click', () => {
                navbarCollapse.classList.toggle('show');
            });

            // Close mobile menu when clicking outside
            document.addEventListener('click', (e) => {
                if (!navbarToggler.contains(e.target) && !navbarCollapse.contains(e.target)) {
                    navbarCollapse.classList.remove('show');
                }
            });
        }
    }

    setupFormHandlers() {
        // Registration form
        const registerForm = document.querySelector('form[action*="register"]');
        if (registerForm) {
            this.handleRegistrationForm(registerForm);
        }

        // Login form
        const loginForm = document.querySelector('form[action*="login"]');
        if (loginForm) {
            this.handleLoginForm(loginForm);
        }

        // Deposit form
        const depositForm = document.querySelector('form[action*="deposit"]');
        if (depositForm) {
            this.handleDepositForm(depositForm);
        }
    }

    handleRegistrationForm(form) {
        const phoneInput = form.querySelector('input[name="phone"]');
        const passwordInput = form.querySelector('input[name="password"]');
        const confirmPasswordInput = form.querySelector('input[name="confirm_password"]');

        // Phone number formatting
        if (phoneInput) {
            phoneInput.addEventListener('input', (e) => {
                // Remove non-numeric characters
                e.target.value = e.target.value.replace(/\D/g, '');
            });
        }

        // Password confirmation validation
        if (confirmPasswordInput) {
            confirmPasswordInput.addEventListener('input', () => {
                this.validatePasswordMatch(passwordInput, confirmPasswordInput);
            });

            passwordInput.addEventListener('input', () => {
                this.validatePasswordMatch(passwordInput, confirmPasswordInput);
            });
        }

        // Form submission
        form.addEventListener('submit', (e) => {
            if (!this.validateRegistrationForm(form)) {
                e.preventDefault();
            }
        });
    }

    handleLoginForm(form) {
        const phoneInput = form.querySelector('input[name="phone"]');
        
        // Phone number formatting
        if (phoneInput) {
            phoneInput.addEventListener('input', (e) => {
                // Allow + at the beginning for international format
                let value = e.target.value;
                if (value.startsWith('+')) {
                    value = '+' + value.slice(1).replace(/\D/g, '');
                } else {
                    value = value.replace(/\D/g, '');
                }
                e.target.value = value;
            });
        }
    }

    handleDepositForm(form) {
        const amountInput = form.querySelector('input[name="amount"]');
        const currencyInputs = form.querySelectorAll('input[name="currency"]');
        const preview = form.querySelector('.investment-preview');

        // Amount input validation and formatting
        if (amountInput) {
            amountInput.addEventListener('input', (e) => {
                this.updateInvestmentPreview(e.target.value, preview);
                this.validateAmount(e.target);
            });
        }

        // Currency selection handling
        currencyInputs.forEach(input => {
            input.addEventListener('change', () => {
                this.updateCurrencySelection(input);
            });
        });
    }

    validatePasswordMatch(passwordInput, confirmPasswordInput) {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        if (confirmPassword && password !== confirmPassword) {
            confirmPasswordInput.setCustomValidity('Passwords do not match');
            confirmPasswordInput.classList.add('is-invalid');
        } else {
            confirmPasswordInput.setCustomValidity('');
            confirmPasswordInput.classList.remove('is-invalid');
            if (confirmPassword) {
                confirmPasswordInput.classList.add('is-valid');
            }
        }
    }

    validateRegistrationForm(form) {
        const phone = form.querySelector('input[name="phone"]').value;
        const password = form.querySelector('input[name="password"]').value;
        const confirmPassword = form.querySelector('input[name="confirm_password"]').value;

        // Basic validation
        if (phone.length < 8) {
            this.showNotification('Phone number is too short', 'error');
            return false;
        }

        if (password.length < 6) {
            this.showNotification('Password must be at least 6 characters', 'error');
            return false;
        }

        if (password !== confirmPassword) {
            this.showNotification('Passwords do not match', 'error');
            return false;
        }

        return true;
    }

    validateAmount(input) {
        const value = parseFloat(input.value);
        const min = 100;
        const max = 100000;

        input.classList.remove('is-valid', 'is-invalid');

        if (value < min || value > max) {
            input.classList.add('is-invalid');
            input.setCustomValidity(`Amount must be between $${min} and $${max.toLocaleString()}`);
        } else if (value >= min) {
            input.classList.add('is-valid');
            input.setCustomValidity('');
        }
    }

    updateInvestmentPreview(amount, preview) {
        if (!preview) return;

        const value = parseFloat(amount);
        
        if (value >= 100) {
            const investmentAmount = preview.querySelector('.investment-amount');
            const finalAmount = preview.querySelector('.final-amount');
            
            if (investmentAmount && finalAmount) {
                investmentAmount.textContent = `$${value.toFixed(2)}`;
                finalAmount.textContent = `$${(value * 2).toFixed(2)}`;
                preview.style.display = 'block';
                preview.classList.add('show');
            }
        } else {
            preview.style.display = 'none';
            preview.classList.remove('show');
        }
    }

    updateCurrencySelection(selectedInput) {
        const currencyOptions = document.querySelectorAll('.currency-option');
        
        currencyOptions.forEach(option => {
            option.classList.remove('selected');
        });

        const selectedOption = selectedInput.closest('.currency-option');
        if (selectedOption) {
            selectedOption.classList.add('selected');
        }
    }

    setupCopyButtons() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('[onclick*="copyReferralCode"]') || 
                e.target.closest('[onclick*="copyReferralCode"]')) {
                e.preventDefault();
                
                // Extract the referral code from the onclick attribute
                const button = e.target.closest('[onclick*="copyReferralCode"]') || e.target;
                const onclickValue = button.getAttribute('onclick');
                const match = onclickValue.match(/copyReferralCode\(['"]([^'"]+)['"]\)/);
                
                if (match) {
                    this.copyToClipboard(match[1]);
                }
            }
        });
    }

    setupShareButtons() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('[onclick*="shareReferralLink"]') || 
                e.target.closest('[onclick*="shareReferralLink"]')) {
                e.preventDefault();
                
                const button = e.target.closest('[onclick*="shareReferralLink"]') || e.target;
                const onclickValue = button.getAttribute('onclick');
                const match = onclickValue.match(/shareReferralLink\(['"]([^'"]+)['"]\)/);
                
                if (match) {
                    this.shareReferralLink(match[1]);
                }
            }
        });
    }

    copyToClipboard(text) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(() => {
                this.showNotification('Copied to clipboard!', 'success');
            }).catch(err => {
                this.fallbackCopyToClipboard(text);
            });
        } else {
            this.fallbackCopyToClipboard(text);
        }
    }

    fallbackCopyToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            this.showNotification('Copied to clipboard!', 'success');
        } catch (err) {
            this.showNotification('Failed to copy', 'error');
        }
        
        document.body.removeChild(textArea);
    }

    shareReferralLink(link) {
        if (navigator.share) {
            navigator.share({
                title: 'Join DoubleMoney',
                text: 'Double your investment in 7 days!',
                url: link
            }).catch(err => {
                this.copyToClipboard(link);
            });
        } else {
            this.copyToClipboard(link);
        }
    }

    setupLanguageSelector() {
        const languageDropdown = document.getElementById('languageDropdown');
        if (languageDropdown) {
            // Store the current page URL for language switching
            const currentUrl = window.location.pathname + window.location.search;
            localStorage.setItem('returnUrl', currentUrl);
        }
    }

    initializeTooltips() {
        // Initialize Bootstrap tooltips if available
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    }

    initializeAnimations() {
        // Animate elements on scroll
        this.setupScrollAnimations();
        
        // Animate stats counters
        this.animateCounters();
        
        // Animate progress bars
        this.animateProgressBars();
    }

    setupScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, observerOptions);

        // Observe feature cards and step icons
        document.querySelectorAll('.feature-card, .step-icon, .investment-card').forEach(el => {
            observer.observe(el);
        });
    }

    animateCounters() {
        const counters = document.querySelectorAll('[data-count]');
        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-count'));
            const duration = 2000; // 2 seconds
            let start = 0;
            const increment = target / (duration / 16); // 60fps

            const updateCounter = () => {
                start += increment;
                if (start < target) {
                    counter.textContent = Math.floor(start);
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.textContent = target;
                }
            };

            // Start animation when element comes into view
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        updateCounter();
                        observer.unobserve(entry.target);
                    }
                });
            });

            observer.observe(counter);
        });
    }

    animateProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const width = bar.style.width || bar.getAttribute('aria-valuenow') + '%';
                        bar.style.width = '0%';
                        setTimeout(() => {
                            bar.style.width = width;
                        }, 100);
                        observer.unobserve(entry.target);
                    }
                });
            });

            observer.observe(bar);
        });
    }

    showNotification(message, type = 'info') {
        // Create notification element
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
                    notification.parentNode.removeChild(notification);
                }, 150);
            }
        }, 5000);

        // Manual close button
        const closeBtn = notification.querySelector('.btn-close');
        closeBtn.addEventListener('click', () => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 150);
        });
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

    handleFormValidation() {
        // Add real-time validation classes
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('blur', () => {
                    if (input.checkValidity()) {
                        input.classList.remove('is-invalid');
                        input.classList.add('is-valid');
                    } else {
                        input.classList.remove('is-valid');
                        input.classList.add('is-invalid');
                    }
                });

                input.addEventListener('input', () => {
                    if (input.classList.contains('is-invalid') && input.checkValidity()) {
                        input.classList.remove('is-invalid');
                        input.classList.add('is-valid');
                    }
                });
            });
        });
    }

    // Utility function to format currency
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2
        }).format(amount);
    }

    // Utility function to format phone numbers
    formatPhoneNumber(phone, countryCode) {
        if (phone.startsWith('+')) {
            return phone;
        }
        return `${countryCode}${phone}`;
    }

    setupInvestmentPreview() {
        const amountInput = document.querySelector('#amount');
        const preview = document.querySelector('.investment-preview');
        
        if (amountInput && preview) {
            amountInput.addEventListener('input', () => {
                this.updateInvestmentPreview(amountInput.value, preview);
            });
        }
    }
}

// Global functions for backward compatibility
window.copyReferralCode = function(code) {
    app.copyToClipboard(code);
};

window.shareReferralLink = function(link) {
    app.shareReferralLink(link);
};

window.showNotification = function(message, type = 'info') {
    app.showNotification(message, type);
};

// Initialize the application
let app;
document.addEventListener('DOMContentLoaded', function() {
    app = new DoubleMoney();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') {
        // Refresh timers when page becomes visible again
        if (typeof updateAllTimers === 'function') {
            updateAllTimers();
        }
    }
});

// Handle online/offline status
window.addEventListener('online', function() {
    showNotification('Connection restored', 'success');
});

window.addEventListener('offline', function() {
    showNotification('Connection lost', 'warning');
});
