/**
 * NutriTracker.ai - Onboarding JavaScript
 * Handles slide navigation, API calls, and validations
 */

// ============================================
// Global State
// ============================================

let currentSlide = 1;
let selectedGoal = null;
// Dynamic API URL - works for localhost and network sharing
const API_BASE = `${window.location.protocol}//${window.location.host}`;

// ============================================
// Initialization
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Onboarding initialized');
    checkOnboardingStatus();
});

// ============================================
// Check Onboarding Status
// ============================================

async function checkOnboardingStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/profile/status`);
        
        if (response.ok) {
            const data = await response.json();
            
            if (data.complete) {
                // Already completed, go to dashboard
                console.log('✓ Onboarding already complete');
                showMessage('You have already completed onboarding!', 'success');
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 2000);
            } else {
                // Resume from last slide
                console.log(`Resuming from slide ${data.last_slide}`);
                goToSlide(data.last_slide);
            }
        } else {
            // No profile found, start from slide 1
            console.log('No profile found, starting onboarding');
            goToSlide(1);
        }
    } catch (error) {
        console.error('Error checking status:', error);
        // Start from slide 1 on error
        goToSlide(1);
    }
}

// ============================================
// Slide Navigation
// ============================================

function goToSlide(slideNumber) {
    // Validate slide number
    if (slideNumber < 1 || slideNumber > 3) return;
    
    // Hide current slide
    const currentSlideEl = document.getElementById(`slide${currentSlide}`);
    if (currentSlideEl) {
        currentSlideEl.classList.remove('active');
    }
    
    // Show new slide
    currentSlide = slideNumber;
    const newSlideEl = document.getElementById(`slide${currentSlide}`);
    if (newSlideEl) {
        newSlideEl.classList.add('active');
    }
    
    // Update progress bar
    updateProgress();
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function nextSlide() {
    if (currentSlide < 3) {
        goToSlide(currentSlide + 1);
    }
}

function previousSlide() {
    if (currentSlide > 1) {
        goToSlide(currentSlide - 1);
    }
}

function updateProgress() {
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    
    const percentage = (currentSlide / 3) * 100;
    progressBar.style.width = `${percentage}%`;
    progressText.textContent = `Step ${currentSlide} of 3`;
}

// ============================================
// Slide 1: Goal Selection
// ============================================

function selectGoal(goal) {
    selectedGoal = goal;
    
    // Update UI - remove all selections
    document.querySelectorAll('.goal-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Add selection to clicked card
    const selectedCard = document.querySelector(`.goal-card[data-goal="${goal}"]`);
    if (selectedCard) {
        selectedCard.classList.add('selected');
    }
    
    // Enable next button
    document.getElementById('slide1Next').disabled = false;
    
    console.log('Selected goal:', goal);
    
    // Save goal to backend
    saveGoal(goal);
}

async function saveGoal(goal) {
    try {
        const response = await fetch(`${API_BASE}/api/onboarding/goal`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ goal })
        });
        
        if (response.ok) {
            console.log('✓ Goal saved successfully');
        } else {
            const error = await response.json();
            console.error('Failed to save goal:', error.detail);
        }
    } catch (error) {
        console.error('Error saving goal:', error);
    }
}

// ============================================
// Slide 2: Metrics Input & Validation
// ============================================

function validateMetricsForm() {
    const gender = document.getElementById('gender').value;
    const age = parseInt(document.getElementById('age').value);
    const height = parseFloat(document.getElementById('height').value);
    const weight = parseFloat(document.getElementById('weight').value);
    const activityLevel = document.getElementById('activityLevel').value;
    
    // Check all fields are filled
    if (!gender || !age || !height || !weight || !activityLevel) {
        showError('Please fill in all fields');
        return null;
    }
    
    // Validate age
    if (age < 13 || age > 120) {
        showError('Age must be between 13 and 120 years');
        return null;
    }
    
    // Validate height
    if (height < 100 || height > 250) {
        showError('Height must be between 100 and 250 cm');
        return null;
    }
    
    // Validate weight
    if (weight < 30 || weight > 300) {
        showError('Weight must be between 30 and 300 kg');
        return null;
    }
    
    // All valid
    hideError();
    
    return {
        goal: selectedGoal,
        gender,
        age,
        height_cm: height,
        weight_kg: weight,
        activity_level: activityLevel
    };
}

function showError(message) {
    const errorDiv = document.getElementById('metricsError');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    
    // Scroll to error
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function hideError() {
    const errorDiv = document.getElementById('metricsError');
    errorDiv.style.display = 'none';
}

// ============================================
// Calculate Profile (Submit Metrics)
// ============================================

async function calculateProfile() {
    // Validate form
    const metrics = validateMetricsForm();
    if (!metrics) {
        return;
    }
    
    // Show loading overlay
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/api/onboarding/metrics`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(metrics)
        });
        
        if (response.ok) {
            const profile = await response.json();
            console.log('✓ Profile calculated:', profile);
            
            // Display results
            displayResults(profile);
            
            // Move to slide 3
            setTimeout(() => {
                hideLoading();
                nextSlide();
            }, 800);
        } else {
            const error = await response.json();
            hideLoading();
            showError(error.detail || 'Failed to calculate profile');
        }
    } catch (error) {
        console.error('Error calculating profile:', error);
        hideLoading();
        showError('Network error. Please try again.');
    }
}

