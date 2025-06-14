# API Specification - EULA Comparison Platform

## Overview

The EULA Comparison Platform API provides programmatic access to company terms analysis, comparisons, and monitoring capabilities. This RESTful API follows OpenAPI 3.0 standards and supports multiple authentication methods for different user tiers.

## Base Configuration

### Base URLs
- **Production**: `https://api.tosboss.com/v1`
- **Staging**: `https://staging-api.tosboss.com/v1`
- **Development**: `http://localhost:8000/api/v1`

### Content Types
- **Request**: `application/json`
- **Response**: `application/json`
- **Bulk Export**: `application/json`, `text/csv`, `application/vnd.ms-excel`

### Rate Limiting
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
Retry-After: 60
```

## Authentication

### API Key Authentication
```http
Authorization: Bearer your-api-key-here
```

### OAuth 2.0 Flow
```http
Authorization: Bearer your-oauth-token-here
```

### User Tiers and Limits

| Tier | Rate Limit | Features |
|------|------------|----------|
| **Free** | 100 req/hour | Basic company data, simple comparisons |
| **Researcher** | 1,000 req/hour | Bulk exports, historical data, webhooks |
| **Commercial** | 10,000 req/hour | Full API access, priority support |
| **Enterprise** | Custom | White-label, custom integrations |

## Core Data Models

### Company Model
```json
{
  "id": "uuid",
  "name": "string",
  "slug": "string",
  "domain": "string",
  "industry": "string",
  "headquarters": "string",
  "logo_url": "string",
  "founded_year": "integer",
  "employee_count": "integer",
  "market_cap": "integer",
  "is_public": "boolean",
  "stock_symbol": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "last_scraped": "datetime",
  "scraping_status": "enum[active, paused, failed, blocked]",
  "documents": ["Document"],
  "overall_score": "Score",
  "category_scores": {"string": "Score"}
}
```

### Document Model
```json
{
  "id": "uuid",
  "company_id": "uuid",
  "type": "enum[terms_of_service, privacy_policy, eula, acceptable_use, cookie_policy, other]",
  "title": "string",
  "url": "string",
  "content": "string",
  "content_hash": "string",
  "word_count": "integer",
  "reading_time_minutes": "integer",
  "effective_date": "date",
  "last_modified": "datetime",
  "version": "integer",
  "language": "string",
  "jurisdiction": "string",
  "is_current": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime",
  "analysis": "DocumentAnalysis",
  "clauses": ["Clause"]
}
```

### Score Model
```json
{
  "overall_score": "float[0-100]",
  "consumer_friendliness": "float[0-100]",
  "transparency": "float[0-100]",
  "data_protection": "float[0-100]",
  "user_rights": "float[0-100]",
  "liability_fairness": "float[0-100]",
  "termination_fairness": "float[0-100]",
  "dispute_resolution": "float[0-100]",
  "modification_notice": "float[0-100]",
  "readability": "float[0-100]",
  "confidence_level": "float[0-1]",
  "last_calculated": "datetime",
  "methodology_version": "string"
}
```

### Clause Model
```json
{
  "id": "uuid",
  "document_id": "uuid",
  "type": "enum[arbitration, liability, data_collection, termination, modification, jurisdiction, other]",
  "title": "string",
  "content": "string",
  "section": "string",
  "severity": "enum[low, medium, high, critical]",
  "consumer_impact": "string",
  "explanation": "string",
  "alternatives": "string",
  "position_start": "integer",
  "position_end": "integer",
  "flagged_terms": ["string"],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Comparison Model
```json
{
  "id": "uuid",
  "title": "string",
  "companies": ["uuid"],
  "criteria": ["string"],
  "results": {
    "company_id": {
      "scores": "Score",
      "advantages": ["string"],
      "disadvantages": ["string"],
      "unique_features": ["string"],
      "risk_factors": ["string"]
    }
  },
  "summary": "string",
  "recommendation": "string",
  "created_at": "datetime",
  "expires_at": "datetime"
}
```

### Change Model
```json
{
  "id": "uuid",
  "document_id": "uuid",
  "change_type": "enum[addition, deletion, modification, restructure]",
  "section": "string",
  "old_content": "string",
  "new_content": "string",
  "impact_level": "enum[minor, moderate, significant, major]",
  "summary": "string",
  "consumer_impact": "string",
  "detected_at": "datetime",
  "effective_date": "date",
  "notification_sent": "boolean"
}
```

## API Endpoints

### Companies

#### List Companies
```http
GET /companies
```

**Parameters:**
- `page` (integer): Page number (default: 1)
- `limit` (integer): Results per page (1-100, default: 20)
- `industry` (string): Filter by industry
- `min_score` (float): Minimum overall score (0-100)
- `max_score` (float): Maximum overall score (0-100)
- `search` (string): Search company names
- `sort` (enum): Sort by [name, score, updated_at, founded_year]
- `order` (enum): Order [asc, desc]
- `has_recent_changes` (boolean): Companies with changes in last 30 days

**Response:**
```json
{
  "data": ["Company"],
  "pagination": {
    "current_page": 1,
    "per_page": 20,
    "total": 1500,
    "total_pages": 75,
    "has_next": true,
    "has_prev": false
  },
  "filters": {
    "applied": {"industry": "social_media"},
    "available": {
      "industries": ["social_media", "cloud_storage", "productivity"],
      "score_range": {"min": 15.5, "max": 89.2}
    }
  }
}
```

#### Get Company Details
```http
GET /companies/{company_id}
```

**Parameters:**
- `include` (array): Additional data [documents, analysis, changes, competitors]

**Response:**
```json
{
  "data": "Company",
  "related": {
    "competitors": ["Company"],
    "industry_average": "Score",
    "recent_changes": ["Change"],
    "trending_concerns": ["string"]
  }
}
```

#### Get Company Documents
```http
GET /companies/{company_id}/documents
```

**Parameters:**
- `type` (enum): Filter by document type
- `current_only` (boolean): Only current versions (default: true)
- `include_analysis` (boolean): Include analysis data

#### Get Company Score History
```http
GET /companies/{company_id}/score-history
```

**Parameters:**
- `period` (enum): Time period [week, month, quarter, year, all]
- `granularity` (enum): Data points [daily, weekly, monthly]

### Documents

#### Get Document Details
```http
GET /documents/{document_id}
```

**Parameters:**
- `include` (array): Additional data [analysis, clauses, changes, full_content]
- `version` (integer): Specific version (default: latest)

#### Get Document Analysis
```http
GET /documents/{document_id}/analysis
```

**Response:**
```json
{
  "data": {
    "scores": "Score",
    "problematic_clauses": ["Clause"],
    "readability_metrics": {
      "flesch_kincaid_grade": 16.2,
      "average_sentence_length": 28.5,
      "complex_words_percentage": 0.23,
      "legal_jargon_density": 0.18
    },
    "key_findings": ["string"],
    "compliance_flags": {
      "gdpr_compliant": true,
      "ccpa_compliant": false,
      "coppa_concerns": true
    },
    "recommendation": "string"
  }
}
```

#### Get Document Changes
```http
GET /documents/{document_id}/changes
```

**Parameters:**
- `since` (datetime): Changes since timestamp
- `impact_level` (enum): Minimum impact level
- `limit` (integer): Maximum changes to return

### Comparisons

#### Create Comparison
```http
POST /comparisons
```

**Request Body:**
```json
{
  "title": "Social Media Platforms Privacy Comparison",
  "company_ids": ["uuid1", "uuid2", "uuid3"],
  "criteria": ["data_protection", "user_rights", "transparency"],
  "weights": {
    "data_protection": 0.4,
    "user_rights": 0.3,
    "transparency": 0.3
  },
  "include_alternatives": true,
  "format": "detailed"
}
```

**Response:**
```json
{
  "data": "Comparison",
  "export_urls": {
    "pdf": "https://api.tosboss.com/exports/comparisons/{id}.pdf",
    "csv": "https://api.tosboss.com/exports/comparisons/{id}.csv"
  }
}
```

#### Get Comparison Results
```http
GET /comparisons/{comparison_id}
```

#### List User Comparisons
```http
GET /users/me/comparisons
```

### Search and Discovery

#### Global Search
```http
GET /search
```

**Parameters:**
- `q` (string): Search query
- `type` (enum): Search type [companies, documents, clauses, all]
- `filters` (object): Advanced filters
- `highlight` (boolean): Highlight matching terms

**Response:**
```json
{
  "data": {
    "companies": ["Company"],
    "documents": ["Document"],
    "clauses": ["Clause"]
  },
  "suggestions": ["string"],
  "facets": {
    "industries": {"social_media": 45, "cloud_storage": 23},
    "document_types": {"privacy_policy": 67, "terms_of_service": 89}
  },
  "query_time_ms": 127
}
```

#### Get Trending Topics
```http
GET /trending
```

**Parameters:**
- `period` (enum): Time period [day, week, month]
- `category` (enum): Trend category [changes, searches, concerns]

### Analytics and Insights

#### Industry Analytics
```http
GET /analytics/industries/{industry}
```

**Response:**
```json
{
  "data": {
    "industry": "social_media",
    "company_count": 25,
    "average_scores": "Score",
    "trends": {
      "improving": ["Company"],
      "declining": ["Company"],
      "stable": ["Company"]
    },
    "common_issues": [
      {
        "issue": "Broad data collection",
        "prevalence": 0.84,
        "severity": "high",
        "trend": "increasing"
      }
    ],
    "best_practices": ["string"],
    "regulatory_impact": "string"
  }
}
```

#### Score Distribution
```http
GET /analytics/score-distribution
```

**Parameters:**
- `industry` (string): Filter by industry
- `document_type` (enum): Filter by document type
- `bins` (integer): Number of score bins (default: 10)

#### Change Timeline
```http
GET /analytics/changes/timeline
```

**Parameters:**
- `company_ids` (array): Specific companies
- `start_date` (date): Timeline start
- `end_date` (date): Timeline end
- `impact_level` (enum): Minimum impact level

### User Management

#### Get User Profile
```http
GET /users/me
```

**Response:**
```json
{
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "tier": "researcher",
    "created_at": "datetime",
    "usage": {
      "requests_this_month": 450,
      "requests_limit": 1000,
      "comparisons_created": 12,
      "watchlist_count": 8
    },
    "preferences": {
      "notification_email": true,
      "newsletter": false,
      "score_weights": {"data_protection": 0.3}
    }
  }
}
```

#### Update User Preferences
```http
PATCH /users/me/preferences
```

#### Get User Watchlist
```http
GET /users/me/watchlist
```

#### Add to Watchlist
```http
POST /users/me/watchlist
```

**Request Body:**
```json
{
  "company_id": "uuid",
  "alert_threshold": "significant",
  "notification_methods": ["email", "webhook"]
}
```

### Notifications and Alerts

#### List User Alerts
```http
GET /users/me/alerts
```

**Parameters:**
- `status` (enum): Filter by status [unread, read, archived]
- `type` (enum): Alert type [change_detected, score_updated, new_company]
- `since` (datetime): Alerts since timestamp

#### Mark Alerts as Read
```http
PATCH /users/me/alerts/mark-read
```

**Request Body:**
```json
{
  "alert_ids": ["uuid1", "uuid2"],
  "mark_all": false
}
```

#### Configure Webhooks
```http
POST /users/me/webhooks
```

**Request Body:**
```json
{
  "url": "https://your-server.com/webhook",
  "events": ["document.changed", "score.updated"],
  "secret": "your-webhook-secret",
  "active": true
}
```

### Export and Bulk Operations

#### Export Company Data
```http
GET /export/companies
```

**Parameters:**
- `format` (enum): Export format [json, csv, xlsx]
- `company_ids` (array): Specific companies
- `include_documents` (boolean): Include document content
- `date_range` (object): {"start": "date", "end": "date"}

**Response:**
```json
{
  "export_id": "uuid",
  "status": "processing",
  "download_url": null,
  "expires_at": "datetime",
  "estimated_completion": "datetime"
}
```

#### Get Export Status
```http
GET /exports/{export_id}/status
```

#### Bulk Document Analysis
```http
POST /bulk/analyze-documents
```

**Request Body:**
```json
{
  "urls": ["https://example.com/terms", "https://example.com/privacy"],
  "analysis_types": ["scoring", "clause_detection", "readability"],
  "callback_url": "https://your-server.com/callback"
}
```

### Administrative Endpoints

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "datetime",
  "version": "1.2.0",
  "services": {
    "database": "healthy",
    "elasticsearch": "healthy",
    "redis": "healthy",
    "scraping_queue": "healthy"
  },
  "metrics": {
    "response_time_ms": 45,
    "active_scrapers": 12,
    "queue_size": 234
  }
}
```

#### API Statistics
```http
GET /admin/stats
```

**Requires:** Admin authentication

## Webhook Events

### Event Types

#### document.changed
```json
{
  "event": "document.changed",
  "timestamp": "datetime",
  "data": {
    "document": "Document",
    "changes": ["Change"],
    "impact_summary": "string"
  }
}
```

#### score.updated
```json
{
  "event": "score.updated",
  "timestamp": "datetime",
  "data": {
    "company": "Company",
    "old_score": "Score",
    "new_score": "Score",
    "change_reason": "string"
  }
}
```

#### company.added
```json
{
  "event": "company.added",
  "timestamp": "datetime",
  "data": {
    "company": "Company",
    "initial_analysis": "DocumentAnalysis"
  }
}
```

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "company_id",
      "issue": "must be a valid UUID"
    },
    "request_id": "req_12345",
    "timestamp": "datetime"
  }
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `INVALID_API_KEY` | 401 | API key is missing or invalid |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `COMPANY_NOT_FOUND` | 404 | Company does not exist |
| `DOCUMENT_NOT_FOUND` | 404 | Document does not exist |
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `INSUFFICIENT_PERMISSIONS` | 403 | Operation not allowed for user tier |
| `EXPORT_FAILED` | 500 | Export generation failed |
| `ANALYSIS_TIMEOUT` | 502 | Document analysis timed out |
| `SCRAPING_BLOCKED` | 503 | Website blocked our scraper |

## SDK and Libraries

### Official SDKs

#### Python SDK
```python
from tosboss import TOSBossClient

