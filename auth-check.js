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
                console.log('Super admin access granted:', this.userPermissions);
                return;
            }

            // Load from admin users table
            const response = await fetch('https://dfu3zr3dnrvgiiwa2yu77cz5fq0rqmth.lambda-url.us-east-2.on.aws/admin-users', {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) {
                throw new Error('Failed to fetch admin users');
            }
            
            const data = await response.json();
            console.log('Admin users response:', data);
            
            if (data.users) {
                const user = data.users.find(u => u.email && u.email.toLowerCase() === email.toLowerCase());
                console.log('Found user:', user);
                
                if (user && user.active !== false) {
                    this.currentUser = user;
                    
                    // Set permissions based on role
                    if (user.role === 'referrals_admin') {
                        this.userPermissions = ['referrals'];
                    } else if (user.role === 'points_admin') {
                        this.userPermissions = ['points'];
                    } else if (user.role === 'admin') {
                        this.userPermissions = ['employees', 'points', 'referrals', 'leads'];
                    } else {
                        this.userPermissions = user.permissions || [];
                    }
                    
                    console.log('User permissions set:', this.userPermissions);
                } else {
                    console.log('User not found or inactive');
                    this.redirectToLogin();
                    return;
                }
            } else {
                console.log('No users data in response');
                this.redirectToLogin();
                return;
            }
        } catch (error) {
            console.error('Error loading user permissions:', error);
            this.redirectToLogin();
        }
    }

    enforcePageAccess() {
        const currentPage = window.location.pathname;
        console.log('Current page:', currentPage);
        console.log('User permissions:', this.userPermissions);
        
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
        console.log('Required permissions for page:', requiredPermissions);
        
        if (requiredPermissions) {
            const hasAccess = requiredPermissions.some(perm => this.userPermissions.includes(perm));
            console.log('Has access to page:', hasAccess);
            
            if (!hasAccess) {
                console.log('Access denied, redirecting to allowed page');
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
            'employees': ['/admin.html', '/employee'],
            'points': ['/points.html', '/points'],
            'referrals': ['/referrals.html', '/referrals'],
            'leads': ['/leads', '/leads.html'],
            'assets': ['/assets', '/assets.html']
        };

        console.log('Updating navigation with permissions:', this.userPermissions);

        // Hide nav links user doesn't have access to
        document.querySelectorAll('.nav-links a').forEach(link => {
            const href = link.getAttribute('href');
            const onclick = link.getAttribute('onclick');
            let hasAccess = false;

            // Check onclick navigation
            if (onclick) {
                for (const [permission, urls] of Object.entries(navItems)) {
                    if (urls.some(url => onclick.includes(url))) {
                        if (this.userPermissions.includes(permission)) {
                            hasAccess = true;
                            break;
                        }
                    }
                }
            }
            
            // Check href navigation
            if (href && !hasAccess) {
                for (const [permission, urls] of Object.entries(navItems)) {
                    if (urls.some(url => href.includes(url.replace('.html', '')) || href === url)) {
                        if (this.userPermissions.includes(permission)) {
                            hasAccess = true;
                            break;
                        }
                    }
                }
            }

            console.log(`Nav link ${href || onclick}: hasAccess = ${hasAccess}`);
            
            if (!hasAccess) {
                link.style.display = 'none';
            } else {
                link.style.display = '';
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
        console.log('Redirecting to allowed page with permissions:', this.userPermissions);
        
        // Redirect to first page user has access to
        if (this.userPermissions.includes('referrals')) {
            console.log('Redirecting to referrals');
            window.location.href = '/referrals.html';
        } else if (this.userPermissions.includes('points')) {
            console.log('Redirecting to points');
            window.location.href = '/points.html';
        } else if (this.userPermissions.includes('employees')) {
            console.log('Redirecting to admin');
            window.location.href = '/admin.html';
        } else if (this.userPermissions.includes('leads')) {
            console.log('Redirecting to leads');
            window.location.href = '/leads.html';
        } else {
            console.log('No permissions found, redirecting to login');
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