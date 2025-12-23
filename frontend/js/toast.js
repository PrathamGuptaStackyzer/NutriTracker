/**
 * NutriTracker.ai - Global Toast Notification System
 * A beautiful, non-intrusive toast notification system
 */

// ============================================
// Toast Container Setup
// ============================================
(function() {
    // Create toast container if it doesn't exist
    if (!document.getElementById('toast-container')) {
        const container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }
})();

// ============================================
// Toast Function
// ============================================
function showToast(message, type = 'info', duration = 4000) {
    const container = document.getElementById('toast-container') || createToastContainer();
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    // Icon based on type
    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ',
        danger: '✕'
    };
    
    // Map danger to error for styling
    const styleType = type === 'danger' ? 'error' : type;
    toast.className = `toast toast-${styleType}`;
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    // Add to container
    container.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Auto remove
    setTimeout(() => {
        toast.classList.remove('show');
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 300);
    }, duration);
    
    return toast;
}

// Helper function to create container
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// ============================================
// Convenience Functions
// ============================================
function toastSuccess(message, duration = 4000) {
    return showToast(message, 'success', duration);
}

function toastError(message, duration = 5000) {
    return showToast(message, 'error', duration);
}

function toastWarning(message, duration = 4000) {
    return showToast(message, 'warning', duration);
}

function toastInfo(message, duration = 4000) {
    return showToast(message, 'info', duration);
}

// ============================================
// Inject Toast Styles
// ============================================
(function injectToastStyles() {
    if (document.getElementById('toast-styles')) return;
    
    const styles = document.createElement('style');
    styles.id = 'toast-styles';
    styles.textContent = `
        #toast-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 99999;
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: 400px;
            pointer-events: none;
        }
        
        .toast {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 20px;
            border-radius: 12px;
            background: #ffffff;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15), 0 2px 10px rgba(0, 0, 0, 0.1);
            transform: translateX(120%);
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            pointer-events: auto;
            min-width: 280px;
            max-width: 400px;
        }
        
        .toast.show {
            transform: translateX(0);
            opacity: 1;
        }
        
        .toast.hide {
            transform: translateX(120%);
            opacity: 0;
        }
        
        .toast-icon {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            font-weight: bold;
            flex-shrink: 0;
        }
        
        .toast-message {
            flex: 1;
            font-size: 14px;
            font-weight: 500;
            color: #1e293b;
            line-height: 1.4;
        }
        
        .toast-close {
            background: none;
            border: none;
            font-size: 20px;
            color: #94a3b8;
            cursor: pointer;
            padding: 0;
            line-height: 1;
            transition: color 0.2s;
        }
        
        .toast-close:hover {
            color: #64748b;
        }
        
        /* Success Toast */
        .toast-success {
            border-left: 4px solid #10b981;
        }
        .toast-success .toast-icon {
            background: rgba(16, 185, 129, 0.1);
            color: #10b981;
        }
        
        /* Error Toast */
        .toast-error {
            border-left: 4px solid #ef4444;
        }
        .toast-error .toast-icon {
            background: rgba(239, 68, 68, 0.1);
            color: #ef4444;
        }
        
        /* Warning Toast */
        .toast-warning {
            border-left: 4px solid #f59e0b;
        }
        .toast-warning .toast-icon {
            background: rgba(245, 158, 11, 0.1);
            color: #f59e0b;
        }
        
        /* Info Toast */
        .toast-info {
            border-left: 4px solid #3b82f6;
        }
        .toast-info .toast-icon {
            background: rgba(59, 130, 246, 0.1);
            color: #3b82f6;
        }
        
        /* Dark Mode Support */
        body.dark-mode .toast,
        .dark-mode .toast {
            background: #1e293b;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
        }
        
        body.dark-mode .toast-message,
        .dark-mode .toast-message {
            color: #f1f5f9;
        }
        
        body.dark-mode .toast-close,
        .dark-mode .toast-close {
            color: #64748b;
        }
        
        body.dark-mode .toast-close:hover,
        .dark-mode .toast-close:hover {
            color: #94a3b8;
        }
        
        /* Mobile Responsive */
        @media (max-width: 480px) {
            #toast-container {
                top: auto;
                bottom: 20px;
                left: 20px;
                right: 20px;
                max-width: none;
            }
            
            .toast {
                min-width: auto;
                max-width: none;
                transform: translateY(120%);
            }
            
            .toast.show {
                transform: translateY(0);
            }
            
            .toast.hide {
                transform: translateY(120%);
            }
        }
    `;
    document.head.appendChild(styles);
})();
