/* ============================================
   NutriTracker Admin Panel - JavaScript
   ============================================
   File: admin/static/admin.js
   Purpose: Admin panel functionality
   
   Features:
   - Sidebar toggle for mobile
   - Edit username modal handling
   - Username validation
   - Toast notifications
   ============================================ */

// ===========================================
// SIDEBAR FUNCTIONS (Mobile responsive)
// ===========================================

/**
 * Toggle sidebar visibility on mobile devices
 * Adds/removes 'active' class to sidebar and overlay
 */
function toggleSidebar() {
    document.querySelector('.sidebar').classList.toggle('active');
    document.querySelector('.overlay').classList.toggle('active');
}

// Close sidebar when window is resized to desktop size
window.addEventListener('resize', function() {
    if (window.innerWidth > 768) {
        document.querySelector('.sidebar').classList.remove('active');
        document.querySelector('.overlay').classList.remove('active');
    }
});

// ===========================================
// EDIT MODAL FUNCTIONS
// ===========================================

/**
 * Open the edit username modal
 * @param {string} userId - The user's UUID
 * @param {string} currentName - The user's current username
 */
function openEditModal(userId, currentName) {
    // Set form action URL with user ID
    document.getElementById('editForm').action = '/admin/edit/' + userId;
    
    // Pre-fill input with current username
    document.getElementById('editFullName').value = currentName || '';
    
    // Clear any previous error messages
    hideUsernameError();
    
    // Show the modal
    document.getElementById('editModal').style.display = 'flex';
    
    // Focus the input field
    setTimeout(function() {
        document.getElementById('editFullName').focus();
    }, 100);
}

/**
 * Close the edit username modal
 */
function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
    document.getElementById('editForm').reset();
    hideUsernameError();
}

// Initialize modal event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    var editModal = document.getElementById('editModal');
    var editForm = document.getElementById('editForm');
    var editFullName = document.getElementById('editFullName');
    
    // Only setup if modal elements exist (dashboard page)
    if (editModal) {
        // Close modal when clicking outside the modal content
        editModal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeEditModal();
            }
        });
    }
    
    // Real-time validation as user types
    if (editFullName) {
        editFullName.addEventListener('input', function() {
            var result = validateUsername(this.value);
            if (!result.valid && this.value.length > 0) {
                showUsernameError(result.message);
            } else {
                hideUsernameError();
            }
        });
    }
    
    // Form submission validation
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            var username = document.getElementById('editFullName').value;
            var result = validateUsername(username);
            
            if (!result.valid) {
                e.preventDefault(); // Stop form submission
                showUsernameError(result.message);
                document.getElementById('editFullName').focus();
                return false;
            }
            
            return true; // Allow form submission
        });
    }
});

// Close modal on Escape key press
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        var editModal = document.getElementById('editModal');
        if (editModal && editModal.style.display !== 'none') {
            closeEditModal();
        }
    }
});

// ===========================================
// USERNAME VALIDATION
// ===========================================

/**
 * Validate username format
 * Rules:
 * - Not empty
 * - 2-50 characters
 * - Only alphanumeric and spaces
 * - Cannot start or end with space
 * 
 * @param {string} username - The username to validate
 * @returns {object} - {valid: boolean, message: string}
 */
function validateUsername(username) {
    // Trim whitespace
    username = username.trim();
    
    // Check if empty
    if (!username) {
        return { valid: false, message: 'Username cannot be empty' };
    }
    
    // Check length
    if (username.length < 2) {
        return { valid: false, message: 'Username must be at least 2 characters' };
    }
    
    if (username.length > 50) {
        return { valid: false, message: 'Username cannot exceed 50 characters' };
    }
    
    // Check for valid characters (alphanumeric and spaces only)
    // Pattern: starts/ends with letter or number, can have spaces in between
    var pattern = /^[a-zA-Z0-9][a-zA-Z0-9\s]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$/;
    if (!pattern.test(username)) {
        return { 
            valid: false, 
            message: 'Username can only contain letters (A-Z), numbers (0-9), and spaces. Cannot start or end with a space.' 
        };
    }
    
    return { valid: true, message: '' };
}

/**
 * Show username validation error
 * @param {string} message - Error message to display
 */
function showUsernameError(message) {
    var errorDiv = document.getElementById('usernameError');
    if (errorDiv) {
        errorDiv.querySelector('span').textContent = message;
        errorDiv.style.display = 'flex';
        document.getElementById('editFullName').classList.add('input-error');
    }
}

/**
 * Hide username validation error
 */
function hideUsernameError() {
    var errorDiv = document.getElementById('usernameError');
    if (errorDiv) {
        errorDiv.style.display = 'none';
        document.getElementById('editFullName').classList.remove('input-error');
    }
}

// ===========================================
// TOAST NOTIFICATION SYSTEM
// ===========================================

/**
 * Show admin toast notification
 * @param {string} message - Message to display
 * @param {string} type - Type: 'success', 'error', 'warning', 'info'
 */
function showAdminToast(message, type = 'info') {
    // Create container if it doesn't exist
    var container = document.getElementById('admin-toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'admin-toast-container';
        container.style.cssText = 'position:fixed;top:20px;right:20px;z-index:99999;';
        document.body.appendChild(container);
    }
    
    // Create toast element
    var toast = document.createElement('div');
    var colors = { 
        success: '#10b981', 
        error: '#ef4444', 
        warning: '#f59e0b', 
        info: '#3b82f6' 
    };
    
    toast.style.cssText = `
        background:#fff;
        padding:14px 20px;
        border-radius:8px;
        margin-bottom:10px;
        box-shadow:0 4px 12px rgba(0,0,0,0.15);
        border-left:4px solid ${colors[type] || colors.info};
        display:flex;
        align-items:center;
        gap:10px;
        min-width:280px;
        animation:slideIn 0.3s ease;
    `;
    
    toast.innerHTML = `
        <span style="flex:1;">${message}</span>
        <button onclick="this.parentElement.remove()" 
                style="background:none;border:none;font-size:18px;cursor:pointer;color:#999;">
            &times;
        </button>
    `;
    
    container.appendChild(toast);
    
    // Auto-dismiss after 4 seconds
    setTimeout(function() {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(function() { 
            toast.remove(); 
        }, 300);
    }, 4000);
}
