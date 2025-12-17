// Load external HTML pages into #content-area
function loadPage(page) {
    fetch(`${page}.html`)
        .then(response => {
            if (!response.ok) throw new Error('Page not found');
            return response.text();
        })
        .then(html => {
            document.getElementById('content-area').innerHTML = html;
        })
        .catch(err => {
            document.getElementById('content-area').innerHTML = `
                <div class="coming-soon-card">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Page Not Ready Yet</h3>
                    <p>${page}.html is being built</p>
                </div>
            `;
        });
}

// Sidebar click handler
document.querySelectorAll('.sidebar-item').forEach(item => {
    item.addEventListener('click', () => {
        // Update active state
        document.querySelectorAll('.sidebar-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');

        // Load the page
        const page = item.getAttribute('data-page');
        loadPage(page);
    });
});

function logout() {
    localStorage.clear();
    window.location.href = 'index.html';
}