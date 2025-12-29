/**
 * NutriTracker.ai - Add Meal Module
 * Complete JavaScript for all 5 sections
 */

// Global state
const AddMealApp = {
    token: null,
    currentAIData: null,
    uploadedImageFile: null
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    AddMealApp.token = localStorage.getItem('token');
    
    if (!AddMealApp.token) {
        // Send message to parent window (dashboard)
        if (window.parent !== window) {
            window.parent.postMessage('sessionExpired', '*');
        } else {
            window.location.href = 'index.html';
        }
        return;
    }

    initAIUpload();
    initMealForm();
    loadUserPresets();
    loadAdminSuggestions();
    loadTodayMeals();
});

// ===========================================================================
// SECTION 1: AI UPLOAD
// ===========================================================================
function initAIUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('imageInput');
    const imagePreview = document.getElementById('imagePreview');
    const detectBtn = document.getElementById('detectBtn');

    // Click to upload
    uploadArea.addEventListener('click', () => fileInput.click());

    // File input change
    fileInput.addEventListener('change', handleImageSelect);

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    // Detect food button
    detectBtn.addEventListener('click', detectFood);
}

function handleImageSelect(e) {
    const file = e.target.files[0];
    if (file) handleFile(file);
}

function handleFile(file) {
    // Validate file
    if (!file.type.startsWith('image/')) {
        alert('Please upload an image file');
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        alert('Image must be less than 5MB');
        return;
    }

    AddMealApp.uploadedImageFile = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        const imagePreview = document.getElementById('imagePreview');
        imagePreview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
        imagePreview.style.display = 'block';
        
        document.getElementById('detectBtn').disabled = false;
    };
    reader.readAsDataURL(file);
}

async function detectFood() {
    if (!AddMealApp.uploadedImageFile) return;

    const detectBtn = document.getElementById('detectBtn');
    detectBtn.disabled = true;
    detectBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Detecting...';

    try {
        // Convert to base64
        const base64 = await fileToBase64(AddMealApp.uploadedImageFile);

        const response = await fetch('/api/ai/detect-food', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${AddMealApp.token}`
            },
            body: JSON.stringify({ image_base64: base64 })
        });

        const data = await response.json();

        if (response.ok && data.detected) {
            AddMealApp.currentAIData = data;
            fillFormFromAI(data);
            showToast('✅ Food detected! Review and log your meal.', 'success');
        } else {
            showToast('⚠️ Could not detect food. Please enter manually.', 'warning');
        }
    } catch (error) {
        console.error('Detection error:', error);
        showToast('❌ Detection failed. Please try again.', 'error');
    } finally {
        detectBtn.disabled = false;
        detectBtn.innerHTML = '<i class="fas fa-wand-magic-sparkles"></i> Detect Food';
    }
}

function fillFormFromAI(data) {
    document.getElementById('mealName').value = data.meal_name;
    document.getElementById('calories').value = data.calories;
    document.getElementById('protein').value = data.protein_g;
    document.getElementById('carbs').value = data.carbs_g;
    document.getElementById('fat').value = data.fat_g;
    document.getElementById('notes').value = `AI Detected (${(data.confidence * 100).toFixed(0)}% confidence)`;
}

function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            const base64 = reader.result.split(',')[1];
            resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

// ===========================================================================
// SECTION 2: LOG MEAL FORM
// ===========================================================================
function initMealForm() {
    const logMealBtn = document.getElementById('logMealBtn');
    const savePresetBtn = document.getElementById('savePresetBtn');

    logMealBtn.addEventListener('click', handleMealSubmit);
    savePresetBtn.addEventListener('click', saveAsPreset);
}

async function handleMealSubmit() {
    const mealData = {
        meal_type: document.getElementById('mealType').value,
        meal_name: document.getElementById('mealName').value.trim(),
        calories: parseInt(document.getElementById('calories').value) || 0,
        protein_g: parseFloat(document.getElementById('protein').value) || 0,
        carbs_g: parseFloat(document.getElementById('carbs').value) || 0,
        fat_g: parseFloat(document.getElementById('fat').value) || 0,
        notes: document.getElementById('notes').value.trim() || null,
        source: AddMealApp.currentAIData ? 'ai' : 'manual',
        image_url: null
    };

    // Validation
    if (!mealData.meal_name) {
        showToast('❌ Please enter a meal name', 'error');
        return;
    }

    if (mealData.calories === 0) {
        showToast('❌ Please enter calories', 'error');
        return;
    }

    try {
        const response = await fetch('/api/meals', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${AddMealApp.token}`
            },
            body: JSON.stringify(mealData)
        });

        if (response.ok) {
            showToast('✅ Meal logged successfully!', 'success');
            clearForm();
            loadTodayMeals(); // Refresh today's section
        } else {
            const error = await response.json();
            showToast(`❌ ${error.detail || 'Failed to log meal'}`, 'error');
        }
    } catch (error) {
        console.error('Error logging meal:', error);
        showToast('❌ Network error. Please try again.', 'error');
    }
}

