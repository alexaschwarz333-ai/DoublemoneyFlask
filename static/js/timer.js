// DoubleMoney Timer System
// Handles all investment timer functionality

class InvestmentTimer {
    constructor() {
        this.timers = new Map();
        this.updateInterval = null;
        this.init();
    }

    init() {
        this.startTimerUpdates();
        this.setupTimerElements();
    }

    setupTimerElements() {
        // Find all timer elements on the page
        const timerElements = document.querySelectorAll('[data-investment-id]');
        timerElements.forEach(element => {
            const investmentId = element.getAttribute('data-investment-id');
            if (investmentId) {
                this.initInvestmentTimer(investmentId);
            }
        });
    }

    initInvestmentTimer(investmentId) {
        // Store timer reference
        this.timers.set(investmentId, {
            id: investmentId,
            element: document.querySelector(`[data-investment-id="${investmentId}"]`),
            lastUpdate: Date.now(),
            isCompleted: false
        });

        // Initial update
        this.updateInvestmentTimer(investmentId);
    }

    startTimerUpdates() {
        // Update timers every second
        this.updateInterval = setInterval(() => {
            this.updateAllTimers();
        }, 1000);

        // Update immediately when page loads
        this.updateAllTimers();
    }

    stopTimerUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    updateAllTimers() {
        this.timers.forEach((timer, investmentId) => {
            this.updateInvestmentTimer(investmentId);
        });
    }

    updateInvestmentTimer(investmentId) {
        const timer = this.timers.get(investmentId);
        if (!timer || timer.isCompleted) return;

        // Fetch current status from server
        this.fetchInvestmentStatus(investmentId)
            .then(data => {
                this.updateTimerDisplay(investmentId, data);
            })
            .catch(error => {
                console.error(`Error updating timer for investment ${investmentId}:`, error);
            });
    }

