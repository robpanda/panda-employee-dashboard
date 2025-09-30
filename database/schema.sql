-- Contacts Table
CREATE TABLE contacts (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20),
    status ENUM('active', 'inactive', 'do-not-contact') DEFAULT 'active',
    lists JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
);

-- Collections Table
CREATE TABLE collections (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    contact_id VARCHAR(36),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    install_date DATE NOT NULL,
    stage ENUM('0-30', '31-60', '61-90', '91-plus', 'judgment', 'resolved') NOT NULL,
    status ENUM('active', 'resolved', 'cancelled') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL,
    INDEX idx_stage (stage),
    INDEX idx_status (status),
    INDEX idx_install_date (install_date),
    INDEX idx_email (email)
);

-- Campaigns Table
CREATE TABLE campaigns (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(255) NOT NULL,
    type ENUM('email', 'sms', 'mixed') NOT NULL,
    stage VARCHAR(20),
    status ENUM('draft', 'active', 'paused', 'completed') DEFAULT 'draft',
    schedule JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Campaign Recipients Table
CREATE TABLE campaign_recipients (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    campaign_id VARCHAR(36) NOT NULL,
    contact_id VARCHAR(36),
    collection_id VARCHAR(36),
    status ENUM('pending', 'sent', 'delivered', 'failed') DEFAULT 'pending',
    sent_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
    FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
);