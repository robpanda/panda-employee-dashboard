// Domain Configuration
const DOMAIN_CONFIG = {
    // Production domain - replace with your actual domain
    production: {
        domain: 'your-domain.com',
        protocol: 'https',
        api: 'https://api.your-domain.com',
        cdn: 'https://cdn.your-domain.com'
    },
    
    // Development/staging
    development: {
        domain: 'panda-exteriors-map-bucket.s3.amazonaws.com',
        protocol: 'https',
        api: 'https://w40mq6ab11.execute-api.us-east-2.amazonaws.com/prod',
        cdn: 'https://panda-exteriors-map-bucket.s3.amazonaws.com'
    },
    
    // Current environment
    current: 'development' // Change to 'production' when ready
};

// Get current configuration
const CONFIG = DOMAIN_CONFIG[DOMAIN_CONFIG.current];

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
} else {
    window.CONFIG = CONFIG;
}

// Domain setup instructions:
// 1. Purchase domain (e.g., pandaexteriors-portal.com)
// 2. Set up CloudFront distribution
// 3. Configure Route 53 DNS
// 4. Update production config above
// 5. Change current to 'production'