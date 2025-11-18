# AI Stock Research Platform - Microservice Architecture Specification

**Version**: 1.0
**Date**: 2025-11-10
**Status**: DRAFT
**Architecture**: Event-Driven Microservices

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Microservice Catalog](#microservice-catalog)
4. [Data Architecture](#data-architecture)
5. [API Specifications](#api-specifications)
6. [Infrastructure Architecture](#infrastructure-architecture)
7. [Security Architecture](#security-architecture)
8. [Deployment Architecture](#deployment-architecture)
9. [Integration Patterns](#integration-patterns)
10. [Monitoring & Observability](#monitoring--observability)

---

## Executive Summary

### Vision
Transform the monolithic AI Stock Research Tool into a scalable, event-driven microservice platform capable of processing real-time market data, performing advanced analytics, and serving 10,000+ concurrent users across global markets.

### Architecture Principles
1. **Single Responsibility**: Each service owns one bounded context
2. **API-First**: OpenAPI-defined contracts before implementation
3. **Event-Driven**: Asynchronous communication for scalability
4. **Cloud-Native**: Kubernetes-orchestrated, horizontally scalable
5. **Resilient**: Circuit breakers, retries, fallbacks, graceful degradation
6. **Observable**: Structured logging, metrics, distributed tracing
7. **Secure**: Zero-trust, encryption everywhere, least privilege

### Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Programming** | Python 3.11+ | Ecosystem, libraries, team expertise |
| **API Framework** | FastAPI | Async, OpenAPI, performance |
| **Message Queue** | RabbitMQ / Kafka | Reliability, persistence, ordering |
| **Cache** | Redis | Speed, data structures, pub/sub |
| **Database (SQL)** | PostgreSQL | ACID, JSON support, extensions |
| **Database (NoSQL)** | MongoDB | Flexible schema, time-series |
| **Search** | Elasticsearch | Full-text, analytics, aggregations |
| **Container** | Docker | Portability, consistency |
| **Orchestration** | Kubernetes | Scaling, self-healing, ecosystem |
| **Service Mesh** | Istio (optional) | Traffic mgmt, security, observability |
| **Monitoring** | Prometheus + Grafana | Industry standard, powerful |
| **Tracing** | Jaeger / Tempo | Distributed tracing, debugging |
| **Logging** | ELK Stack | Centralized, searchable, visual |
| **CI/CD** | GitHub Actions | Integration, automation |
| **Cloud** | AWS (primary) | Mature, global, services |

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Client Layer                                │
│  Web App │ Mobile App │ Trading Platform │ Excel Plugin │ API SDK   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                      API Gateway (Kong / NGINX)                      │
│           Authentication │ Rate Limiting │ Load Balancing            │
└────────┬─────────┬────────┬─────────┬────────┬────────┬─────────────┘
         │         │        │         │        │        │
    ┌────▼───┐ ┌──▼────┐ ┌─▼──────┐ ┌▼──────┐ ┌▼─────┐ ┌▼───────┐
    │ Market │ │ News  │ │Finance │ │ Alert │ │ User │ │Predict │
    │ Data   │ │Service│ │ Svc    │ │ Svc   │ │ Svc  │ │ Svc    │
    └────┬───┘ └──┬────┘ └─┬──────┘ └┬──────┘ └┬─────┘ └┬───────┘
         │        │        │         │        │        │
    ┌────▼────────▼────────▼─────────▼────────▼────────▼───────────┐
    │              Message Bus (RabbitMQ / Kafka)                    │
    │   Topics: market.quotes | news.articles | alerts.triggers     │
    └────────────────────────────────────────────────────────────────┘
         │        │        │         │        │        │
    ┌────▼───┐ ┌─▼─────┐ ┌▼──────┐ ┌▼──────┐ ┌▼─────┐ ┌▼───────┐
    │  Data  │ │ Event │ │ ML    │ │Search │ │Cache │ │Metrics │
    │Ingestion│ │Process│ │Engine │ │Index  │ │Redis │ │  Svc   │
    └────┬───┘ └──┬────┘ └┬──────┘ └┬──────┘ └┬─────┘ └┬───────┘
         │        │        │         │        │        │
    ┌────▼────────▼────────▼─────────▼────────▼────────▼───────────┐
    │                   Data Layer                                   │
    │ PostgreSQL │ MongoDB │ Elasticsearch │ Redis │ S3 │ TimescaleDB│
    └────────────────────────────────────────────────────────────────┘
```

### Service Communication Patterns

1. **Synchronous**: REST/gRPC for request-response (API Gateway → Services)
2. **Asynchronous**: Message queue for events (Service → Service)
3. **Streaming**: WebSocket for real-time data (Service → Client)
4. **Batch**: Scheduled jobs for analytics (Cron → Service)

---

## Microservice Catalog

### 1. API Gateway Service
**Purpose**: Single entry point for all client requests

**Responsibilities**:
- Request routing to backend services
- Authentication and authorization (JWT validation)
- Rate limiting (per user/IP/tenant)
- Request/response transformation
- SSL termination
- API versioning
- CORS handling
- Request logging and metrics

**Technology**: Kong Gateway or NGINX Plus or AWS API Gateway

**Endpoints**:
- `/v1/*` - API v1 routes
- `/health` - Health check
- `/metrics` - Prometheus metrics

**Scaling**: Auto-scale 2-10 instances based on RPS

---

### 2. Market Data Service
**Purpose**: Aggregate and serve market data from multiple providers

**Responsibilities**:
- Real-time quote retrieval
- Historical data queries
- Multi-provider failover (Polygon → YFinance → Alpha Vantage)
- Data normalization and validation
- Rate limit management per provider
- Data quality monitoring
- Cache management (Redis)

**Technology**: FastAPI + asyncio + aiohttp

**Database**:
- **TimescaleDB** (time-series for OHLCV)
- **Redis** (cache for quotes, 5-min TTL)

**Endpoints**:
```python
GET  /v1/quotes/{ticker}              # Single quote
GET  /v1/quotes?tickers=NVDA,MSFT     # Batch quotes
GET  /v1/historical/{ticker}          # Historical data
GET  /v1/market-status                # Market open/closed
WS   /v1/stream/quotes                # Real-time stream
```

**Events Published**:
- `market.quote.updated` - When quote is fetched
- `market.status.changed` - Market open/close
- `market.anomaly.detected` - Unusual activity

**Scaling**: Auto-scale 5-20 instances based on request rate

**Performance**:
- Quote latency: <100ms P95
- Batch quotes: <500ms for 50 tickers
- Cache hit rate: >70%

---

### 3. News & Sentiment Service
**Purpose**: Ingest, process, and analyze financial news

**Responsibilities**:
- News ingestion from 50+ sources (APIs, RSS, web scraping)
- Duplicate detection (content hashing)
- Entity extraction (companies, people, products)
- Sentiment analysis (BERT-based model)
- Event classification (earnings, M&A, product launch, etc.)
- Multi-language support (English, Chinese, Japanese)
- News search and filtering

**Technology**: FastAPI + Celery + Transformers (HuggingFace)

**Database**:
- **MongoDB** (news articles, flexible schema)
- **Elasticsearch** (full-text search, aggregations)
- **Redis** (recent articles cache)

**ML Models**:
- **Sentiment**: FinBERT (fine-tuned BERT for financial text)
- **NER**: spaCy with custom financial entity model
- **Classification**: Multi-label classifier for event types

**Endpoints**:
```python
GET  /v1/news?ticker={ticker}&limit=10    # Get news for ticker
GET  /v1/news/search?q={query}            # Full-text search
GET  /v1/news/{news_id}                   # Get article details
GET  /v1/news/{news_id}/sentiment         # Sentiment analysis
WS   /v1/stream/news                      # Real-time news stream
```

**Events Published**:
- `news.article.published` - New article ingested
- `news.sentiment.analyzed` - Sentiment score available
- `news.event.detected` - Important event identified

**Background Jobs**:
- News ingestion: Every 60 seconds
- Sentiment analysis: On article publish
- Index cleanup: Daily

**Scaling**: Auto-scale 3-15 instances

**Performance**:
- News latency: <30s from publication
- Sentiment inference: <100ms per article
- Search latency: <200ms P95

---

### 4. Financial Analysis Service
**Purpose**: Calculate financial metrics and perform fundamental analysis

**Responsibilities**:
- Financial statement retrieval (IS, BS, CF)
- Ratio calculations (P/E, P/S, ROE, ROA, debt ratios, etc.)
- Growth metrics (YoY, QoQ revenue, earnings, margins)
- Peer comparison and sector benchmarking
- Valuation models (DCF, multiples, dividend discount)
- Technical indicators (RSI, MACD, SMA, EMA, Bollinger Bands)

**Technology**: FastAPI + Pandas + NumPy + TA-Lib

**Database**:
- **PostgreSQL** (financial statements, normalized)
- **Redis** (calculated metrics cache, 1-hour TTL)

**Endpoints**:
```python
GET  /v1/financials/{ticker}                    # Statements
GET  /v1/financials/{ticker}/ratios             # All ratios
GET  /v1/financials/{ticker}/growth             # Growth metrics
GET  /v1/financials/{ticker}/valuation          # Valuation models
GET  /v1/technical/{ticker}/indicators          # Technical indicators
POST /v1/compare                                # Compare companies
```

**Events Published**:
- `financials.updated` - New financial data available
- `financials.anomaly.detected` - Unusual metrics (negative cash flow, etc.)

**Background Jobs**:
- Financial data sync: Daily after market close
- Ratio recalculation: On new financial data

**Scaling**: Auto-scale 2-10 instances

**Performance**:
- Metrics calculation: <200ms for single company
- Batch comparison: <5s for 50 companies
- Technical indicators: <100ms for 1 year daily data

---

### 5. Predictive Analytics Service
**Purpose**: ML-powered forecasting and predictive insights

**Responsibilities**:
- Price prediction (short-term: 1-7 days)
- Volatility forecasting (implied volatility, GARCH)
- Sentiment-driven event prediction
- Correlation and portfolio analysis
- Anomaly detection (unusual patterns)
- Risk scoring (VaR, expected shortfall)

**Technology**: FastAPI + PyTorch/TensorFlow + Scikit-learn

**ML Models**:
- **Price Prediction**: LSTM, Transformer, LightGBM ensemble
- **Volatility**: GARCH, EWMA
- **Anomaly Detection**: Isolation Forest, Autoencoder
- **Risk**: Monte Carlo simulation

**Database**:
- **MongoDB** (model metadata, predictions)
- **S3** (model artifacts, training data)
- **Redis** (prediction cache)

**Endpoints**:
```python
GET  /v1/predict/price/{ticker}?days=7          # Price forecast
GET  /v1/predict/volatility/{ticker}            # Volatility forecast
GET  /v1/analyze/correlation                    # Correlation matrix
GET  /v1/analyze/risk/{ticker}                  # Risk metrics
POST /v1/analyze/portfolio                      # Portfolio analysis
```

**Events Published**:
- `prediction.generated` - New prediction available
- `anomaly.detected` - Unusual pattern found
- `risk.threshold.exceeded` - High risk detected

**Background Jobs**:
- Model training: Weekly
- Batch predictions: Daily after market close
- Feature engineering: Hourly

**Scaling**: Auto-scale 2-8 instances (GPU for training)

**Performance**:
- Inference: <100ms per prediction
- Batch predictions: <10s for 100 tickers
- Model training: <1 hour for updates

---

### 6. Alert & Notification Service
**Purpose**: Manage user alerts and deliver notifications

**Responsibilities**:
- Alert rule management (CRUD)
- Real-time alert evaluation
- Multi-channel delivery (webhook, email, SMS, push)
- Alert throttling and deduplication
- Delivery status tracking
- Scheduled alerts (daily digest, weekly summary)

**Technology**: FastAPI + Celery + Twilio (SMS) + SendGrid (Email)

**Database**:
- **PostgreSQL** (alert rules, delivery logs)
- **Redis** (alert state, throttling)

**Endpoints**:
```python
POST /v1/alerts                          # Create alert rule
GET  /v1/alerts                          # List user alerts
PUT  /v1/alerts/{alert_id}               # Update alert
DELETE /v1/alerts/{alert_id}             # Delete alert
GET  /v1/alerts/{alert_id}/history       # Delivery history
```

**Events Consumed**:
- `market.quote.updated` - Evaluate price alerts
- `news.article.published` - Evaluate news alerts
- `financials.updated` - Evaluate fundamental alerts
- `prediction.generated` - Evaluate ML alerts

**Events Published**:
- `alert.triggered` - Alert condition met
- `alert.delivered` - Notification sent
- `alert.failed` - Delivery failed

**Background Jobs**:
- Alert evaluation: Real-time (event-driven)
- Scheduled digests: Cron (daily, weekly)
- Failed delivery retry: Every 5 minutes

**Scaling**: Auto-scale 2-10 instances

**Performance**:
- Alert latency: <5s from trigger to delivery
- Delivery rate: 99.99%
- Throughput: 10,000 alerts/minute

---

### 7. User & Watchlist Service
**Purpose**: User management, authentication, and watchlist management

**Responsibilities**:
- User registration and profile management
- Authentication (JWT issuance, refresh)
- Authorization (RBAC, permissions)
- Watchlist CRUD operations
- Portfolio tracking
- User preferences and settings

**Technology**: FastAPI + SQLAlchemy + Alembic + JWT

**Database**:
- **PostgreSQL** (users, watchlists, portfolios)
- **Redis** (session cache, JWT blacklist)

**Endpoints**:
```python
POST /v1/auth/register                   # User registration
POST /v1/auth/login                      # Login (get JWT)
POST /v1/auth/refresh                    # Refresh token
GET  /v1/users/me                        # Get user profile
PUT  /v1/users/me                        # Update profile

POST /v1/watchlists                      # Create watchlist
GET  /v1/watchlists                      # List watchlists
PUT  /v1/watchlists/{id}                 # Update watchlist
DELETE /v1/watchlists/{id}               # Delete watchlist

POST /v1/portfolios                      # Create portfolio
GET  /v1/portfolios/{id}/performance     # Portfolio performance
```

**Events Published**:
- `user.registered` - New user created
- `watchlist.updated` - Watchlist modified

**Scaling**: Auto-scale 2-8 instances

**Performance**:
- Authentication: <50ms
- Watchlist sync: <100ms

---

### 8. Data Ingestion Service (Background)
**Purpose**: Continuously ingest data from external providers

**Responsibilities**:
- Scheduled data fetching (quotes, news, financials)
- Provider health monitoring
- Data validation and normalization
- Deduplication
- Error handling and retry logic
- Data quality metrics

**Technology**: Python + Celery + APScheduler

**Database**:
- **TimescaleDB** (raw ingested data)
- **PostgreSQL** (ingestion logs)

**Background Jobs**:
- Quote ingestion: Every 15 seconds (market hours)
- News ingestion: Every 60 seconds
- Financial data: Daily after market close
- Historical backfill: Weekly

**Events Published**:
- `data.ingested` - New data batch ingested
- `data.quality.issue` - Data quality problem detected
- `provider.unavailable` - Provider down

**Scaling**: Auto-scale 3-10 workers

---

### 9. Search & Index Service
**Purpose**: Full-text search across all content

**Responsibilities**:
- Index management (news, companies, financial data)
- Full-text search with relevance scoring
- Autocomplete and suggestions
- Aggregations (faceted search)
- Index optimization and reindexing

**Technology**: Elasticsearch + FastAPI

**Database**:
- **Elasticsearch** (all searchable content)

**Endpoints**:
```python
GET  /v1/search?q={query}&type={type}    # Universal search
GET  /v1/search/suggest?q={partial}      # Autocomplete
GET  /v1/search/company?q={query}        # Company search
GET  /v1/search/news?q={query}           # News search
```

**Events Consumed**:
- `news.article.published` - Index new article
- `company.updated` - Update company index

**Scaling**: Auto-scale 2-6 instances

**Performance**:
- Search latency: <200ms P95
- Index refresh: <10s
- Autocomplete: <50ms

---

### 10. Metrics & Analytics Service (Internal)
**Purpose**: Aggregate and analyze platform usage metrics

**Responsibilities**:
- Platform metrics collection
- User behavior analytics
- API usage tracking
- Cost analysis per provider
- Performance benchmarking
- Business intelligence dashboards

**Technology**: FastAPI + ClickHouse + Apache Superset

**Database**:
- **ClickHouse** (time-series metrics)
- **Redis** (metrics buffer)

**Endpoints** (Internal Only):
```python
POST /internal/metrics/track             # Track event
GET  /internal/metrics/dashboard         # Dashboard data
GET  /internal/metrics/costs             # Cost breakdown
```

**Background Jobs**:
- Metrics aggregation: Every minute
- Reports generation: Daily

**Scaling**: 2-4 instances

---

## Data Architecture

### Database Design

#### PostgreSQL Schema

```sql
-- Users and Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    tier VARCHAR(50) DEFAULT 'free', -- free, pro, enterprise
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE watchlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    tickers TEXT[], -- Array of ticker symbols
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    positions JSONB, -- {ticker: {shares, cost_basis, ...}}
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Alert Management
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    ticker VARCHAR(10),
    condition_type VARCHAR(50), -- price_above, price_below, news, etc.
    condition_value JSONB,
    channels TEXT[], -- ['email', 'sms', 'webhook']
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE alert_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id UUID REFERENCES alerts(id) ON DELETE CASCADE,
    triggered_at TIMESTAMP NOT NULL,
    delivered_at TIMESTAMP,
    channel VARCHAR(50),
    status VARCHAR(50), -- pending, delivered, failed
    error TEXT
);

-- Financial Data
CREATE TABLE companies (
    ticker VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    metadata JSONB,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE financial_statements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) REFERENCES companies(ticker),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    fiscal_year INT NOT NULL,
    fiscal_period VARCHAR(10), -- Q1, Q2, Q3, Q4, FY
    statement_type VARCHAR(50), -- income, balance, cashflow
    data JSONB NOT NULL, -- All financial line items
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(ticker, period_end, statement_type)
);

CREATE INDEX idx_statements_ticker_period ON financial_statements(ticker, period_end DESC);
```

#### TimescaleDB Schema (Time-Series)

```sql
-- OHLCV Data
CREATE TABLE ohlcv (
    time TIMESTAMPTZ NOT NULL,
    ticker VARCHAR(10) NOT NULL,
    open NUMERIC(12, 4),
    high NUMERIC(12, 4),
    low NUMERIC(12, 4),
    close NUMERIC(12, 4),
    volume BIGINT,
    provider VARCHAR(50)
);

SELECT create_hypertable('ohlcv', 'time');
CREATE INDEX idx_ohlcv_ticker_time ON ohlcv (ticker, time DESC);

-- Quotes (Real-time)
CREATE TABLE quotes (
    time TIMESTAMPTZ NOT NULL,
    ticker VARCHAR(10) NOT NULL,
    price NUMERIC(12, 4),
    bid NUMERIC(12, 4),
    ask NUMERIC(12, 4),
    volume BIGINT,
    provider VARCHAR(50)
);

SELECT create_hypertable('quotes', 'time');
CREATE INDEX idx_quotes_ticker_time ON quotes (ticker, time DESC);
```

#### MongoDB Collections

```javascript
// News Articles
{
  _id: ObjectId,
  title: String,
  description: String,
  url: String,
  published_at: Date,
  source: String,
  tickers: [String],
  entities: {
    companies: [String],
    people: [String],
    products: [String]
  },
  sentiment: {
    score: Number,      // -1 to 1
    label: String,      // negative, neutral, positive
    confidence: Number  // 0 to 1
  },
  event_type: [String], // ['earnings', 'product_launch', etc.]
  indexed_at: Date
}

// ML Predictions
{
  _id: ObjectId,
  ticker: String,
  prediction_type: String, // price, volatility, risk
  generated_at: Date,
  horizon: String, // 1d, 7d, 30d
  prediction: {
    value: Number,
    confidence: Number,
    range: {min: Number, max: Number}
  },
  features_used: [String],
  model_version: String
}
```

#### Redis Data Structures

```
# Quote Cache (String with TTL)
quote:{ticker} → JSON (TTL: 300s)

# Rate Limiting (String counter)
ratelimit:{provider}:{minute} → count (TTL: 60s)
ratelimit:user:{user_id}:{minute} → count (TTL: 60s)

# Session Cache (Hash)
session:{token} → {user_id, tier, expires_at} (TTL: 3600s)

# Alert State (Hash)
alert:state:{alert_id} → {last_triggered, count}

# News Cache (Sorted Set)
news:recent → {score: timestamp, member: news_id}
```

---

## API Specifications

### RESTful API Standards

#### URL Structure
```
https://api.aistock.io/v1/{resource}/{identifier}?{query_params}
```

#### Authentication
```http
Authorization: Bearer {jwt_token}
```

#### Response Format (Success)
```json
{
  "data": { ... },
  "meta": {
    "timestamp": "2025-11-10T12:00:00Z",
    "version": "v1"
  }
}
```

#### Response Format (Error - RFC 7807)
```json
{
  "type": "https://api.aistock.io/errors/rate-limit-exceeded",
  "title": "Rate Limit Exceeded",
  "status": 429,
  "detail": "You have exceeded your rate limit of 100 requests per minute",
  "instance": "/v1/quotes/NVDA",
  "retry_after": 30
}
```

#### Pagination (Cursor-based)
```http
GET /v1/news?limit=20&cursor={opaque_cursor}

Response:
{
  "data": [...],
  "meta": {
    "next_cursor": "eyJ0aW1lc3RhbXAiOi4uLn0=",
    "has_more": true
  }
}
```

#### Filtering & Sorting
```http
GET /v1/companies?sector=ai-infrastructure&sort=-market_cap&limit=50
```

---

## Infrastructure Architecture

### Kubernetes Cluster Design

```yaml
# Namespace per environment
apiVersion: v1
kind: Namespace
metadata:
  name: aistock-production
```

```yaml
# Example: Market Data Service Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: market-data-service
  namespace: aistock-production
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2
      maxUnavailable: 1
  selector:
    matchLabels:
      app: market-data-service
  template:
    metadata:
      labels:
        app: market-data-service
        version: v1.2.3
    spec:
      containers:
      - name: market-data
        image: aistock/market-data-service:v1.2.3
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: market-data-service
  namespace: aistock-production
spec:
  selector:
    app: market-data-service
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: market-data-hpa
  namespace: aistock-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: market-data-service
  minReplicas: 5
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Resource Allocation

| Service | Min Replicas | Max Replicas | CPU (request/limit) | Memory (request/limit) |
|---------|--------------|--------------|---------------------|------------------------|
| API Gateway | 2 | 10 | 250m / 1000m | 512Mi / 2Gi |
| Market Data | 5 | 20 | 500m / 2000m | 1Gi / 4Gi |
| News Service | 3 | 15 | 1000m / 4000m | 2Gi / 8Gi |
| Financial Analysis | 2 | 10 | 500m / 2000m | 1Gi / 4Gi |
| Predictive Analytics | 2 | 8 | 2000m / 8000m | 4Gi / 16Gi |
| Alert Service | 2 | 10 | 250m / 1000m | 512Mi / 2Gi |
| User Service | 2 | 8 | 250m / 1000m | 512Mi / 2Gi |
| Data Ingestion | 3 | 10 | 500m / 2000m | 1Gi / 4Gi |
| Search Service | 2 | 6 | 500m / 2000m | 2Gi / 8Gi |

---

## Security Architecture

### Zero-Trust Model

1. **Authentication**: All requests require valid JWT
2. **Authorization**: RBAC with fine-grained permissions
3. **Encryption in Transit**: TLS 1.3 for all communication
4. **Encryption at Rest**: AES-256 for databases and S3
5. **Network Segmentation**: VPC, security groups, network policies
6. **Secrets Management**: HashiCorp Vault / AWS Secrets Manager
7. **Audit Logging**: All access logged with tamper-proof storage

### JWT Structure

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user-uuid",
    "email": "user@example.com",
    "tier": "pro",
    "permissions": ["read:quotes", "read:news", "write:alerts"],
    "iat": 1699632000,
    "exp": 1699635600
  },
  "signature": "..."
}
```

### RBAC Permissions

| Tier | Permissions |
|------|-------------|
| **Free** | read:quotes (delayed), read:news (limited), read:financials (limited) |
| **Pro** | read:quotes (real-time), read:news, read:financials, write:alerts, read:predictions |
| **Enterprise** | All + write:webhooks, read:raw-data, custom SLAs |

---

## Deployment Architecture

### Multi-Region Setup

```
┌──────────────────────────────────────────────────────────────┐
│                     Route 53 (Global DNS)                     │
│              Latency-based routing + health checks            │
└───────┬─────────────────────────┬────────────────────────────┘
        │                         │
   ┌────▼─────┐             ┌─────▼────┐
   │ US-EAST-1│             │ EU-WEST-1│
   │ (Primary)│             │(Secondary)│
   └────┬─────┘             └─────┬────┘
        │                         │
   ┌────▼─────────────────────────▼────────┐
   │    CloudFront (CDN)                    │
   │    API caching, DDoS protection        │
   └────┬───────────────────────────────────┘
        │
   ┌────▼─────────────────────────────────┐
   │  ALB (Application Load Balancer)      │
   │  SSL termination, path routing        │
   └────┬──────────────────────────────────┘
        │
   ┌────▼──────────────────────────────────┐
   │  EKS Cluster (Kubernetes)              │
   │  - API Gateway pods                    │
   │  - Microservice pods                   │
   │  - Auto-scaling groups                 │
   └────┬───────────────────────────────────┘
        │
   ┌────▼──────────────────────────────────┐
   │  Data Layer                            │
   │  - RDS (PostgreSQL) Multi-AZ           │
   │  - ElastiCache (Redis) Cluster         │
   │  - OpenSearch (Elasticsearch)          │
   │  - S3 (object storage)                 │
   └────────────────────────────────────────┘
```

### CI/CD Pipeline

```
┌──────────────┐
│ Git Push     │
└──────┬───────┘
       │
┌──────▼────────┐
│ GitHub Actions│
│ - Lint        │
│ - Test        │
│ - Security    │
└──────┬────────┘
       │
┌──────▼────────┐
│ Build & Push  │
│ Docker image  │
│ to ECR        │
└──────┬────────┘
       │
┌──────▼────────┐
│ Deploy to     │
│ Staging (EKS) │
│ - Smoke tests │
└──────┬────────┘
       │
┌──────▼────────┐
│ Manual        │
│ Approval      │
└──────┬────────┘
       │
┌──────▼────────┐
│ Blue-Green    │
│ Deploy to Prod│
│ - Canary 10%  │
│ - Canary 50%  │
│ - Full 100%   │
└───────────────┘
```

---

## Monitoring & Observability

### Key Metrics

#### Golden Signals
1. **Latency**: Request duration (P50, P95, P99)
2. **Traffic**: Requests per second
3. **Errors**: Error rate (%)
4. **Saturation**: CPU, memory, disk, network utilization

#### Custom Metrics
- Cache hit rate
- Provider failover count
- Alert delivery rate
- ML model inference latency
- Database query performance

### Alerting Rules

```yaml
# High error rate
alert: HighErrorRate
expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
for: 5m
severity: critical
annotations:
  summary: "High error rate detected"

# High latency
alert: HighLatency
expr: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 1
for: 5m
severity: warning

# Service down
alert: ServiceDown
expr: up{job="market-data-service"} == 0
for: 2m
severity: critical
```

---

## Next Steps

1. **Review & Approve** this specification
2. **Create detailed implementation plan** (next document)
3. **Set up infrastructure** (AWS, Kubernetes, databases)
4. **Implement Phase 1 services** (Market Data, News, User)
5. **Deploy to staging** and validate
6. **Production deployment** with monitoring

---

**Document Status**: DRAFT for Review
**Owner**: Engineering Team
**Review Date**: TBD
**Approval Date**: TBD