// ============================================
// Slide 3: Display Results
// ============================================

function displayResults(profile) {
    // BMI Section
    document.getElementById('bmiValue').textContent = profile.bmi.toFixed(1);
    
    const bmiCategoryEl = document.getElementById('bmiCategory');
    bmiCategoryEl.textContent = profile.bmi_category;
    bmiCategoryEl.className = `result-badge ${profile.bmi_category.toLowerCase().replace(' ', '')}`;
    
    document.getElementById('idealWeight').textContent = `Ideal: ${profile.ideal_weight_range}`;
    
    // Calorie Section
    document.getElementById('calorieGoal').textContent = `${profile.daily_calorie_goal} cal`;
    document.getElementById('goalDescription').textContent = profile.goal_description;
    document.getElementById('maintenanceCalories').textContent = profile.maintenance_calories;
    
    // Profile Summary
    document.getElementById('summaryGoal').textContent = capitalizeFirst(profile.goal);
    document.getElementById('summaryGender').textContent = capitalizeFirst(profile.gender);
    document.getElementById('summaryAge').textContent = `${profile.age} years`;
    document.getElementById('summaryActivity').textContent = formatActivityLevel(profile.activity_level);
    
    console.log('✓ Results displayed');
}

// ============================================
// Utility Functions
// ============================================

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function formatActivityLevel(level) {
    const formatted = level.replace(/_/g, ' ');
    return formatted.split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

function showMessage(message, type = 'info') {
    // Simple console log for now
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// ============================================
// Dashboard Navigation
// ============================================

function goToDashboard() {
    // Redirect to dashboard
    window.location.href = 'dashboard.html';
}

// ============================================
// Form Real-time Validation (Optional)
// ============================================

// Add event listeners for real-time feedback
document.addEventListener('DOMContentLoaded', () => {
    const ageInput = document.getElementById('age');
    const heightInput = document.getElementById('height');
    const weightInput = document.getElementById('weight');
    
    if (ageInput) {
        ageInput.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            if (value && (value < 13 || value > 120)) {
                e.target.classList.add('is-invalid');
            } else {
                e.target.classList.remove('is-invalid');
            }
        });
    }
    
    if (heightInput) {
        heightInput.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            if (value && (value < 100 || value > 250)) {
                e.target.classList.add('is-invalid');
            } else {
                e.target.classList.remove('is-invalid');
            }
        });
    }
    
    if (weightInput) {
        weightInput.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            if (value && (value < 30 || value > 300)) {
                e.target.classList.add('is-invalid');
            } else {
                e.target.classList.remove('is-invalid');
            }
        });
    }
});

// ============================================
// Keyboard Navigation (Optional Enhancement)
// ============================================

document.addEventListener('keydown', (e) => {
    // Enter key on slide 1 with goal selected
    if (currentSlide === 1 && e.key === 'Enter' && selectedGoal) {
        nextSlide();
    }
    
    // Arrow keys for navigation
    if (e.key === 'ArrowLeft' && currentSlide > 1) {
        previousSlide();
    }
});

// ============================================
// Export functions for HTML onclick handlers
// ============================================

// Make functions globally available
window.selectGoal = selectGoal;
window.nextSlide = nextSlide;
window.previousSlide = previousSlide;
window.calculateProfile = calculateProfile;
window.goToDashboard = goToDashboard;

console.log('✓ Onboarding.js loaded successfully');
