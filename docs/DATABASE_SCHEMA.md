# Database Schema - EULA Comparison Platform

## Overview

This document defines the database schema for the EULA Comparison Platform, designed to support automated scraping, analysis, and comparison of End User License Agreements (EULAs) and Terms of Service (ToS) documents.

## Database Technology

- **Primary Database**: PostgreSQL 15+
- **Document Storage**: MinIO/S3-compatible for binary files
- **Search Engine**: Elasticsearch for full-text search
- **Time Series**: InfluxDB for analytics (separate schema)
- **Caching**: Redis for session and frequently accessed data

## Schema Design Principles

- **Normalization**: 3NF compliance with selective denormalization for performance
- **Audit Trail**: Complete change tracking for all critical entities
- **Soft Deletes**: Logical deletion with `deleted_at` timestamps
- **UUID Primary Keys**: Distributed-friendly unique identifiers
- **Timestamps**: Created/updated timestamps on all entities
- **Indexing**: Strategic indexing for common query patterns

## Core Tables

### 1. Companies

Stores information about companies whose terms are being tracked.

```sql
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    domain VARCHAR(255) NOT NULL,
    logo_url TEXT,
    website_url TEXT NOT NULL,
    description TEXT,
    headquarters VARCHAR(255),
    founded_year INTEGER,
    employee_count_range VARCHAR(50), -- e.g., "1-10", "11-50", "1000+"
    industry_category VARCHAR(100) NOT NULL,
    stock_symbol VARCHAR(10),
    is_public BOOLEAN DEFAULT FALSE,
    parent_company_id UUID REFERENCES companies(id),
    status VARCHAR(50) DEFAULT 'active', -- active, inactive, merged, acquired
    scraping_priority INTEGER DEFAULT 5, -- 1-10 scale
    scraping_frequency VARCHAR(20) DEFAULT 'weekly', -- daily, weekly, monthly
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_companies_slug ON companies(slug);
CREATE INDEX idx_companies_domain ON companies(domain);
CREATE INDEX idx_companies_industry ON companies(industry_category);
CREATE INDEX idx_companies_status ON companies(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_companies_scraping ON companies(scraping_priority, scraping_frequency) WHERE status = 'active';
```

### 2. Products

Individual products or services offered by companies.

```sql
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    description TEXT,
    product_url TEXT,
    category VARCHAR(100), -- productivity, social-media, cloud-storage, etc.
    pricing_model VARCHAR(50), -- free, freemium, subscription, one-time
    target_audience VARCHAR(100), -- consumer, business, enterprise
    launch_date DATE,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(company_id, slug)
);

CREATE INDEX idx_products_company ON products(company_id);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_status ON products(status) WHERE deleted_at IS NULL;
```

### 3. Documents

Legal documents (EULAs, ToS, Privacy Policies) associated with companies/products.

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    product_id UUID REFERENCES products(id), -- NULL if company-wide
    document_type VARCHAR(50) NOT NULL, -- eula, tos, privacy_policy, cookie_policy
    title VARCHAR(500) NOT NULL,
    source_url TEXT NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    jurisdiction VARCHAR(100), -- legal jurisdiction
    effective_date DATE,
    last_modified DATE,
    version_identifier VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active', -- active, superseded, archived
    file_path TEXT, -- path to stored document file
    file_size BIGINT,
    file_hash VARCHAR(64), -- SHA-256 hash for change detection
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_documents_company ON documents(company_id);
CREATE INDEX idx_documents_product ON documents(product_id);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_status ON documents(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_documents_hash ON documents(file_hash);
CREATE INDEX idx_documents_effective ON documents(effective_date);
```

### 4. Document Versions

Historical versions of documents for change tracking.

```sql
CREATE TABLE document_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id),
    version_number INTEGER NOT NULL,
    content TEXT NOT NULL, -- extracted text content
    raw_content TEXT, -- original HTML/formatted content
    content_hash VARCHAR(64) NOT NULL, -- SHA-256 of content
    word_count INTEGER,
    character_count INTEGER,
    file_path TEXT, -- path to version-specific file
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(document_id, version_number)
);

