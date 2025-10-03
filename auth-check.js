// Role-based access control for admin pages
class AdminAuth {
    constructor() {
        this.currentUser = null;
        this.userPermissions = [];
        this.init();
    }

    async init() {
        // Check if user is authenticated
        if (!sessionStorage.getItem('pandaAdmin')) {
            this.redirectToLogin();
            return;
        }

        const adminEmail = sessionStorage.getItem('adminUser');
        if (!adminEmail) {
            this.redirectToLogin();
            return;
        }

        // Load user permissions
        await this.loadUserPermissions(adminEmail);
        this.enforcePageAccess();
    }

    async loadUserPermissions(email) {
        try {
            // Check if super admin
            const superAdmins = [
                'admin@pandaexteriors.com',
                'super@pandaexteriors.com', 
                'rob@pandaexteriors.com',
                'rb.winters@me.com'
            ];

            if (superAdmins.includes(email.toLowerCase())) {
                this.userPermissions = ['employees', 'points', 'referrals', 'leads', 'assets', 'admin'];
                this.currentUser = { email, role: 'super_admin' };
                return;
            }

            // Load from admin users table
            const response = await fetch('https://dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth.lambda-url.us-east-2.on.aws/admin-users');
            const data = await response.json();
            
            if (data.users) {
                const user = data.users.find(u => u.email.toLowerCase() === email.toLowerCase());
                if (user && user.active) {
                    this.currentUser = user;
                    this.userPermissions = user.permissions || [];
                    
                    // Set default permissions based on role
                    if (user.role === 'referrals_admin') {
                        this.userPermissions = ['referrals'];
                    } else if (user.role === 'points_admin') {
                        this.userPermissions = ['points'];
                    } else if (user.role === 'admin') {
                        this.userPermissions = ['employees', 'points', 'referrals'];
                    }
                } else {
                    this.redirectToLogin();
                }
            } else {
                this.redirectToLogin();
            }
        } catch (error) {
            console.error('Error loading user permissions:', error);
            this.redirectToLogin();
        }
    }

    enforcePageAccess() {
        const currentPage = window.location.pathname;
        const pagePermissions = {
            '/admin.html': ['employees', 'admin'],
            '/points.html': ['points'],
            '/referrals.html': ['referrals'],
            '/referrals': ['referrals'],
            '/leads': ['leads'],
            '/leads.html': ['leads'],
            '/assets': ['assets'],
            '/assets.html': ['assets']
        };

        // Check if current page requires specific permissions
        const requiredPermissions = pagePermissions[currentPage];
        if (requiredPermissions) {
            const hasAccess = requiredPermissions.some(perm => this.userPermissions.includes(perm));
            
            if (!hasAccess) {
                // Redirect to first allowed page
                this.redirectToAllowedPage();
                return;
            }
        }

        // Hide navigation items user doesn't have access to
        this.updateNavigation();
    }

    updateNavigation() {
        const navItems = {
            'employees': ['/admin.html'],
            'points': ['/points.html'],
            'referrals': ['/referrals.html', '/referrals'],
            'leads': ['/leads', '/leads.html'],
            'assets': ['/assets', '/assets.html']
        };

        // Hide nav links user doesn't have access to
        document.querySelectorAll('.nav-links a').forEach(link => {
            const href = link.getAttribute('href');
            let hasAccess = false;

            for (const [permission, urls] of Object.entries(navItems)) {
                if (urls.some(url => href.includes(url.replace('.html', '')) || href === url)) {
                    if (this.userPermissions.includes(permission)) {
                        hasAccess = true;
                        break;
                    }
                }
            }

            if (!hasAccess && !href.includes('admin.html')) {
                link.style.display = 'none';
            }
        });

        // Show user info
        this.displayUserInfo();
    }

    displayUserInfo() {
        const userInfo = document.createElement('div');
        userInfo.className = 'user-info text-muted';
        userInfo.style.fontSize = '12px';
        userInfo.innerHTML = `
            <i class="fas fa-user"></i> ${this.currentUser.email}
            <br><small>${this.currentUser.role || 'admin'}</small>
        `;

        const logoutBtn = document.querySelector('.logout-btn');
        if (logoutBtn && !document.querySelector('.user-info')) {
            logoutBtn.parentNode.insertBefore(userInfo, logoutBtn);
        }
    }

    redirectToAllowedPage() {
        // Redirect to first page user has access to
        if (this.userPermissions.includes('referrals')) {
            window.location.href = '/referrals.html';
        } else if (this.userPermissions.includes('points')) {
            window.location.href = '/points.html';
        } else if (this.userPermissions.includes('employees')) {
            window.location.href = '/admin.html';
        } else if (this.userPermissions.includes('leads')) {
            window.location.href = '/leads';
        } else {
            this.redirectToLogin();
        }
    }

    redirectToLogin() {
        sessionStorage.removeItem('pandaAdmin');
        sessionStorage.removeItem('adminUser');
        window.location.href = '/login.html';
    }

    hasPermission(permission) {
        return this.userPermissions.includes(permission);
    }
}

// Initialize auth check when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.adminAuth = new AdminAuth();
});