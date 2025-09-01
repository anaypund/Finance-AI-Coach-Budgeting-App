// FinanceAI - Main JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            if (href && href !== '#') {
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Number formatting for currency inputs
    const currencyInputs = document.querySelectorAll('input[type="number"][step="0.01"]');
    currencyInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value) {
                const value = parseFloat(this.value);
                if (!isNaN(value)) {
                    this.setAttribute('data-original-value', this.value);
                }
            }
        });

        input.addEventListener('focus', function() {
            const originalValue = this.getAttribute('data-original-value');
            if (originalValue) {
                this.value = originalValue;
            }
        });
    });

    // Auto-save draft functionality for forms
    const draftForms = document.querySelectorAll('.auto-save');
    draftForms.forEach(form => {
        const formId = form.getAttribute('id') || 'default-form';
        
        // Load saved draft
        loadDraft(form, formId);
        
        // Save draft on input change
        form.addEventListener('input', debounce(function() {
            saveDraft(form, formId);
        }, 1000));
    });

    // Loading state management
    const loadingButtons = document.querySelectorAll('.btn-loading');
    loadingButtons.forEach(button => {
        button.addEventListener('click', function() {
            showButtonLoading(this);
        });
    });

    // Chart.js global defaults
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = 'inherit';
        Chart.defaults.color = getComputedStyle(document.documentElement).getPropertyValue('--bs-body-color');
        Chart.defaults.plugins.legend.labels.usePointStyle = true;
        Chart.defaults.plugins.legend.labels.padding = 20;
    }

    // Animate numbers on scroll
    const animatedNumbers = document.querySelectorAll('.animate-number');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateNumber(entry.target);
                observer.unobserve(entry.target);
            }
        });
    });

    animatedNumbers.forEach(element => {
        observer.observe(element);
    });

    // Goal progress animation
    const progressBars = document.querySelectorAll('.progress-bar');
    const progressObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateProgressBar(entry.target);
                progressObserver.unobserve(entry.target);
            }
        });
    });

    progressBars.forEach(bar => {
        progressObserver.observe(bar);
    });
});

// Utility Functions

// Debounce function for performance optimization
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Format currency for display
function formatCurrency(amount, currency = '₹') {
    if (amount >= 10000000) {
        return `${currency}${(amount / 10000000).toFixed(1)}Cr`;
    } else if (amount >= 100000) {
        return `${currency}${(amount / 100000).toFixed(1)}L`;
    } else if (amount >= 1000) {
        return `${currency}${(amount / 1000).toFixed(1)}K`;
    } else {
        return `${currency}${amount.toLocaleString('en-IN')}`;
    }
}

// Animate numbers counting up
function animateNumber(element) {
    const target = parseFloat(element.getAttribute('data-target') || element.textContent.replace(/[^0-9.-]+/g, ''));
    const duration = 2000; // 2 seconds
    const start = 0;
    const increment = target / (duration / 16); // 60 FPS
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        
        // Update the element's text with currency formatting if needed
        if (element.classList.contains('currency')) {
            element.textContent = formatCurrency(current);
        } else {
            element.textContent = Math.floor(current).toLocaleString('en-IN');
        }
    }, 16);
}

// Animate progress bars
function animateProgressBar(progressBar) {
    const targetWidth = progressBar.style.width || progressBar.getAttribute('data-width');
    progressBar.style.width = '0%';
    progressBar.style.transition = 'width 1.5s ease-in-out';
    
    setTimeout(() => {
        progressBar.style.width = targetWidth;
    }, 100);
}

// Show loading state on buttons
function showButtonLoading(button) {
    const originalText = button.innerHTML;
    button.setAttribute('data-original-text', originalText);
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Loading...';
    button.disabled = true;
}

// Hide loading state on buttons
function hideButtonLoading(button) {
    const originalText = button.getAttribute('data-original-text');
    if (originalText) {
        button.innerHTML = originalText;
        button.removeAttribute('data-original-text');
    }
    button.disabled = false;
}

// Save form draft to localStorage
function saveDraft(form, formId) {
    const formData = new FormData(form);
    const draftData = {};
    
    for (let [key, value] of formData.entries()) {
        draftData[key] = value;
    }
    
    localStorage.setItem(`draft_${formId}`, JSON.stringify(draftData));
}

// Load form draft from localStorage
function loadDraft(form, formId) {
    const draftData = localStorage.getItem(`draft_${formId}`);
    if (draftData) {
        try {
            const data = JSON.parse(draftData);
            Object.keys(data).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input && input.type !== 'password') {
                    input.value = data[key];
                }
            });
        } catch (e) {
            console.warn('Failed to load draft data:', e);
        }
    }
}

// Clear form draft
function clearDraft(formId) {
    localStorage.removeItem(`draft_${formId}`);
}