CREATE INDEX idx_document_versions_document ON document_versions(document_id);
CREATE INDEX idx_document_versions_hash ON document_versions(content_hash);
CREATE INDEX idx_document_versions_extracted ON document_versions(extracted_at);
```

### 5. Document Analysis

Analysis results for document versions.

```sql
CREATE TABLE document_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_version_id UUID NOT NULL REFERENCES document_versions(id),
    overall_score DECIMAL(4,2) NOT NULL, -- 0.00 to 10.00 (consumer-friendliness)
    complexity_score DECIMAL(4,2), -- readability/complexity metrics
    readability_score DECIMAL(4,2), -- Flesch-Kincaid or similar
    sentiment_score DECIMAL(4,2), -- -1.00 to 1.00
    confidence_level DECIMAL(3,2), -- 0.00 to 1.00
    analysis_version VARCHAR(20) NOT NULL, -- version of analysis algorithm
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(document_version_id, analysis_version)
);

CREATE INDEX idx_analysis_version ON document_analysis(document_version_id);
CREATE INDEX idx_analysis_score ON document_analysis(overall_score);
CREATE INDEX idx_analysis_date ON document_analysis(analyzed_at);
```

### 6. Clauses

Individual clauses or sections identified within documents.

```sql
CREATE TABLE clauses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_version_id UUID NOT NULL REFERENCES document_versions(id),
    clause_type VARCHAR(100) NOT NULL, -- arbitration, liability, data_collection, etc.
    title VARCHAR(500),
    content TEXT NOT NULL,
    section_number VARCHAR(50),
    start_position INTEGER, -- character position in document
    end_position INTEGER,
    severity_score DECIMAL(4,2), -- 0.00 to 10.00 (how problematic)
    confidence_score DECIMAL(3,2), -- 0.00 to 1.00 (classification confidence)
    is_problematic BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_clauses_document_version ON clauses(document_version_id);
CREATE INDEX idx_clauses_type ON clauses(clause_type);
CREATE INDEX idx_clauses_problematic ON clauses(is_problematic);
CREATE INDEX idx_clauses_severity ON clauses(severity_score);
```

### 7. Clause Types

Reference table for standardized clause classifications.

```sql
CREATE TABLE clause_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    category VARCHAR(50), -- rights, obligations, limitations, etc.
    default_weight DECIMAL(3,2) DEFAULT 1.00, -- weight in overall scoring
    is_problematic_indicator BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add foreign key constraint to clauses table
ALTER TABLE clauses ADD CONSTRAINT fk_clauses_type 
    FOREIGN KEY (clause_type) REFERENCES clause_types(name);
```

### 8. Users

User accounts and profiles.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255), -- bcrypt hash
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    organization VARCHAR(255),
    user_type VARCHAR(50) DEFAULT 'individual', -- individual, researcher, journalist, advocate
    account_tier VARCHAR(50) DEFAULT 'free', -- free, researcher, premium
    email_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP WITH TIME ZONE,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_type ON users(user_type);
CREATE INDEX idx_users_active ON users(is_active) WHERE deleted_at IS NULL;
```

### 9. User Watchlists

Companies/products users want to monitor.

```sql
CREATE TABLE user_watchlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    company_id UUID REFERENCES companies(id),
    product_id UUID REFERENCES products(id),
    notification_preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT watchlist_target CHECK (
        (company_id IS NOT NULL AND product_id IS NULL) OR
        (company_id IS NULL AND product_id IS NOT NULL)
    ),
    UNIQUE(user_id, company_id, product_id)
);

CREATE INDEX idx_watchlists_user ON user_watchlists(user_id);
CREATE INDEX idx_watchlists_company ON user_watchlists(company_id);
CREATE INDEX idx_watchlists_product ON user_watchlists(product_id);
```

### 10. Comparisons

Saved comparison sessions by users.

```sql
CREATE TABLE comparisons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id), -- NULL for anonymous
    title VARCHAR(255),
    description TEXT,
    comparison_data JSONB NOT NULL, -- stores comparison configuration
    is_public BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_comparisons_user ON comparisons(user_id);
CREATE INDEX idx_comparisons_public ON comparisons(is_public, created_at) WHERE deleted_at IS NULL;
```

### 11. API Keys

