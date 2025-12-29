/**
 * NutriTracker.ai - Profile Page JavaScript
 * Module 7: User Profile & Settings
 * 
 * This file handles:
 * - Tab switching between Personal, Goals, Settings
 * - Fetching user profile data from API
 * - Updating personal information (name, age, height, weight)
 * - Updating goals (goal type, target weight, activity level)
 * - Calculating and displaying stats (BMI, calories)
 * - Form validation and error handling
 */

// ============================================
// CONFIGURATION
// ============================================
// Dynamic API URL - works for localhost and network sharing
const API_BASE = `${window.location.protocol}//${window.location.host}`;

// Store current user data globally
let currentProfile = null;
let selectedGoal = null;
let selectedActivity = null;

// ============================================
// PAGE INITIALIZATION
// When page loads, fetch and display user data
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Profile page initialized');
    
    // Dark mode is now handled by dark-mode.js
    // Just attach the toggle event listener
    const toggle = document.getElementById('darkModeToggle');
    if (toggle) {
        toggle.addEventListener('change', function() {
            // Use the shared dark mode function from dark-mode.js
            toggleDarkMode(this.checked);
        });
        console.log('🌙 Dark mode toggle attached');
    }
    
    // Load user profile data from backend
    loadProfileData();
    
    // Setup form submission handlers
    setupFormHandlers();
    
    // Setup activity level and goal selectors
    setupSelectors();
});

// ============================================
// TAB SWITCHING FUNCTION
// Switches between Personal, Goals, Settings tabs
// ============================================
function switchTab(tabName) {
    console.log(`Switching to tab: ${tabName}`);
    
    // Remove 'active' class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Remove 'active' class from all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Add 'active' class to clicked tab button
    const tabButton = document.getElementById(`${tabName}Tab`);
    if (tabButton) {
        tabButton.classList.add('active');
    }
    
    // Add 'active' class to corresponding content
    const tabContent = document.getElementById(`${tabName}Content`);
    if (tabContent) {
        tabContent.classList.add('active');
    }
}

// ============================================
// LOAD PROFILE DATA FROM API
// Fetches complete user profile and populates all fields
// ============================================
async function loadProfileData() {
    try {
        // Show loading state (optional)
        console.log('📡 Fetching profile data...');
        
        // Get JWT token from localStorage
        const token = localStorage.getItem('token');
        
        console.log('🔑 Token check:', token ? 'Token found' : 'No token');
        
        if (!token) {
            // No token found, notify parent dashboard to redirect
            console.error('No authentication token found');
            // Send message to parent window (dashboard)
            if (window.parent !== window) {
                window.parent.postMessage('sessionExpired', '*');
            } else {
                // If not in iframe, redirect directly
                window.location.href = 'index.html';
            }
            return;
        }
        
        // Make API call to get full profile
        console.log('📡 Calling API:', `${API_BASE}/api/profile/full`);
        const response = await fetch(`${API_BASE}/api/profile/full`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json' 
            }
        });
        
        console.log('📥 API Response status:', response.status);
        
        if (!response.ok) {
            if (response.status === 401) {
                // Unauthorized - token expired or invalid
                const errorData = await response.json().catch(() => ({}));
                console.error('❌ 401 Error:', errorData);
                // Send message to parent window (dashboard)
                if (window.parent !== window) {
                    window.parent.postMessage('sessionExpired', '*');
                } else {
                    // If not in iframe, redirect directly
                    if (typeof showToast === 'function') showToast('Session expired. Please login again.', 'error');
                    setTimeout(() => { window.location.href = 'index.html'; }, 1500);
                }
                return;
            }
            throw new Error(`Failed to load profile: ${response.status}`);
        }
        
        // Parse response data
        const data = await response.json();
        console.log('✅ Profile data loaded:', data);
        
        // Store globally for later use
        currentProfile = data;
        
        // Populate all form fields with data
        populateProfileData(data);
        
    } catch (error) {
        console.error('❌ Error loading profile:', error);
        showError('Failed to load profile data. Please refresh the page.');
    }
}