client = TOSBossClient(api_key="your-key")
companies = client.companies.list(industry="social_media")
comparison = client.comparisons.create([
    "facebook-uuid", 
    "twitter-uuid"
])
```

#### JavaScript SDK
```javascript
import { TOSBossClient } from '@tosboss/sdk';

const client = new TOSBossClient({ apiKey: 'your-key' });
const companies = await client.companies.list({ industry: 'social_media' });
const comparison = await client.comparisons.create({
  companyIds: ['facebook-uuid', 'twitter-uuid']
});
```

#### cURL Examples
```bash
# Get company list
curl -H "Authorization: Bearer your-api-key" \
     "https://api.tosboss.com/v1/companies?industry=social_media"

# Create comparison
curl -X POST \
     -H "Authorization: Bearer your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"company_ids":["uuid1","uuid2"],"criteria":["data_protection"]}' \
     "https://api.tosboss.com/v1/comparisons"
```

## Integration Examples

### Browser Extension Integration
```javascript
// Check if current site has analysis
fetch(`https://api.tosboss.com/v1/companies/by-domain/${window.location.hostname}`)
  .then(response => response.json())
  .then(data => {
    if (data.data) {
      showTermsWarning(data.data.overall_score);
    }
  });
```

### Webhook Handler Example
```python
import hmac
import hashlib
from flask import Flask, request

