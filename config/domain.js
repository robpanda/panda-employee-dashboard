// Domain Configuration
const DOMAIN_CONFIG = {
    // Production domain
    production: {
        domain: 'pandaadmin.com',
        protocol: 'https',
        api: 'https://api.pandaadmin.com',
        s3bucket: 'pandaadmin-com'
    },
    
    // Development/staging
    development: {
        domain: 'panda-exteriors-map-bucket.s3.amazonaws.com',
        protocol: 'https',
        api: 'https://w40mq6ab11.execute-api.us-east-2.amazonaws.com/prod',
        s3bucket: 'panda-exteriors-map-bucket'
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
// 1. Transfer DNS to Route 53 (see setup commands below)
// 2. Create S3 bucket: pandaadmin-com
// 3. Request SSL certificate in ACM
// 4. Create ALB with SSL certificate
// 5. Update production config above
// 6. Change current to 'production'