async function saveAsPreset() {
    const presetData = {
        meal_name: document.getElementById('mealName').value.trim(),
        calories: parseInt(document.getElementById('calories').value) || 0,
        protein_g: parseFloat(document.getElementById('protein').value) || 0,
        carbs_g: parseFloat(document.getElementById('carbs').value) || 0,
        fat_g: parseFloat(document.getElementById('fat').value) || 0,
        notes: document.getElementById('notes').value.trim() || null
    };

    if (!presetData.meal_name) {
        showToast('❌ Please enter a meal name', 'error');
        return;
    }

    try {
        const response = await fetch('/api/user-meal-presets', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${AddMealApp.token}`
            },
            body: JSON.stringify(presetData)
        });

        if (response.ok) {
            showToast('✅ Preset saved successfully!', 'success');
            loadUserPresets(); // Refresh presets section
        } else {
            const error = await response.json();
            showToast(`❌ ${error.detail || 'Failed to save preset'}`, 'error');
        }
    } catch (error) {
        console.error('Error saving preset:', error);
        showToast('❌ Network error. Please try again.', 'error');
    }
}

function clearForm() {
    document.getElementById('mealName').value = '';
    document.getElementById('calories').value = '';
    document.getElementById('protein').value = '';
    document.getElementById('carbs').value = '';
    document.getElementById('fat').value = '';
    document.getElementById('notes').value = '';
    document.getElementById('imagePreview').style.display = 'none';
    document.getElementById('imagePreview').innerHTML = '';
    document.getElementById('imageInput').value = '';
    AddMealApp.currentAIData = null;
    AddMealApp.uploadedImageFile = null;
}

// ===========================================================================
// SECTION 3: USER PRESETS
// ===========================================================================
async function loadUserPresets() {
    try {
        const response = await fetch('/api/user-meal-presets', {
            headers: { 'Authorization': `Bearer ${AddMealApp.token}` }
        });

        if (response.ok) {
            const presets = await response.json();
            renderUserPresets(presets);
        }
    } catch (error) {
        console.error('Error loading user presets:', error);
    }
}

function renderUserPresets(presets) {
    const container = document.getElementById('userPresetsGrid');
    
    if (presets.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-bookmark"></i>
                <p>No presets saved yet</p>
                <small>Log a meal and click "Save as Preset"</small>
            </div>
        `;
        return;
    }

    container.innerHTML = presets.map(preset => `
        <div class="preset-card">
            <h4>${preset.meal_name}</h4>
            <div class="preset-macros">
                <span><i class="fas fa-fire"></i> ${preset.calories} cal</span>
                <span><i class="fas fa-drumstick-bite"></i> ${preset.protein_g}g P</span>
                <span><i class="fas fa-bread-slice"></i> ${preset.carbs_g}g C</span>
                <span><i class="fas fa-cheese"></i> ${preset.fat_g}g F</span>
            </div>
            ${preset.notes ? `<p class="preset-notes">${preset.notes}</p>` : ''}
            <div class="preset-actions">
                <button class="btn-add" onclick="usePreset('${preset.preset_id}')">
                    <i class="fas fa-plus"></i> Add to Form
                </button>
                <button class="btn-delete" onclick="deleteUserPreset('${preset.preset_id}')">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
}

async function usePreset(presetId) {
    try {
        const response = await fetch('/api/user-meal-presets', {
            headers: { 'Authorization': `Bearer ${AddMealApp.token}` }
        });

        if (response.ok) {
            const presets = await response.json();
            const preset = presets.find(p => p.preset_id === presetId);
            
            if (preset) {
                document.getElementById('mealName').value = preset.meal_name;
                document.getElementById('calories').value = preset.calories;
                document.getElementById('protein').value = preset.protein_g;
                document.getElementById('carbs').value = preset.carbs_g;
                document.getElementById('fat').value = preset.fat_g;
                document.getElementById('notes').value = preset.notes || '';
                
                // Scroll to form
                document.querySelector('.manual-entry-section').scrollIntoView({ behavior: 'smooth' });
                showToast('✅ Preset loaded into form', 'success');
            }
        }
    } catch (error) {
        console.error('Error using preset:', error);
    }
}

async function deleteUserPreset(presetId) {
    if (!confirm('Delete this preset?')) return;

    try {
        const response = await fetch(`/api/user-meal-presets/${presetId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${AddMealApp.token}` }
        });

        if (response.ok) {
            showToast('✅ Preset deleted', 'success');
            loadUserPresets();
        }
    } catch (error) {
        console.error('Error deleting preset:', error);
        showToast('❌ Failed to delete preset', 'error');
    }
}

// ===========================================================================
// SECTION 4: ADMIN SUGGESTIONS
// ===========================================================================
async function loadAdminSuggestions() {
    try {
        const response = await fetch('/api/admin-meal-presets', {
            headers: { 'Authorization': `Bearer ${AddMealApp.token}` }
        });

        if (response.ok) {
            const suggestions = await response.json();
            renderAdminSuggestions(suggestions);
        }
    } catch (error) {
        console.error('Error loading admin suggestions:', error);
    }
}

function renderAdminSuggestions(suggestions) {
    const container = document.getElementById('adminSuggestionsGrid');
    
    if (suggestions.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-star"></i>
                <p>No suggestions available</p>
            </div>
        `;
        return;
    }

    container.innerHTML = suggestions.map(suggestion => `
        <div class="preset-card admin-card">
            <div class="admin-badge"><i class="fas fa-crown"></i> Recommended</div>
            <h4>${suggestion.meal_name}</h4>
            <div class="preset-macros">
                <span><i class="fas fa-fire"></i> ${suggestion.calories} cal</span>
                <span><i class="fas fa-drumstick-bite"></i> ${suggestion.protein_g}g P</span>
                <span><i class="fas fa-bread-slice"></i> ${suggestion.carbs_g}g C</span>
                <span><i class="fas fa-cheese"></i> ${suggestion.fat_g}g F</span>
            </div>
            ${suggestion.notes ? `<p class="preset-notes">${suggestion.notes}</p>` : ''}
            ${suggestion.category ? `<span class="category-tag">${suggestion.category}</span>` : ''}
            <button class="btn-add" onclick="useAdminSuggestion('${suggestion.preset_id}')">
                <i class="fas fa-plus"></i> Add to Form
            </button>
        </div>
    `).join('');
}

async function useAdminSuggestion(presetId) {
    try {
        const response = await fetch('/api/admin-meal-presets', {
            headers: { 'Authorization': `Bearer ${AddMealApp.token}` }
        });

        if (response.ok) {
            const suggestions = await response.json();
            const suggestion = suggestions.find(s => s.preset_id === presetId);
            
            if (suggestion) {
                document.getElementById('mealName').value = suggestion.meal_name;
                document.getElementById('calories').value = suggestion.calories;
                document.getElementById('protein').value = suggestion.protein_g;
                document.getElementById('carbs').value = suggestion.carbs_g;
                document.getElementById('fat').value = suggestion.fat_g;
                document.getElementById('notes').value = suggestion.notes || '';
                
                // Scroll to form
                document.querySelector('.manual-entry-section').scrollIntoView({ behavior: 'smooth' });
                showToast('✅ Suggestion loaded into form', 'success');
            }
        }
    } catch (error) {
        console.error('Error using suggestion:', error);
    }
}

// ===========================================================================
// SECTION 5: TODAY'S MEALS
// ===========================================================================
async function loadTodayMeals() {
    try {
        const response = await fetch('/api/meals/today', {
            headers: { 'Authorization': `Bearer ${AddMealApp.token}` }
        });

        if (response.ok) {
            const data = await response.json();
            renderTodayMeals(data);
        }
    } catch (error) {
        console.error('Error loading today meals:', error);
    }
}

function renderTodayMeals(data) {
    // Update summary cards
    document.getElementById('totalCalories').textContent = data.summary.total_calories;
    document.getElementById('totalProtein').textContent = data.summary.total_protein.toFixed(1);
    document.getElementById('totalCarbs').textContent = data.summary.total_carbs.toFixed(1);
    document.getElementById('totalFat').textContent = data.summary.total_fat.toFixed(1);

    // Render meals list
    const container = document.getElementById('todayMealsList');
    
    if (data.meals.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-utensils"></i>
                <p>No meals logged today</p>
                <small>Start logging your meals above!</small>
            </div>
        `;
        return;
    }

    // Group by meal type
    const grouped = data.meals.reduce((acc, meal) => {
        if (!acc[meal.meal_type]) acc[meal.meal_type] = [];
        acc[meal.meal_type].push(meal);
        return acc;
    }, {});

    container.innerHTML = Object.entries(grouped).map(([type, meals]) => `
        <div class="meal-type-group">
            <h3 class="meal-type-title">
                <i class="fas fa-${getMealIcon(type)}"></i>
                ${type.charAt(0).toUpperCase() + type.slice(1)}
            </h3>
            ${meals.map(meal => `
                <div class="meal-item">
                    <div class="meal-info">
                        <strong>${meal.meal_name}</strong>
                        <div class="meal-macros">
                            <span>${meal.calories} cal</span>
                            <span>P: ${meal.protein_g}g</span>
                            <span>C: ${meal.carbs_g}g</span>
                            <span>F: ${meal.fat_g}g</span>
                        </div>
                        ${meal.notes ? `<small>${meal.notes}</small>` : ''}
                    </div>
                    <button class="btn-delete-meal" onclick="deleteMeal('${meal.meal_id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `).join('')}
        </div>
    `).join('');
}

async function deleteMeal(mealId) {
    if (!confirm('Delete this meal?')) return;

    try {
        const response = await fetch(`/api/meals/${mealId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${AddMealApp.token}` }
        });

        if (response.ok) {
            showToast('✅ Meal deleted', 'success');
            loadTodayMeals();
        }
    } catch (error) {
        console.error('Error deleting meal:', error);
        showToast('❌ Failed to delete meal', 'error');
    }
}

function getMealIcon(type) {
    const icons = {
        breakfast: 'mug-hot',
        lunch: 'hamburger',
        dinner: 'pizza-slice',
        snack: 'cookie'
    };
    return icons[type] || 'utensils';
}

// ===========================================================================
// UTILITY FUNCTIONS
// ===========================================================================
function showToast(message, type = 'info') {
    if (typeof window.parent.showToast === 'function') {
        window.parent.showToast(message, type);
    } else {
        alert(message);
    }
}
