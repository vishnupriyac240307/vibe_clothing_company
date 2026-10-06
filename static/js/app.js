/* VIBE CLOTHING COMPANY — Global Application JavaScript */

document.addEventListener("DOMContentLoaded", function() {
    // 1. Sidebar Toggle Mobile
    const sidebarToggle = document.getElementById("sidebarToggle");
    const appSidebar = document.getElementById("appSidebar");
    
    if (sidebarToggle && appSidebar) {
        sidebarToggle.addEventListener("click", function() {
            appSidebar.classList.toggle("show");
        });
    }

    // 2. Global Search Ctrl K Shortcut
    document.addEventListener("keydown", function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === "k") {
            e.preventDefault();
            const modalEl = document.getElementById("globalSearchModal");
            if (modalEl) {
                const modal = new bootstrap.Modal(modalEl);
                modal.show();
            }
        }
    });

    // 3. Theme Toggle (Light/Dark Mode)
    const themeBtn = document.getElementById("themeToggleBtn");
    const themeIcon = document.getElementById("themeIcon");
    const currentTheme = localStorage.getItem("vibe_theme") || "light";

    document.documentElement.setAttribute("data-theme", currentTheme);
    updateThemeIcon(currentTheme);

    if (themeBtn) {
        themeBtn.addEventListener("click", function() {
            const nextTheme = document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light";
            document.documentElement.setAttribute("data-theme", nextTheme);
            localStorage.setItem("vibe_theme", nextTheme);
            updateThemeIcon(nextTheme);
        });
    }

    function updateThemeIcon(theme) {
        if (themeIcon) {
            if (theme === "dark") {
                themeIcon.className = "fa-solid fa-sun fs-5 text-warning";
            } else {
                themeIcon.className = "fa-regular fa-moon fs-5";
            }
        }
    }

    // 4. Global Search Filter Handler
    const searchInput = document.getElementById("globalSearchInput");
    const searchResults = document.getElementById("globalSearchResults");

    if (searchInput && searchResults) {
        searchInput.addEventListener("input", function() {
            const query = this.value.trim();
            if (query.length < 2) {
                searchResults.innerHTML = '<p class="text-center text-muted py-3">Type at least 2 characters to search...</p>';
                return;
            }

            searchResults.innerHTML = `
                <a href="/inventory?search=${encodeURIComponent(query)}" class="list-group-item list-group-item-action d-flex justify-content-between">
                    <span><i class="fa-solid fa-boxes-stacked text-primary me-2"></i>Search Materials for "<strong>${query}</strong>"</span>
                    <span class="badge bg-light text-dark">Inventory</span>
                </a>
                <a href="/products?search=${encodeURIComponent(query)}" class="list-group-item list-group-item-action d-flex justify-content-between">
                    <span><i class="fa-solid fa-tags text-success me-2"></i>Search Product ID / Catalog for "<strong>${query}</strong>"</span>
                    <span class="badge bg-light text-dark">Products</span>
                </a>
                <a href="/production?search=${encodeURIComponent(query)}" class="list-group-item list-group-item-action d-flex justify-content-between">
                    <span><i class="fa-solid fa-industry text-warning me-2"></i>Search Orders for "<strong>${query}</strong>"</span>
                    <span class="badge bg-light text-dark">Production</span>
                </a>
                <a href="/batches?search=${encodeURIComponent(query)}" class="list-group-item list-group-item-action d-flex justify-content-between">
                    <span><i class="fa-solid fa-layer-group text-purple me-2"></i>Search Batches for "<strong>${query}</strong>"</span>
                    <span class="badge bg-light text-dark">Batches</span>
                </a>
                <a href="/shipments?search=${encodeURIComponent(query)}" class="list-group-item list-group-item-action d-flex justify-content-between">
                    <span><i class="fa-solid fa-truck-fast text-info me-2"></i>Search Shipments for "<strong>${query}</strong>"</span>
                    <span class="badge bg-light text-dark">Shipments</span>
                </a>
            `;
        });
    }

    // Password Toggle Button
    const togglePassword = document.getElementById("togglePassword");
    const passwordInput = document.getElementById("password");
    const eyeIcon = document.getElementById("eyeIcon");

    if (togglePassword && passwordInput && eyeIcon) {
        togglePassword.addEventListener("click", function() {
            const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
            passwordInput.setAttribute("type", type);
            eyeIcon.className = type === "password" ? "fa-regular fa-eye" : "fa-regular fa-eye-slash";
        });
    }
});