API access credentials for external integrations.

```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    key_hash VARCHAR(255) UNIQUE NOT NULL, -- hashed API key
    key_prefix VARCHAR(20) NOT NULL, -- first few chars for identification
    name VARCHAR(255) NOT NULL,
    permissions JSONB DEFAULT '{}', -- scoped permissions
    rate_limit_per_hour INTEGER DEFAULT 1000,
    usage_count BIGINT DEFAULT 0,
    last_used TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_user ON api_keys(user_id);
CREATE INDEX idx_api_keys_active ON api_keys(is_active, expires_at);
```

## Supporting Tables

### 12. Scraping Jobs

Tracks scraping activities and schedules.

```sql
CREATE TABLE scraping_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    job_type VARCHAR(50) NOT NULL, -- scheduled, manual, retry
    status VARCHAR(50) DEFAULT 'pending', -- pending, running, completed, failed
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    documents_found INTEGER DEFAULT 0,
    documents_updated INTEGER DEFAULT 0,
    documents_new INTEGER DEFAULT 0,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_scraping_jobs_company ON scraping_jobs(company_id);
CREATE INDEX idx_scraping_jobs_status ON scraping_jobs(status, created_at);
CREATE INDEX idx_scraping_jobs_retry ON scraping_jobs(next_retry_at) WHERE status = 'failed';
```

### 13. Change Notifications

Tracks notifications sent to users about changes.

```sql
CREATE TABLE change_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    document_id UUID NOT NULL REFERENCES documents(id),
    notification_type VARCHAR(50) NOT NULL, -- email, sms, push
    change_type VARCHAR(50) NOT NULL, -- new_version, score_change, new_document
    subject VARCHAR(255),
    content TEXT,
    sent_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'pending', -- pending, sent, failed
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON change_notifications(user_id);
CREATE INDEX idx_notifications_status ON change_notifications(status, created_at);
CREATE INDEX idx_notifications_document ON change_notifications(document_id);
```

### 14. Audit Log

Comprehensive audit trail for all significant actions.

```sql
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id), -- NULL for system actions
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL, -- table name
    entity_id UUID NOT NULL,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_action ON audit_log(action, created_at);
```

## Views and Derived Tables

### Company Scores View

```sql
CREATE VIEW company_scores AS
SELECT 
    c.id,
    c.name,
    c.slug,
    c.industry_category,
    AVG(da.overall_score) as average_score,
    MIN(da.overall_score) as worst_score,
    MAX(da.overall_score) as best_score,
    COUNT(DISTINCT d.id) as document_count,
    MAX(da.analyzed_at) as last_analysis
FROM companies c
JOIN documents d ON c.id = d.company_id
JOIN document_versions dv ON d.id = dv.document_id
JOIN document_analysis da ON dv.id = da.document_version_id
WHERE c.deleted_at IS NULL 
    AND d.status = 'active'
    AND d.deleted_at IS NULL
GROUP BY c.id, c.name, c.slug, c.industry_category;
```

### Recent Changes View

```sql
CREATE VIEW recent_changes AS
SELECT 
    c.name as company_name,
    d.document_type,
    d.title,
    dv.version_number,
    dv.extracted_at,
    da.overall_score,
    LAG(da.overall_score) OVER (
        PARTITION BY d.id 
        ORDER BY dv.version_number
    ) as previous_score
FROM companies c
JOIN documents d ON c.id = d.company_id
JOIN document_versions dv ON d.id = dv.document_id
JOIN document_analysis da ON dv.id = da.document_version_id
WHERE dv.extracted_at >= NOW() - INTERVAL '30 days'
ORDER BY dv.extracted_at DESC;
```

## Indexes Strategy

### Performance Indexes

