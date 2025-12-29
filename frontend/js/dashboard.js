// Dashboard functionality
// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    // Check authentication before loading dashboard
    if (!checkAuthentication()) {
        return; // Redirect to login will happen in checkAuthentication
    }
    
    loadPage('overview');
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Sidebar navigation
    document.querySelectorAll('.sidebar-item').forEach(item => {
        item.addEventListener('click', function() {
            const page = this.getAttribute('data-page');
            loadPage(page);
            
            // Update active state
            document.querySelectorAll('.sidebar-item').forEach(i => i.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Listen for messages from iframes
    window.addEventListener('message', function(e) {
        if (e.data === 'mealAdded') {
            // Switch to overview after meal is added
            setTimeout(() => {
                loadPage('overview');
                document.querySelector('[data-page="overview"]').classList.add('active');
                document.querySelector('[data-page="add-meal"]').classList.remove('active');
            }, 1500);
            
            // Update overview and history iframes
            notifyIframe('overview-iframe', 'updateStats');
            notifyIframe('history-iframe', 'updateHistory');
        } else if (e.data === 'mealDeleted') {
            // Update overview when meal is deleted
            notifyIframe('overview-iframe', 'updateStats');
        } else if (e.data === 'sessionExpired') {
            // Session expired from any iframe page
            handleSessionExpired();
        }
    });
}

// Load page content (show/hide iframes)
function loadPage(pageName) {
    // Hide all iframes
    document.querySelectorAll('.page-iframe').forEach(iframe => {
        iframe.classList.remove('active');
    });
    
    // Show selected iframe
    const targetIframe = document.getElementById(`${pageName}-iframe`);
    if (targetIframe) {
        targetIframe.classList.add('active');
    }
}

// Send message to iframe
function notifyIframe(iframeId, message) {
    const iframe = document.getElementById(iframeId);
    if (iframe && iframe.contentWindow) {
        iframe.contentWindow.postMessage(message, '*');
    }
}

// Check authentication
function checkAuthentication() {
    const token = localStorage.getItem('token');
    
    if (!token) {
        console.error('No authentication token found');
        alert('Please login to access the dashboard');
        window.location.href = 'index.html';
        return false;
    }
    
    return true;
}

// Handle session expired
function handleSessionExpired() {
    console.error('Session expired');
    localStorage.clear();
    alert('Your session has expired. Please login again.');
    window.location.href = 'index.html';
}

// Logout function
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.clear();
        window.location.href = 'index.html';
    }
}