// ============================================
// POPULATE PROFILE DATA
// Fills all form fields with data from API
// ============================================
function populateProfileData(data) {
    // ========== HEADER SECTION ==========
    // Update name and email in header
    document.getElementById('headerName').textContent = data.full_name || 'User';
    document.getElementById('headerEmail').textContent = data.email;
    
    // ========== PERSONAL TAB ==========
    // Fill personal information form
    document.getElementById('fullName').value = data.full_name || '';
    document.getElementById('email').value = data.email;
    document.getElementById('age').value = data.age;
    document.getElementById('height').value = data.height_cm;
    document.getElementById('weight').value = data.weight_kg;
    
    // Update stats cards
    updateStatsDisplay(data);
    
    // ========== GOALS TAB ==========
    // Display current goal
    const goalText = getGoalDisplayText(data.goal);
    document.getElementById('currentGoalDisplay').textContent = goalText;
    
    // Set target weight if exists
    if (data.target_weight_kg) {
        document.getElementById('targetWeight').value = data.target_weight_kg;
        updateWeightProgress(data.weight_kg, data.target_weight_kg, data.goal);
    }
    
    // Store selected values
    selectedGoal = data.goal;
    selectedActivity = data.activity_level;
    
    // Highlight selected activity level
    highlightActivityLevel(data.activity_level);
}

// ============================================
// UPDATE STATS DISPLAY
// Updates BMI, Calories, Weight Change cards
// ============================================
function updateStatsDisplay(data) {
    // ========== BMI CARD ==========
    const bmiValue = data.bmi.toFixed(1);
    document.getElementById('bmiValue').textContent = bmiValue;
    
    // Get BMI category (Underweight, Normal, Overweight, Obese)
    const bmiCategory = getBMICategory(data.bmi);
    document.getElementById('bmiCategory').textContent = bmiCategory;
    
    // ========== DAILY CALORIES CARD ==========
    // Format with comma separator (2000 → 2,000)
    const caloriesFormatted = data.daily_calorie_goal.toLocaleString();
    document.getElementById('caloriesValue').textContent = caloriesFormatted;
    
    // ========== WEIGHT CHANGE CARD ==========
    // This would come from tracking data (future feature)
    // For now, show placeholder
    document.getElementById('weightChangeValue').textContent = '0 kg';
}

// ============================================
// GET BMI CATEGORY
// Returns category based on BMI value
// ============================================
function getBMICategory(bmi) {
    if (bmi < 18.5) return 'Underweight';
    if (bmi < 25) return 'Normal range';
    if (bmi < 30) return 'Overweight';
    return 'Obese';
}

// ============================================
// GET GOAL DISPLAY TEXT
// Converts goal code to display text
// ============================================
function getGoalDisplayText(goal) {
    const goalMap = {
        'loss': 'Weight Loss',
        'maintain': 'Maintain Weight',
        'gain': 'Weight Gain'
    };
    return goalMap[goal] || goal;
}

// ============================================
// SETUP FORM HANDLERS
// Attach submit handlers to forms
// ============================================
function setupFormHandlers() {
    // Personal Information Form
    const personalForm = document.getElementById('personalForm');
    personalForm.addEventListener('submit', handlePersonalFormSubmit);
    
    // Goals Form
    const goalsForm = document.getElementById('goalsForm');
    goalsForm.addEventListener('submit', handleGoalsFormSubmit);
}