```sql
-- Composite indexes for common query patterns
CREATE INDEX idx_documents_company_type ON documents(company_id, document_type, status);
CREATE INDEX idx_analysis_score_date ON document_analysis(overall_score, analyzed_at);
CREATE INDEX idx_clauses_type_problematic ON clauses(clause_type, is_problematic, severity_score);
CREATE INDEX idx_versions_document_date ON document_versions(document_id, extracted_at DESC);

-- Full-text search indexes (if not using Elasticsearch)
CREATE INDEX idx_documents_title_fts ON documents USING gin(to_tsvector('english', title));
CREATE INDEX idx_clauses_content_fts ON clauses USING gin(to_tsvector('english', content));

-- Partial indexes for active records
CREATE INDEX idx_companies_active ON companies(industry_category, created_at) 
    WHERE status = 'active' AND deleted_at IS NULL;
CREATE INDEX idx_users_active_tier ON users(account_tier, created_at) 
    WHERE is_active = TRUE AND deleted_at IS NULL;
```

## Data Retention Policies

### Automated Cleanup

```sql
-- Function to clean up old document versions (keep last 10 per document)
CREATE OR REPLACE FUNCTION cleanup_old_document_versions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
BEGIN
    WITH versions_to_delete AS (
        SELECT id
        FROM (
            SELECT id,
                   ROW_NUMBER() OVER (
                       PARTITION BY document_id 
                       ORDER BY version_number DESC
                   ) as rn
            FROM document_versions
        ) ranked
        WHERE rn > 10
    )
    DELETE FROM document_versions 
    WHERE id IN (SELECT id FROM versions_to_delete);
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to archive old audit log entries
CREATE OR REPLACE FUNCTION archive_old_audit_logs()
RETURNS INTEGER AS $$
DECLARE
    archived_count INTEGER := 0;
BEGIN
    -- Move records older than 2 years to archive table
    INSERT INTO audit_log_archive 
    SELECT * FROM audit_log 
    WHERE created_at < NOW() - INTERVAL '2 years';
    
    GET DIAGNOSTICS archived_count = ROW_COUNT;
    
    DELETE FROM audit_log 
    WHERE created_at < NOW() - INTERVAL '2 years';
    
    RETURN archived_count;
END;
$$ LANGUAGE plpgsql;
```

## Security Considerations

### Row Level Security

```sql
-- Enable RLS on sensitive tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_watchlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE comparisons ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;

-- Users can only access their own data
CREATE POLICY user_own_data ON users
    FOR ALL TO authenticated_users
    USING (id = current_user_id());

CREATE POLICY watchlist_own_data ON user_watchlists
    FOR ALL TO authenticated_users
    USING (user_id = current_user_id());
```

### Sensitive Data Encryption

```sql
-- Extension for encryption
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt sensitive user data
ALTER TABLE users ADD COLUMN encrypted_data BYTEA;

-- Function to encrypt/decrypt sensitive data
CREATE OR REPLACE FUNCTION encrypt_sensitive_data(data TEXT)
RETURNS BYTEA AS $$
BEGIN
    RETURN pgp_sym_encrypt(data, current_setting('app.encryption_key'));
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

## Migration Strategy

### Version Control

Each schema change is versioned with migration files:

```
migrations/
├── 001_initial_schema.sql
├── 002_add_user_preferences.sql
├── 003_add_api_keys.sql
├── 004_add_audit_logging.sql
└── ...
```

### Deployment Process

1. **Backup**: Always backup before migrations
2. **Validation**: Run migrations on staging first
3. **Rollback Plan**: Prepare rollback scripts
4. **Monitoring**: Monitor performance after deployment

## Performance Considerations

### Query Optimization

- Use appropriate indexes for common query patterns
- Partition large tables (audit_log, document_versions) by date
- Use materialized views for complex aggregations
- Implement connection pooling (PgBouncer)

### Scaling Strategy

- **Read Replicas**: For analytics and reporting queries
- **Horizontal Partitioning**: For time-series data (audit logs, metrics)
- **Caching**: Redis for frequently accessed data
- **Archive Strategy**: Move old data to separate archive tables

## Monitoring and Maintenance

### Health Checks

```sql
-- Query to monitor table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Query to monitor index usage
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;
```

### Maintenance Tasks

- **VACUUM ANALYZE**: Weekly on all tables
- **REINDEX**: Monthly on heavily updated indexes
- **Statistics Update**: After bulk data loads
- **Backup Verification**: Daily backup integrity checks

This schema provides a robust foundation for the EULA Comparison Platform, supporting scalability, data integrity, and comprehensive audit trails while maintaining performance for the expected query patterns.