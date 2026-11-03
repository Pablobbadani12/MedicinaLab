// MedicinaLab – base.js
(function () {
    // 1. Mark active nav item based on current URL
    const currentPath = window.location.pathname;
    let bestMatch = null;
    let bestLength = 0;
    
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(function (link) {
        link.classList.remove('active');
        const href = link.getAttribute('href');
        if (href && href !== '/' && currentPath.startsWith(href) && href.length > bestLength) {
            bestMatch = link;
            bestLength = href.length;
        }
    });
    
    if (bestMatch) {
        bestMatch.classList.add('active');
    }

    // 2. Mobile Sidebar Toggle Logic
    const sidebar = document.getElementById('sidebar');
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    function toggleSidebar() {
        if (sidebar && sidebarOverlay) {
            const isOpen = sidebar.classList.contains('open');
            if (isOpen) {
                closeSidebar();
            } else {
                openSidebar();
            }
        }
    }

    function openSidebar() {
        if (sidebar && sidebarOverlay) {
            sidebar.classList.add('open');
            sidebarOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }

    function closeSidebar() {
        if (sidebar && sidebarOverlay) {
            sidebar.classList.remove('open');
            sidebarOverlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', toggleSidebar);
    }

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeSidebar);
    }

    // Close sidebar on Escape key
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && sidebar && sidebar.classList.contains('open')) {
            closeSidebar();
        }
    });

    // Close sidebar when clicking a nav link in mobile view
    if (navItems) {
        navItems.forEach(function (item) {
            item.addEventListener('click', function () {
                if (window.innerWidth < 992) {
                    closeSidebar();
                }
            });
        });
    }
})();