// ============================================
// HANDLE PERSONAL FORM SUBMISSION
// Updates name, age, height, weight
// ============================================
async function handlePersonalFormSubmit(event) {
    // Prevent default form submission (page reload)
    event.preventDefault();
    
    console.log('📝 Submitting personal information...');
    
    // Get form values
    const formData = {
        full_name: document.getElementById('fullName').value.trim(),
        age: parseInt(document.getElementById('age').value),
        height_cm: parseFloat(document.getElementById('height').value),
        weight_kg: parseFloat(document.getElementById('weight').value)
    };
    
    // Validate data
    if (!formData.full_name || formData.full_name.length < 2) {
        showError('Please enter a valid name (at least 2 characters)');
        return;
    }
    
    if (formData.age < 10 || formData.age > 120) {
        showError('Please enter a valid age (10-120)');
        return;
    }
    
    if (formData.height_cm < 50 || formData.height_cm > 300) {
        showError('Please enter a valid height (50-300 cm)');
        return;
    }
    
    if (formData.weight_kg < 20 || formData.weight_kg > 500) {
        showError('Please enter a valid weight (20-500 kg)');
        return;
    }
    
    try {
        // Get authentication token
        const token = localStorage.getItem('token');
        
        // Show saving state
        const submitBtn = event.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
        submitBtn.disabled = true;
        
        // Make API call to update personal info
        const response = await fetch(`${API_BASE}/api/profile/personal`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to update profile');
        }
        
        const result = await response.json();
        console.log('✅ Personal info updated:', result);
        
        // Show success message
        showSuccess('Personal information updated successfully!');
        
        // Update the current profile with new calculated values
        if (result.updated_metrics) {
            currentProfile.bmi = result.updated_metrics.bmi;
            currentProfile.maintenance_calories = result.updated_metrics.maintenance_calories;
            currentProfile.daily_calorie_goal = result.updated_metrics.daily_calorie_goal;
            currentProfile.weight_kg = formData.weight_kg;
            
            // Update stats display with new values
            updateStatsDisplay(currentProfile);
            
            // Update header name
            document.getElementById('headerName').textContent = formData.full_name;
        }
        
        // Restore button
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
        
    } catch (error) {
        console.error('❌ Error updating personal info:', error);
        showError(error.message || 'Failed to update personal information');
        
        // Restore button
        const submitBtn = event.target.querySelector('button[type="submit"]');
        submitBtn.innerHTML = '<i class="fas fa-check me-2"></i>Save Changes';
        submitBtn.disabled = false;
    }
}

// ============================================
// HANDLE GOALS FORM SUBMISSION
// Updates goal, target weight, activity level
// ============================================
async function handleGoalsFormSubmit(event) {
    event.preventDefault();
    
    console.log('🎯 Submitting goals...');

    // No more inputs to read from DOM — everything comes from selected variables
    const formData = {
        goal: selectedGoal || currentProfile.goal,
        activity_level: selectedActivity || currentProfile.activity_level
        // Removed: target_weight_kg, weekly_change_kg, etc.
    };

    // Basic validation
    if (!formData.goal) {
        showError('Please select a goal');
        return;
    }
    
    if (!formData.activity_level) {
        showError('Please select an activity level');
        return;
    }

    try {
        const token = localStorage.getItem('token');
        
        const submitBtn = event.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Updating...';
        submitBtn.disabled = true;

        const response = await fetch(`${API_BASE}/api/profile/goals`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to update goals');
        }

        const result = await response.json();
        console.log('✅ Goals updated:', result);
        
        showSuccess('Goals updated successfully!');

        // Update currentProfile with new values
        if (result.updated_metrics) {
            currentProfile.maintenance_calories = result.updated_metrics.maintenance_calories;
            currentProfile.daily_calorie_goal = result.updated_metrics.daily_calorie_goal;
            
            // Update goal and activity level
            currentProfile.goal = formData.goal;
            currentProfile.activity_level = formData.activity_level;

            // Update UI
            updateStatsDisplay(currentProfile);
            document.getElementById('currentGoalDisplay').textContent = getGoalDisplayText(formData.goal);
        }

        // Restore button
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;

    } catch (error) {
        console.error('❌ Error updating goals:', error);
        showError(error.message || 'Failed to update goals');

        // Restore button on error
        const submitBtn = event.target.querySelector('button[type="submit"]');
        submitBtn.innerHTML = '<i class="fas fa-check me-2"></i>Update Goals';
        submitBtn.disabled = false;
    }
}
// ============================================
// SETUP SELECTORS
// Activity level and goal selectors
// ============================================
function setupSelectors() {
    // ========== ACTIVITY LEVEL CARDS ==========
    const activityCards = document.querySelectorAll('.activity-card');
    activityCards.forEach(card => {
        card.addEventListener('click', function() {
            // Remove 'selected' from all cards
            activityCards.forEach(c => c.classList.remove('selected'));
            
            // Add 'selected' to clicked card
            this.classList.add('selected');
            
            // Store selected activity
            selectedActivity = this.getAttribute('data-activity');
            console.log('Selected activity:', selectedActivity);
        });
    });
    
    // ========== GOAL OPTION CARDS ==========
    const goalOptions = document.querySelectorAll('.goal-option');
    goalOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Remove 'selected' from all options
            goalOptions.forEach(o => o.classList.remove('selected'));
            
            // Add 'selected' to clicked option
            this.classList.add('selected');
            
            // Store selected goal
            selectedGoal = this.getAttribute('data-goal');
            console.log('Selected goal:', selectedGoal);
            
            // Update display
            document.getElementById('currentGoalDisplay').textContent = getGoalDisplayText(selectedGoal);
        });
    });
}

