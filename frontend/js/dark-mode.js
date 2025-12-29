/**
 * Dark Mode Management - Shared across all pages
 * This script handles dark mode for all pages in the NutriTracker app
 */

// Apply dark mode immediately on page load (before page renders)
(function() {
    const theme = localStorage.getItem('theme');
    if (theme === 'dark') {
        document.documentElement.classList.add('dark-mode');
        if (document.body) {
            document.body.classList.add('dark-mode');
        }
    } else {
        // Explicitly remove dark-mode class if theme is not dark
        document.documentElement.classList.remove('dark-mode');
        if (document.body) {
            document.body.classList.remove('dark-mode');
        }
    }
})();

// Initialize dark mode after DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    applySavedTheme();
    
    // Listen for theme changes from other pages/iframes
    window.addEventListener('storage', function(e) {
        if (e.key === 'theme') {
            applySavedTheme();
        }
    });
    
    // Listen for theme change messages from parent/iframes
    window.addEventListener('message', function(e) {
        if (e.data && e.data.type === 'themeChange') {
            applySavedTheme();
        }
    });
});

/**
 * Apply saved theme from localStorage
 */
function applySavedTheme() {
    const theme = localStorage.getItem('theme');
    const isDark = theme === 'dark';
    
    console.log('🌙 applySavedTheme - theme:', theme, 'isDark:', isDark);
    
    if (isDark) {
        document.documentElement.classList.add('dark-mode');
        document.body.classList.add('dark-mode');
    } else {
        document.documentElement.classList.remove('dark-mode');
        document.body.classList.remove('dark-mode');
    }
    
    // Update toggle if it exists on this page
    const toggle = document.getElementById('darkModeToggle');
    if (toggle) {
        toggle.checked = isDark;
        console.log('🌙 Toggle updated, checked:', toggle.checked);
    }
    
    console.log('🌙 Body has dark-mode class:', document.body.classList.contains('dark-mode'));
}

/**
 * Toggle dark mode on/off
 */
function toggleDarkMode(checked) {
    const isDark = checked;
    
    console.log('🌙 toggleDarkMode - checked:', checked, 'isDark:', isDark);
    
    if (isDark) {
        document.documentElement.classList.add('dark-mode');
        document.body.classList.add('dark-mode');
        localStorage.setItem('theme', 'dark');
        console.log('🌙 Dark mode enabled');
    } else {
        document.documentElement.classList.remove('dark-mode');
        document.body.classList.remove('dark-mode');
        localStorage.setItem('theme', 'light');
        console.log('🌙 Light mode enabled');
    }
    
    console.log('🌙 Body classList:', document.body.classList.toString());
    console.log('🌙 HTML classList:', document.documentElement.classList.toString());
    
    // Notify all iframes and parent window
    notifyThemeChange();
    
    // Force immediate update on current page
    setTimeout(() => {
        applySavedTheme();
    }, 10);
}

/**
 * Notify all windows about theme change
 */
function notifyThemeChange() {
    const message = { type: 'themeChange' };
    
    console.log('🌙 notifyThemeChange called');
    
    // Notify parent window
    if (window.parent !== window) {
        console.log('🌙 Notifying parent window');
        window.parent.postMessage(message, '*');
        
        // Also get parent to notify all its iframes
        try {
            const iframes = window.parent.document.querySelectorAll('iframe');
            console.log('🌙 Found', iframes.length, 'iframes in parent');
            iframes.forEach((iframe, index) => {
                if (iframe.contentWindow && iframe.contentWindow !== window) {
                    console.log('🌙 Notifying iframe', index);
                    iframe.contentWindow.postMessage(message, '*');
                }
            });
        } catch (e) {
            console.warn('🌙 Could not access parent iframes:', e);
        }
    }
    
    // If this is parent window, notify all iframes
    const iframes = document.querySelectorAll('iframe');
    console.log('🌙 Notifying', iframes.length, 'child iframes');
    iframes.forEach((iframe, index) => {
        if (iframe.contentWindow) {
            console.log('🌙 Notifying child iframe', index);
            iframe.contentWindow.postMessage(message, '*');
        }
    });
}