def verify_webhook(payload, signature, secret):
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    if verify_webhook(request.data, request.headers.get('X-Signature'), WEBHOOK_SECRET):
        event = request.json
        if event['event'] == 'document.changed':
            notify_users_of_change(event['data'])
    return 'OK'
```

## Rate Limiting Details

### Algorithms
- **Token Bucket**: Allows bursts up to limit
- **Sliding Window**: Smooth rate enforcement
- **Per-Endpoint**: Different limits for different operations

### Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1640995200
X-RateLimit-Policy: 1000;w=3600
```

### Handling Rate Limits
```python
import time
import requests

def api_call_with_retry(url, headers):
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            time.sleep(retry_after)
            continue
        return response
```

## Testing and Development

### Test Environment
- **Base URL**: `https://staging-api.tosboss.com/v1`
- **Test API Keys**: Contact support for test credentials
- **Sample Data**: Pre-populated with major companies
- **Webhook Testing**: Use tools like ngrok for local development

### API Client Testing
```python
import pytest
from tosboss import TOSBossClient

@pytest.fixture
def client():
    return TOSBossClient(api_key="test-key", base_url="https://staging-api.tosboss.com/v1")

def test_company_list(client):
    companies = client.companies.list(limit=5)
    assert len(companies.data) <= 5
    assert all(c.id for c in companies.data)
```

## Versioning and Deprecation

### Version Strategy
- **Semantic Versioning**: Major.Minor.Patch
- **Backward Compatibility**: Maintained within major versions
- **Deprecation Timeline**: 12 months notice for breaking changes
- **Multiple Versions**: Up to 2 major versions supported simultaneously

### Migration Guides
- Detailed migration documentation for version upgrades
- Code examples showing before/after API usage
- Timeline for deprecated feature removal
- Support for automated migration tools

This comprehensive API specification provides developers with everything needed to integrate with the EULA Comparison Platform, from basic company lookups to complex analysis workflows and real-time change monitoring.