// ============================================
// HIGHLIGHT ACTIVITY LEVEL
// Highlights the user's current activity level
// ============================================
function highlightActivityLevel(activityLevel) {
    const activityCards = document.querySelectorAll('.activity-card');
    activityCards.forEach(card => {
        if (card.getAttribute('data-activity') === activityLevel) {
            card.classList.add('selected');
        }
    });
}

// ============================================
// SHOW GOAL SELECTOR
// Shows goal selection when "Change Goal" clicked
// ============================================
function showGoalSelector() {
    const goalSelector = document.getElementById('goalSelector');
    if (goalSelector.style.display === 'none') {
        goalSelector.style.display = 'block';
    } else {
        goalSelector.style.display = 'none';
    }
}

// ============================================
// UPDATE WEIGHT PROGRESS
// Shows current, target, and remaining weight
// ============================================
function updateWeightProgress(currentWeight, targetWeight, goal) {
    let remaining = 0;
    
    if (goal === 'loss') {
        remaining = currentWeight - targetWeight;
    } else if (goal === 'gain') {
        remaining = targetWeight - currentWeight;
    }
    
    const progressText = `Current: ${currentWeight} kg • Target: ${targetWeight} kg • Remaining: ${Math.abs(remaining).toFixed(1)} kg`;
    document.getElementById('weightProgress').textContent = progressText;
}

// ============================================
// ENABLE EDIT MODE (Future Feature)
// Could enable inline editing of profile
// ============================================
function enableEditMode() {
    // For now, just scroll to Personal tab
    switchTab('personal');
    showSuccess('Edit mode enabled! Update your information below.');
}

// ============================================
// LOGOUT FUNCTION
// Clears token and redirects to login
// ============================================
function logout() {
    // Clear authentication token
    localStorage.removeItem('token');
    sessionStorage.clear();
    
    console.log('👋 Logging out...');
    
    // Redirect to login page
    window.location.href = 'index.html';
}

// ============================================
// NOTIFICATION HELPERS
// Show success/error messages to user using toast
// ============================================
function showSuccess(message) {
    if (typeof showToast === 'function') {
        showToast(message, 'success');
    }
    console.log('✅', message);
}

function showError(message) {
    if (typeof showToast === 'function') {
        showToast(message, 'error');
    }
    console.error('❌', message);
}

// ============================================
// DARK MODE - Now handled by dark-mode.js
// ============================================
// The dark mode functionality is now centralized in dark-mode.js
// and shared across all pages for consistency

// ============================================
// EXPORT FUNCTIONS (For Testing)
// ============================================
// These functions are available globally
window.switchTab = switchTab;
window.showGoalSelector = showGoalSelector;
window.enableEditMode = enableEditMode;
window.logout = logout;