// Financial calculation utilities
const FinanceUtils = {
    // Calculate EMI
    calculateEMI: function(principal, rate, tenure) {
        const monthlyRate = rate / (12 * 100);
        const emi = (principal * monthlyRate * Math.pow(1 + monthlyRate, tenure)) / 
                   (Math.pow(1 + monthlyRate, tenure) - 1);
        return Math.round(emi);
    },

    // Calculate compound interest
    calculateCompoundInterest: function(principal, rate, time, compoundingFrequency = 12) {
        const amount = principal * Math.pow(1 + (rate / (100 * compoundingFrequency)), compoundingFrequency * time);
        return Math.round(amount - principal);
    },

    // Calculate SIP returns
    calculateSIPReturns: function(monthlyAmount, rate, years) {
        const monthlyRate = rate / (12 * 100);
        const months = years * 12;
        const futureValue = monthlyAmount * (Math.pow(1 + monthlyRate, months) - 1) / monthlyRate * (1 + monthlyRate);
        return Math.round(futureValue);
    },

    // Calculate retirement corpus needed
    calculateRetirementCorpus: function(currentAge, retirementAge, monthlyExpenses, inflationRate = 6, returnRate = 12) {
        const yearsToRetirement = retirementAge - currentAge;
        const retirementYears = 25; // Assume 25 years post retirement
        
        // Future value of current expenses
        const futureMonthlyExpenses = monthlyExpenses * Math.pow(1 + inflationRate / 100, yearsToRetirement);
        
        // Corpus needed (considering inflation during retirement)
        const corpusNeeded = futureMonthlyExpenses * 12 * retirementYears * 
                            Math.pow(1 + inflationRate / 100, retirementYears / 2);
        
        return Math.round(corpusNeeded);
    }
};

// Export utilities to global scope
window.FinanceUtils = FinanceUtils;
window.formatCurrency = formatCurrency;
window.showButtonLoading = showButtonLoading;
window.hideButtonLoading = hideButtonLoading;

// Chat functionality
const ChatUtils = {
    scrollToBottom: function(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    },

    addMessage: function(containerId, message, isUser = false) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `d-flex ${isUser ? 'justify-content-end' : 'justify-content-start'} mb-3`;
        
        const messageContent = `
            ${!isUser ? '<div class="me-2"><div class="bg-success rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;"><i class="fas fa-robot text-white"></i></div></div>' : ''}
            <div class="card ${isUser ? 'bg-primary text-white' : 'bg-light'}" style="max-width: 75%;">
                <div class="card-body p-3">
                    <p class="mb-1">${message}</p>
                    <small class="${isUser ? 'opacity-75' : 'text-muted'}">
                        <i class="fas fa-clock me-1"></i>${new Date().toLocaleTimeString('en-IN', {hour: '2-digit', minute: '2-digit'})}
                    </small>
                </div>
            </div>
            ${isUser ? '<div class="ms-2"><div class="bg-primary rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;"><i class="fas fa-user text-white"></i></div></div>' : ''}
        `;
        
        messageDiv.innerHTML = messageContent;
        container.appendChild(messageDiv);
        
        // Animate in
        messageDiv.classList.add('fade-in');
        
        // Scroll to bottom
        this.scrollToBottom(containerId);
    }
};

window.ChatUtils = ChatUtils;

// Goal management utilities
const GoalUtils = {
    calculateProgress: function(current, target) {
        return target > 0 ? Math.min((current / target) * 100, 100) : 0;
    },

    getProgressColor: function(progress) {
        if (progress >= 100) return 'success';
        if (progress >= 75) return 'primary';
        if (progress >= 50) return 'info';
        if (progress >= 25) return 'warning';
        return 'danger';
    },

    calculateMonthlySavings: function(targetAmount, currentAmount, targetDate) {
        const today = new Date();
        const target = new Date(targetDate);
        const monthsRemaining = (target.getFullYear() - today.getFullYear()) * 12 + 
                               (target.getMonth() - today.getMonth());
        
        if (monthsRemaining <= 0) return targetAmount - currentAmount;
        
        return Math.max((targetAmount - currentAmount) / monthsRemaining, 0);
    }
};

window.GoalUtils = GoalUtils;

// Portfolio utilities
const PortfolioUtils = {
    calculateAllocation: function(age, riskTolerance) {
        let baseEquity = Math.max(100 - age, 20);
        
        switch(riskTolerance) {
            case 'conservative':
                baseEquity = Math.max(baseEquity - 20, 20);
                break;
            case 'aggressive':
                baseEquity = Math.min(baseEquity + 20, 80);
                break;
            default: // moderate
                break;
        }
        
        const remaining = 100 - baseEquity;
        return {
            equity: baseEquity,
            debt: Math.round(remaining * 0.7),
            gold: Math.round(remaining * 0.3)
        };
    },

    rebalancePortfolio: function(currentAllocation, targetAllocation, tolerance = 5) {
        const suggestions = [];
        
        Object.keys(targetAllocation).forEach(asset => {
            const current = currentAllocation[asset] || 0;
            const target = targetAllocation[asset];
            const difference = Math.abs(current - target);
            
            if (difference > tolerance) {
                suggestions.push({
                    asset: asset,
                    action: current > target ? 'reduce' : 'increase',
                    amount: difference
                });
            }
        });
        
        return suggestions;
    }
};

window.PortfolioUtils = PortfolioUtils;

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    // Could send error to analytics service here
});

// Handle online/offline status
window.addEventListener('online', function() {
    const offlineAlert = document.getElementById('offline-alert');
    if (offlineAlert) {
        offlineAlert.remove();
    }
});

window.addEventListener('offline', function() {
    const alertDiv = document.createElement('div');
    alertDiv.id = 'offline-alert';
    alertDiv.className = 'alert alert-warning alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x';
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        <i class="fas fa-wifi me-2"></i>
        You're currently offline. Some features may not work properly.
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
});

console.log('FinanceAI JavaScript loaded successfully');
