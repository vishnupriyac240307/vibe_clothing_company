// Vibe Clothing Company ERP Main JavaScript Engine

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initGlobalSearch();
    initNotifications();
});

// --- Theme Toggle ---
function initTheme() {
    const savedTheme = localStorage.getItem('vibe_theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    const toggleBtn = document.getElementById('theme-toggle-btn');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('vibe_theme', next);
            updateThemeIcon(next);
        });
    }
}

function updateThemeIcon(theme) {
    const icon = document.querySelector('#theme-toggle-btn i');
    if (icon) {
        icon.className = theme === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
    }
}

// --- Toast Notifications ---
function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast-item toast-${type}`;
    
    let borderColors = {
        success: '#10b981',
        danger: '#ef4444',
        warning: '#f59e0b',
        info: '#2563eb'
    };
    
    toast.style.borderLeftColor = borderColors[type] || borderColors.info;
    
    toast.innerHTML = `
        <div class="d-flex align-items-center gap-2">
            <i class="fa-solid ${type === 'success' ? 'fa-circle-check text-success' : type === 'danger' ? 'fa-circle-xmark text-danger' : 'fa-circle-info text-primary'}"></i>
            <span style="font-size: 0.875rem; font-weight: 500;">${message}</span>
        </div>
        <button type="button" class="btn-close ms-2" onclick="this.parentElement.remove()"></button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 4500);
}

// --- Global Search ---
function initGlobalSearch() {
    const searchTrigger = document.getElementById('global-search-trigger');
    const searchModal = document.getElementById('globalSearchModal');
    const searchInput = document.getElementById('globalSearchInput');
    const searchResults = document.getElementById('globalSearchResults');

    if (!searchTrigger || !searchModal || !searchInput) return;

    searchTrigger.addEventListener('click', () => {
        const bsModal = new bootstrap.Modal(searchModal);
        bsModal.show();
        setTimeout(() => searchInput.focus(), 300);
    });

    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const bsModal = bootstrap.Modal.getInstance(searchModal) || new bootstrap.Modal(searchModal);
            bsModal.show();
            setTimeout(() => searchInput.focus(), 300);
        }
    });

    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const query = e.target.value.trim();
        if (query.length < 2) {
            searchResults.innerHTML = '<div class="text-center text-muted p-4">Type at least 2 characters to search across materials, products, orders, batches, customers, suppliers, and shipments.</div>';
            return;
        }

        searchResults.innerHTML = '<div class="text-center p-4"><div class="spinner-border spinner-border-sm text-primary"></div> Searching...</div>';

        searchTimeout = setTimeout(() => {
            fetch(`/api/search?q=${encodeURIComponent(query)}`)
                .then(res => res.json())
                .then(data => {
                    if (!data.results || data.results.length === 0) {
                        searchResults.innerHTML = `<div class="text-center text-muted p-4">No records found matching "${query}".</div>`;
                        return;
                    }

                    let html = '<div class="list-group list-group-flush">';
                    data.results.forEach(item => {
                        html += `
                            <a href="${item.link}" class="list-group-item list-group-item-action d-flex align-items-center justify-content-between py-3">
                                <div class="d-flex align-items-center gap-3">
                                    <div class="rounded-circle p-2 bg-light text-primary">
                                        <i class="fa-solid ${item.icon}"></i>
                                    </div>
                                    <div>
                                        <div class="fw-bold text-dark mb-0">${item.title}</div>
                                        <small class="text-muted">${item.subtitle}</small>
                                    </div>
                                </div>
                                <span class="badge bg-secondary opacity-75">${item.category}</span>
                            </a>
                        `;
                    });
                    html += '</div>';
                    searchResults.innerHTML = html;
                })
                .catch(err => {
                    searchResults.innerHTML = '<div class="text-center text-danger p-4">Error executing search.</div>';
                });
        }, 250);
    });
}

// --- Notifications Engine ---
function initNotifications() {
    fetchNotifications();

    const markReadBtn = document.getElementById('mark-all-read-btn');
    if (markReadBtn) {
        markReadBtn.addEventListener('click', () => {
            fetch('/api/notifications/mark-read', { method: 'POST' })
                .then(res => res.json())
                .then(() => {
                    fetchNotifications();
                    showToast('All notifications marked as read.', 'info');
                });
        });
    }
}

function fetchNotifications() {
    const badge = document.getElementById('notif-badge');
    const list = document.getElementById('notif-list');
    if (!badge || !list) return;

    fetch('/api/notifications')
        .then(res => res.json())
        .then(data => {
            if (data.unread_count > 0) {
                badge.innerText = data.unread_count;
                badge.classList.remove('d-none');
            } else {
                badge.classList.add('d-none');
            }

            if (!data.notifications || data.notifications.length === 0) {
                list.innerHTML = '<div class="text-center text-muted p-4">No notifications yet.</div>';
                return;
            }

            let html = '';
            data.notifications.forEach(n => {
                let bgClass = n.is_read ? 'bg-white' : 'bg-light';
                let iconClass = n.type.includes('critical') || n.type.includes('qc_failed') ? 'text-danger fa-circle-exclamation' : 'text-warning fa-triangle-exclamation';
                html += `
                    <div class="p-3 border-bottom ${bgClass}">
                        <div class="d-flex align-items-start gap-2">
                            <i class="fa-solid ${iconClass} mt-1"></i>
                            <div class="flex-grow-1">
                                <div class="fw-bold small text-dark">${n.title}</div>
                                <div class="small text-muted mb-1">${n.message}</div>
                                <div class="d-flex justify-content-between align-items-center">
                                    <small class="text-muted" style="font-size: 0.7rem;">${n.created_at}</small>
                                    ${n.link ? `<a href="${n.link}" class="small text-primary text-decoration-none">View →</a>` : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
            list.innerHTML = html;
        });
}