    async fetchInvestmentStatus(investmentId) {
        try {
            const response = await fetch(`/api/investment_status/${investmentId}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            // Fallback: calculate time client-side if API fails
            console.warn('API call failed, using client-side calculation');
            return this.calculateClientSideTime(investmentId);
        }
    }

    calculateClientSideTime(investmentId) {
        // This is a fallback method - in production, time should come from server
        const timer = this.timers.get(investmentId);
        if (!timer.startTime || !timer.duration) {
            return { time_remaining: null, is_completed: false };
        }

        const now = Date.now();
        const elapsed = now - timer.startTime;
        const remaining = Math.max(0, timer.duration - elapsed);

        if (remaining === 0) {
            return { time_remaining: null, is_completed: true };
        }

        return {
            time_remaining: this.millisecondsToTimeObject(remaining),
            is_completed: false
        };
    }

    updateTimerDisplay(investmentId, data) {
        const timer = this.timers.get(investmentId);
        if (!timer || !timer.element) return;

        const timerDisplay = timer.element.querySelector('.timer-display');
        if (!timerDisplay) return;

        if (data.is_completed) {
            this.displayCompletedState(timer.element, data);
            timer.isCompleted = true;
        } else if (data.time_remaining) {
            this.displayRemainingTime(timer.element, data.time_remaining);
            this.updateProgressBar(timer.element, data.time_remaining);
        } else {
            this.displayPendingState(timer.element);
        }
    }

    displayRemainingTime(element, timeRemaining) {
        const days = timeRemaining.days || 0;
        const hours = timeRemaining.hours || 0;
        const minutes = timeRemaining.minutes || 0;
        const seconds = timeRemaining.seconds || 0;

        // Update individual time units
        this.updateTimeUnit(element, 'days', days);
        this.updateTimeUnit(element, 'hours', hours);
        this.updateTimeUnit(element, 'minutes', minutes);
        this.updateTimeUnit(element, 'seconds', seconds);

        // Update compact display if exists
        const compactDisplay = element.querySelector('.timer-remaining');
        if (compactDisplay) {
            if (days > 0) {
                compactDisplay.textContent = `${days}d ${hours}h ${minutes}m`;
            } else if (hours > 0) {
                compactDisplay.textContent = `${hours}h ${minutes}m ${seconds}s`;
            } else {
                compactDisplay.textContent = `${minutes}m ${seconds}s`;
            }
        }
    }

    updateTimeUnit(element, unit, value) {
        const unitElement = element.querySelector(`[data-unit="${unit}"]`);
        if (unitElement) {
            unitElement.textContent = String(value).padStart(2, '0');
            
            // Add animation class for visual feedback
            if (unit === 'seconds' && value % 5 === 0) {
                unitElement.parentElement.classList.add('pulse');
                setTimeout(() => {
                    unitElement.parentElement.classList.remove('pulse');
                }, 500);
            }
        }
    }

    updateProgressBar(element, timeRemaining) {
        const progressBar = element.querySelector('.timer-progress');
        if (!progressBar) return;

        // Calculate progress percentage (assuming 7 days total)
        const totalTime = 7 * 24 * 60 * 60; // 7 days in seconds
        const remainingTime = 
            (timeRemaining.days || 0) * 24 * 60 * 60 +
            (timeRemaining.hours || 0) * 60 * 60 +
            (timeRemaining.minutes || 0) * 60 +
            (timeRemaining.seconds || 0);

        const progress = Math.max(0, Math.min(100, ((totalTime - remainingTime) / totalTime) * 100));
        
        progressBar.style.width = `${progress}%`;
        progressBar.setAttribute('aria-valuenow', progress);

        // Change color based on progress
        progressBar.className = progressBar.className.replace(/bg-\w+/, '');
        if (progress < 30) {
            progressBar.classList.add('bg-info');
        } else if (progress < 70) {
            progressBar.classList.add('bg-warning');
        } else {
            progressBar.classList.add('bg-success');
        }
    }

    displayCompletedState(element, data) {
        const timerDisplay = element.querySelector('.timer-display');
        if (timerDisplay) {
            timerDisplay.innerHTML = `
                <div class="text-center">
                    <div class="text-success mb-2">
                        <i class="fas fa-check-circle fa-2x"></i>
                    </div>
                    <h6 class="text-success mb-1">Investment Completed!</h6>
                    ${data.final_amount ? `<div class="fw-bold">Final Amount: $${data.final_amount.toFixed(2)}</div>` : ''}
                </div>
            `;
        }

        // Update progress bar to 100%
        const progressBar = element.querySelector('.timer-progress');
        if (progressBar) {
            progressBar.style.width = '100%';
            progressBar.className = progressBar.className.replace(/bg-\w+/, 'bg-success');
        }

        // Add celebration animation
        element.classList.add('success-glow');
        
        // Show completion notification
        if (typeof showNotification === 'function') {
            showNotification('Investment completed! Check your wallet for the doubled amount.', 'success');
        }
    }

    displayPendingState(element) {
        const timerDisplay = element.querySelector('.timer-display');
        if (timerDisplay) {
            timerDisplay.innerHTML = `
                <div class="text-center">
                    <div class="text-warning mb-2">
                        <i class="fas fa-clock fa-2x"></i>
                    </div>
                    <h6 class="text-warning">Waiting for Admin Confirmation</h6>
                    <small class="text-muted">Timer will start after approval</small>
                </div>
            `;
        }
    }

    millisecondsToTimeObject(ms) {
        const totalSeconds = Math.floor(ms / 1000);
        const days = Math.floor(totalSeconds / (24 * 60 * 60));
        const hours = Math.floor((totalSeconds % (24 * 60 * 60)) / (60 * 60));
        const minutes = Math.floor((totalSeconds % (60 * 60)) / 60);
        const seconds = totalSeconds % 60;

        return { days, hours, minutes, seconds };
    }

    // Format time for display
    formatTime(timeObj) {
        const { days, hours, minutes, seconds } = timeObj;
        
        if (days > 0) {
            return `${days}d ${hours}h ${minutes}m`;
        } else if (hours > 0) {
            return `${hours}h ${minutes}m ${seconds}s`;
        } else {
            return `${minutes}m ${seconds}s`;
        }
    }

    // Add a new timer for a newly created investment
    addTimer(investmentId, startTime, duration) {
        this.timers.set(investmentId, {
            id: investmentId,
            element: document.querySelector(`[data-investment-id="${investmentId}"]`),
            startTime: startTime,
            duration: duration,
            lastUpdate: Date.now(),
            isCompleted: false
        });

        this.updateInvestmentTimer(investmentId);
    }

    // Remove a timer
    removeTimer(investmentId) {
        this.timers.delete(investmentId);
    }

    // Clear all timers
    clearAllTimers() {
        this.timers.clear();
        this.stopTimerUpdates();
    }

    // Get timer status
    getTimerStatus(investmentId) {
        return this.timers.get(investmentId);
    }

    // Check if any timers are running
    hasActiveTimers() {
        return Array.from(this.timers.values()).some(timer => !timer.isCompleted);
    }

    // Refresh all timers (useful when returning from background)
    refreshAllTimers() {
        this.timers.forEach((timer, investmentId) => {
            if (!timer.isCompleted) {
                this.updateInvestmentTimer(investmentId);
            }
        });
    }
}

// Global timer instance
let investmentTimer;

// Global functions for compatibility
window.initInvestmentTimer = function(investmentId) {
    if (investmentTimer) {
        investmentTimer.initInvestmentTimer(investmentId);
    }
};

window.updateAllTimers = function() {
    if (investmentTimer) {
        investmentTimer.updateAllTimers();
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    investmentTimer = new InvestmentTimer();
});

// Handle page visibility changes to refresh timers
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible' && investmentTimer) {
        investmentTimer.refreshAllTimers();
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (investmentTimer) {
        investmentTimer.clearAllTimers();
    }
});

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = InvestmentTimer;
}
