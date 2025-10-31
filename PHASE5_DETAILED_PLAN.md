# 🎯 Phase 5: Deployment & Launch - Detailed Plan

**Project Type:** Startup Product - Production Deployment & Public Launch  
**Timeline:** 4-6 weeks  
**Start Date:** Late July 2026 (after Phase 4 completion)  
**Target Completion:** Late August 2026  
**Focus:** Production infrastructure, launch, paying customers

**Prerequisites:** Phase 1 (ML engine) + Phase 2 (Backend) + Phase 3 (Frontend) + Phase 4 (Advanced features) complete

---

## 📋 Executive Summary

### What We're Building
**Production-ready infrastructure and go-to-market strategy:**
- **Cloud infrastructure** (AWS/GCP production setup, scalable architecture)
- **CI/CD pipeline** (automated testing, deployment, rollbacks)
- **Monitoring & observability** (logs, metrics, alerts, dashboards)
- **Security & compliance** (HTTPS, firewall, backups, SOC 2)
- **Marketing site** (landing page, pricing, blog, docs)
- **Billing & payments** (Stripe integration, subscription management)
- **Beta launch** (first 20-50 paying customers)
- **Support system** (help center, chat, ticketing)

### Why This Phase Matters
- 🚀 **Launch:** Go from development to production
- 💰 **Revenue:** Start acquiring paying customers
- 📈 **Scale:** Infrastructure ready for 1000+ users
- 🛡️ **Trust:** Security and compliance for enterprise
- 🎯 **GTM:** Marketing and sales engine ready

### Business Milestones
- **Week 1-2:** Deploy to production (AWS/GCP)
- **Week 3:** Soft launch to beta users (20-50 customers)
- **Week 4:** Marketing site + billing live
- **Week 5:** Public launch (Product Hunt, social media)
- **Week 6:** First paying customers, iterate based on feedback

### Success Criteria
- ✅ Production environment live (AWS/GCP)
- ✅ 99.9% uptime SLA
- ✅ CI/CD pipeline automated
- ✅ Monitoring & alerts configured
- ✅ Security audit passed
- ✅ Marketing site live (landing page, pricing, docs)
- ✅ Billing integrated (Stripe)
- ✅ Beta users onboarded (20-50 customers)
- ✅ Public launch executed
- ✅ First 10+ paying customers acquired
- ✅ Support system operational

---

## 🗓️ Phase 5 Timeline Breakdown

### **Module 1: Cloud Infrastructure & Deployment** (Weeks 1-2)
**Deliverables:** Production-ready cloud setup

---

#### Week 1: Infrastructure Setup
**Focus:** Cloud platform, architecture, database

**Tasks:**

**Day 1: Choose Cloud Platform**
- [ ] Evaluate options:
  - **AWS (Amazon Web Services):**
    - Pros: Most mature, extensive services, best documentation
    - Cons: Complex pricing, steep learning curve
    - Services: EC2, RDS, S3, CloudFront, Lambda
  
  - **GCP (Google Cloud Platform):**
    - Pros: Simpler pricing, great ML support, good DX
    - Cons: Fewer services than AWS, smaller community
    - Services: Compute Engine, Cloud SQL, Cloud Storage, Cloud Run
  
  - **Azure:**
    - Pros: Good for enterprises, Microsoft integration
    - Cons: Complex, expensive
  
  - **Railway/Render/Fly.io:**
    - Pros: Easiest, cheapest for startups, great DX
    - Cons: Less control, fewer services, scaling limits
  
  - **Recommended:** **AWS** (industry standard, best for startups scaling to enterprise)
  - **Alternative:** **Railway/Render** (if budget-constrained, MVP first)

- [ ] Create AWS account:
  - Root account (email + MFA)
  - IAM users (don't use root for daily work)
  - Billing alerts (set budget, get alerts)

**Day 2: Architecture Design**
- [ ] Design production architecture:
  ```
  Production Architecture (AWS):
  
  ┌─────────────────────────────────────────────────────────────┐
  │                      Users (Web/Mobile)                      │
  └────────────────────────┬────────────────────────────────────┘
                           │
                           ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                 CloudFront (CDN)                             │
  │              - Static assets (images, JS, CSS)               │
  │              - Edge caching (global)                         │
  └────────────────────────┬────────────────────────────────────┘
                           │
                           ▼
  ┌─────────────────────────────────────────────────────────────┐
  │              Application Load Balancer (ALB)                 │
  │              - HTTPS termination                             │
  │              - Health checks                                 │
  │              - Auto-scaling trigger                          │
  └────────────────────────┬────────────────────────────────────┘
                           │
           ┌───────────────┴───────────────┐
           │                               │
           ▼                               ▼
  ┌──────────────────┐         ┌──────────────────┐
  │   EC2 Instance   │         │   EC2 Instance   │
  │  (Backend API)   │         │  (Backend API)   │
  │  - FastAPI app   │         │  - FastAPI app   │
  │  - Uvicorn       │         │  - Uvicorn       │
  │  - Auto-scaling  │         │  - Auto-scaling  │
  └────────┬─────────┘         └────────┬─────────┘
           │                            │
           └──────────┬─────────────────┘
                      │
                      ▼
  ┌─────────────────────────────────────────────────────────────┐
  │              RDS PostgreSQL (Multi-AZ)                       │
  │              - Primary + Standby replica                     │
  │              - Automated backups (daily)                     │
  │              - Point-in-time recovery                        │
  └─────────────────────────────────────────────────────────────┘
  
  ┌─────────────────────────────────────────────────────────────┐
  │              ElastiCache Redis (Cluster)                     │
  │              - Caching (API responses, sessions)             │
  │              - Celery broker (background jobs)               │
  └─────────────────────────────────────────────────────────────┘
  
  ┌─────────────────────────────────────────────────────────────┐
  │              S3 Buckets                                      │
  │              - Resumes (private, encrypted)                  │
  │              - ML models (versioned)                         │
  │              - Static assets (public)                        │
  │              - Backups (versioned, lifecycle)                │
  └─────────────────────────────────────────────────────────────┘
  
  ┌─────────────────────────────────────────────────────────────┐
  │              Celery Workers (Auto-scaling)                   │
  │              - Resume parsing (OCR, NLP)                     │
  │              - Candidate matching (ML inference)             │
  │              - Email sending (background)                    │
  └─────────────────────────────────────────────────────────────┘
  
  ┌─────────────────────────────────────────────────────────────┐
  │              CloudWatch (Monitoring)                         │
  │              - Logs (application, access, error)             │
  │              - Metrics (CPU, memory, latency)                │
  │              - Alarms (email/SMS on issues)                  │
  └─────────────────────────────────────────────────────────────┘
  ```

- [ ] Create infrastructure-as-code (Terraform):
  ```hcl
  # infrastructure/terraform/main.tf
  terraform {
    required_providers {
      aws = {
        source  = "hashicorp/aws"
        version = "~> 5.0"
      }
    }
  }
  
  provider "aws" {
    region = var.aws_region
  }
  
  # VPC (Virtual Private Cloud)
  resource "aws_vpc" "main" {
    cidr_block = "10.0.0.0/16"
    enable_dns_hostnames = true
    enable_dns_support   = true
    
    tags = {
      Name = "intellimatch-vpc"
    }
  }
  
  # Subnets (public + private)
  resource "aws_subnet" "public_1" {
    vpc_id            = aws_vpc.main.id
    cidr_block        = "10.0.1.0/24"
    availability_zone = "${var.aws_region}a"
    map_public_ip_on_launch = true
  }
  
  # RDS PostgreSQL
  resource "aws_db_instance" "postgres" {
    identifier        = "intellimatch-db"
    engine            = "postgres"
    engine_version    = "15.3"
    instance_class    = "db.t3.medium"
    allocated_storage = 100
    storage_type      = "gp3"
    
    db_name  = "intellimatch"
    username = var.db_username
    password = var.db_password
    
    multi_az               = true  # High availability
    backup_retention_period = 7
    backup_window          = "03:00-04:00"
    maintenance_window     = "Mon:04:00-Mon:05:00"
    
    skip_final_snapshot = false
    final_snapshot_identifier = "intellimatch-final-snapshot"
  }
  
  # ElastiCache Redis
  resource "aws_elasticache_cluster" "redis" {
    cluster_id           = "intellimatch-redis"
    engine               = "redis"
    node_type            = "cache.t3.medium"
    num_cache_nodes      = 1
    parameter_group_name = "default.redis7"
    port                 = 6379
  }
  
  # S3 Buckets
  resource "aws_s3_bucket" "resumes" {
    bucket = "intellimatch-resumes-${var.environment}"
  }
  
  resource "aws_s3_bucket_versioning" "resumes" {
    bucket = aws_s3_bucket.resumes.id
    versioning_configuration {
      status = "Enabled"
    }
  }
  ```

**Day 3: Database Setup**
- [ ] Provision RDS PostgreSQL:
  - Multi-AZ deployment (high availability)
  - Instance size: db.t3.medium (2 vCPU, 4GB RAM)
  - Storage: 100GB (auto-scaling to 500GB)
  - Backups: Daily automated, 7-day retention
  - Encryption: At rest (AWS KMS)

- [ ] Configure database:
  - Create production database
  - Create read replica (for analytics queries)
  - Setup parameter groups (optimize for production)
  - Configure security groups (allow only from backend)

- [ ] Run migrations:
  ```bash
  # Set production DATABASE_URL
  export DATABASE_URL="postgresql://user:pass@intellimatch-db.abc.rds.amazonaws.com:5432/intellimatch"
  
  # Run Alembic migrations
  alembic upgrade head
  
  # Verify tables created
  psql $DATABASE_URL -c "\dt"
  ```

**Day 4: Storage & CDN**
- [ ] Setup S3 buckets:
  - **Resumes bucket:**
    - Private (no public access)
    - Encryption (SSE-S3)
    - Versioning enabled
    - Lifecycle policy (delete old versions after 90 days)
    - Bucket policy (only backend can access)
  
  - **Static assets bucket:**
    - Public read access
    - CloudFront distribution (CDN)
    - Cache-Control headers (1 year cache)
  
  - **Backups bucket:**
    - Cross-region replication (disaster recovery)
    - Glacier transition (old backups after 30 days)

- [ ] Setup CloudFront (CDN):
  - Origin: S3 static assets bucket
  - Edge locations: Global
  - Cache behavior: Cache for 1 year
  - Custom domain: cdn.intellimatch.ai
  - SSL certificate (AWS ACM)

**Day 5: Compute & Auto-Scaling**
- [ ] Create EC2 launch template:
  ```yaml
  # infrastructure/ec2-user-data.sh
  #!/bin/bash
  
  # Update system
  yum update -y
  
  # Install Docker
  amazon-linux-extras install docker -y
  systemctl start docker
  systemctl enable docker
  
  # Install Docker Compose
  curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  chmod +x /usr/local/bin/docker-compose
  
  # Pull application Docker image
  docker pull ghcr.io/meher4567/intellimatch-backend:latest
  
  # Run application
  docker run -d \
    --name intellimatch-backend \
    -p 8000:8000 \
    -e DATABASE_URL="${DATABASE_URL}" \
    -e REDIS_URL="${REDIS_URL}" \
    -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
    -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
    ghcr.io/meher4567/intellimatch-backend:latest
  ```

- [ ] Create Auto Scaling Group:
  - Min instances: 2 (high availability)
  - Max instances: 10 (scale for traffic)
  - Desired: 2
  - Health checks: ELB health checks (every 30 seconds)
  - Scaling policy:
    - Scale up: CPU > 70% for 5 minutes → add 1 instance
    - Scale down: CPU < 30% for 5 minutes → remove 1 instance

- [ ] Create Application Load Balancer:
  - Public-facing (internet-facing)
  - HTTPS listener (port 443)
  - HTTP listener (port 80) → redirect to HTTPS
  - Target group: EC2 instances (port 8000)
  - Health check: GET /health (expect 200)
  - Stickiness: Enabled (session affinity)

**Deliverables:**
- AWS account setup (IAM, billing alerts)
- Infrastructure-as-code (Terraform)
- RDS PostgreSQL (Multi-AZ, encrypted, backups)
- ElastiCache Redis (cluster mode)
- S3 buckets (resumes, static, backups)
- CloudFront CDN (static assets)
- EC2 Auto Scaling Group (2-10 instances)
- Application Load Balancer (HTTPS)

**Learning Focus:**
- Cloud architecture design
- Infrastructure-as-code (Terraform)
- AWS services (EC2, RDS, S3, CloudFront)
- High availability and disaster recovery
- Security best practices (encryption, IAM)

---

#### Week 2: CI/CD Pipeline & Deployment
**Focus:** Automated testing, building, deployment

**Tasks:**

**Day 1: GitHub Actions CI/CD**
- [ ] Create CI/CD pipeline:
  ```yaml
  # .github/workflows/deploy.yml
  name: Deploy to Production
  
  on:
    push:
      branches: [main]
    pull_request:
      branches: [main]
  
  jobs:
    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        
        - name: Set up Python
          uses: actions/setup-python@v4
          with:
            python-version: '3.11'
        
        - name: Install dependencies
          run: |
            pip install -r requirements.txt
            pip install pytest pytest-cov
        
        - name: Run tests
          run: pytest --cov=src --cov-report=xml
        
        - name: Upload coverage
          uses: codecov/codecov-action@v3
    
    build-backend:
      needs: test
      runs-on: ubuntu-latest
      if: github.ref == 'refs/heads/main'
      steps:
        - uses: actions/checkout@v3
        
        - name: Build Docker image
          run: docker build -t intellimatch-backend:${{ github.sha }} .
        
        - name: Push to GitHub Container Registry
          run: |
            echo ${{ secrets.GITHUB_TOKEN }} | docker login ghcr.io -u ${{ github.actor }} --password-stdin
            docker tag intellimatch-backend:${{ github.sha }} ghcr.io/meher4567/intellimatch-backend:latest
            docker push ghcr.io/meher4567/intellimatch-backend:latest
    
    build-frontend:
      needs: test
      runs-on: ubuntu-latest
      if: github.ref == 'refs/heads/main'
      steps:
        - uses: actions/checkout@v3
        
        - name: Set up Node.js
          uses: actions/setup-node@v3
          with:
            node-version: '18'
        
        - name: Install dependencies
          run: cd frontend && npm install
        
        - name: Build
          run: cd frontend && npm run build
        
        - name: Deploy to Vercel
          uses: amondnet/vercel-action@v25
          with:
            vercel-token: ${{ secrets.VERCEL_TOKEN }}
            vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
            vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
            vercel-args: '--prod'
    
    deploy-backend:
      needs: [build-backend]
      runs-on: ubuntu-latest
      steps:
        - name: Deploy to AWS
          run: |
            # Trigger AWS CodeDeploy or ECS update
            # Or SSH to EC2 and pull new image
            aws ecs update-service \
              --cluster intellimatch-cluster \
              --service intellimatch-backend \
              --force-new-deployment
  ```

- [ ] Setup secrets:
  - GitHub secrets (Settings → Secrets)
  - AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
  - Database credentials (DATABASE_URL)
  - API keys (OPENAI_API_KEY, SENDGRID_API_KEY)
  - Vercel token (VERCEL_TOKEN)

**Day 2: Database Migrations**
- [ ] Automated migration strategy:
  ```python
  # deployment/migrate.py
  import alembic.config
  
  def run_migrations():
      """Run database migrations during deployment"""
      alembic_args = [
          '--raiseerr',
          'upgrade', 'head',
      ]
      alembic.config.main(argv=alembic_args)
  
  if __name__ == '__main__':
      run_migrations()
  ```

- [ ] Deployment script:
  ```bash
  #!/bin/bash
  # deployment/deploy.sh
  
  set -e  # Exit on error
  
  echo "Starting deployment..."
  
  # 1. Backup database
  echo "Backing up database..."
  pg_dump $DATABASE_URL > backups/backup-$(date +%Y%m%d-%H%M%S).sql
  
  # 2. Run migrations
  echo "Running migrations..."
  python deployment/migrate.py
  
  # 3. Pull new Docker image
  echo "Pulling new image..."
  docker pull ghcr.io/meher4567/intellimatch-backend:latest
  
  # 4. Restart containers (zero-downtime)
  echo "Restarting containers..."
  docker-compose up -d --no-deps --build backend
  
  # 5. Health check
  echo "Checking health..."
  sleep 10
  curl -f http://localhost:8000/health || exit 1
  
  echo "Deployment successful!"
  ```

**Day 3: Zero-Downtime Deployment**
- [ ] Blue-Green deployment:
  - **Blue environment:** Current production (running)
  - **Green environment:** New version (deploy here)
  - Test green environment
  - Switch load balancer to green
  - Keep blue for rollback (24 hours)

- [ ] Rolling deployment:
  - Auto Scaling Group with multiple instances
  - Deploy to 1 instance at a time
  - Health check passes → deploy to next
  - If health check fails → stop deployment

- [ ] Database migration safety:
  - Backwards-compatible migrations only
  - Add column (not rename or delete)
  - Deploy code first, then migrate
  - Or: Migrate first (if backwards compatible)

**Day 4: Rollback Strategy**
- [ ] Automated rollback:
  ```yaml
  # .github/workflows/rollback.yml
  name: Rollback Deployment
  
  on:
    workflow_dispatch:
      inputs:
        version:
          description: 'Version to rollback to'
          required: true
  
  jobs:
    rollback:
      runs-on: ubuntu-latest
      steps:
        - name: Rollback Docker image
          run: |
            docker pull ghcr.io/meher4567/intellimatch-backend:${{ github.event.inputs.version }}
            docker tag ghcr.io/meher4567/intellimatch-backend:${{ github.event.inputs.version }} \
                       ghcr.io/meher4567/intellimatch-backend:latest
            docker push ghcr.io/meher4567/intellimatch-backend:latest
        
        - name: Deploy rolled-back version
          run: |
            aws ecs update-service \
              --cluster intellimatch-cluster \
              --service intellimatch-backend \
              --force-new-deployment
  ```

- [ ] Database rollback:
  - Restore from backup (last 7 days available)
  - Point-in-time recovery (RDS feature)
  - Test rollback procedure (disaster recovery drill)

**Day 5: Environment Management**
- [ ] Multiple environments:
  - **Development:** `dev.intellimatch.ai` (auto-deploy from `dev` branch)
  - **Staging:** `staging.intellimatch.ai` (auto-deploy from `staging` branch)
  - **Production:** `app.intellimatch.ai` (auto-deploy from `main` branch)

- [ ] Environment variables:
  ```bash
  # .env.production
  ENVIRONMENT=production
  DEBUG=false
  DATABASE_URL=postgresql://...
  REDIS_URL=redis://...
  AWS_S3_BUCKET=intellimatch-resumes-prod
  SENDGRID_API_KEY=SG.xxx
  OPENAI_API_KEY=sk-xxx
  SENTRY_DSN=https://xxx@sentry.io/xxx
  ```

- [ ] Secrets management:
  - **AWS Secrets Manager:** Store sensitive credentials
  - Rotate secrets regularly (every 90 days)
  - Access via IAM roles (not hardcoded)

**Deliverables:**
- GitHub Actions CI/CD pipeline
- Automated testing (on every commit)
- Docker image building (backend + frontend)
- Automated deployment (to AWS)
- Zero-downtime deployment strategy
- Rollback procedure
- Multi-environment setup (dev, staging, prod)

**Learning Focus:**
- CI/CD best practices
- Docker containerization
- Deployment automation
- Zero-downtime strategies
- Secrets management

---

### **Module 2: Monitoring, Security & Performance** (Week 3)
**Deliverables:** Observability, hardening, optimization

---

#### Week 3: Production Hardening
**Focus:** Monitoring, security, performance

**Tasks:**

**Day 1: Monitoring & Logging**
- [ ] Setup CloudWatch:
  - **Application logs:**
    - All backend logs (info, warning, error)
    - Frontend errors (JavaScript errors)
    - Search and filter logs
    - Log retention: 30 days
  
  - **Metrics:**
    - CPU utilization (EC2, RDS)
    - Memory usage
    - Disk I/O
    - Network traffic
    - Database connections
    - API latency (p50, p95, p99)
    - Error rate (5xx responses)
  
  - **Custom metrics:**
    ```python
    # src/utils/metrics.py
    import boto3
    
    cloudwatch = boto3.client('cloudwatch')
    
    def track_metric(name: str, value: float, unit: str = 'Count'):
        cloudwatch.put_metric_data(
            Namespace='IntelliMatch',
            MetricData=[{
                'MetricName': name,
                'Value': value,
                'Unit': unit,
            }]
        )
    
    # Usage
    track_metric('ResumesParsed', 1)
    track_metric('MatchingDuration', 1.5, 'Seconds')
    ```

- [ ] Setup error tracking (Sentry):
  ```bash
  pip install sentry-sdk
  ```
  ```python
  # src/main.py
  import sentry_sdk
  
  sentry_sdk.init(
      dsn="https://xxx@sentry.io/xxx",
      environment="production",
      traces_sample_rate=0.1,  # 10% of requests
  )
  ```

**Day 2: Alerting & Dashboards**
- [ ] Configure CloudWatch alarms:
  - **Critical alarms (page on-call engineer):**
    - API error rate > 5% for 5 minutes
    - Database CPU > 90% for 5 minutes
    - No healthy instances in Auto Scaling Group
    - RDS storage < 10% free
  
  - **Warning alarms (send email):**
    - API latency p95 > 1 second for 10 minutes
    - Database connections > 80% of max
    - S3 bucket size growing rapidly
  
  - **Info alarms (send to Slack):**
    - New user signup
    - Large resume uploaded (> 5MB)

- [ ] Notification channels:
  - Email (AWS SNS → Email)
  - Slack (AWS SNS → Lambda → Slack webhook)
  - PagerDuty (for critical alerts)

- [ ] Create dashboards:
  - **System health dashboard:**
    - Green/yellow/red indicators
    - API uptime (last 24 hours)
    - Error rate
    - Active users
  
  - **Business metrics dashboard:**
    - New signups today
    - Resumes parsed today
    - Jobs created today
    - Matches generated today
    - Revenue (if billing live)

**Day 3: Security Hardening**
- [ ] HTTPS everywhere:
  - SSL certificate (AWS ACM or Let's Encrypt)
  - Force HTTPS (redirect HTTP → HTTPS)
  - HSTS header (Strict-Transport-Security)
  - Secure cookies (httpOnly, secure, sameSite)

- [ ] Firewall & network security:
  - Security groups:
    - ALB: Allow 80, 443 from 0.0.0.0/0 (internet)
    - EC2: Allow 8000 from ALB only
    - RDS: Allow 5432 from EC2 only
    - Redis: Allow 6379 from EC2 only
  - No SSH from internet (use AWS Systems Manager)
  - VPC: Private subnets for backend, database

- [ ] Application security:
  - **Rate limiting:**
    ```python
    from slowapi import Limiter
    
    limiter = Limiter(key_func=get_remote_address)
    
    @app.post("/api/v1/resumes/upload")
    @limiter.limit("10/minute")  # Max 10 uploads per minute
    async def upload_resume():
        pass
    ```
  
  - **Input validation:**
    - Pydantic models (already have)
    - Sanitize file uploads (check magic bytes)
    - SQL injection protection (use ORM, not raw SQL)
  
  - **CORS:**
    ```python
    from fastapi.middleware.cors import CORSMiddleware
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://app.intellimatch.ai"],
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    ```
  
  - **CSP (Content Security Policy):**
    ```python
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response
    ```

**Day 4: Performance Optimization**
- [ ] Database optimization:
  - Indexes on frequently queried columns
  - Connection pooling (SQLAlchemy pool_size=20)
  - Query optimization (EXPLAIN ANALYZE)
  - Read replica for analytics queries
  - Vacuum and analyze (maintenance)

- [ ] Caching strategy:
  - **Redis caching:**
    ```python
    @lru_cache(maxsize=1000)
    def get_job_by_id(job_id: int):
        # Check Redis first
        cached = redis.get(f"job:{job_id}")
        if cached:
            return json.loads(cached)
        
        # Query database
        job = db.query(Job).get(job_id)
        
        # Cache for 1 hour
        redis.setex(f"job:{job_id}", 3600, json.dumps(job))
        
        return job
    ```
  
  - **HTTP caching:**
    - Cache-Control headers
    - ETag (conditional requests)
    - CDN for static assets

- [ ] Backend optimization:
  - Async I/O (FastAPI already async)
  - Background tasks (Celery for heavy jobs)
  - Pagination (limit 50 per page)
  - Database query batching (avoid N+1)

- [ ] Frontend optimization:
  - Code splitting (lazy load routes)
  - Image optimization (WebP, lazy load)
  - Bundle size < 500KB
  - Service worker (cache API responses)

**Day 5: Backup & Disaster Recovery**
- [ ] Automated backups:
  - **Database:**
    - RDS automated backups (daily, 7-day retention)
    - Manual snapshots (before major changes)
    - Cross-region replication (disaster recovery)
  
  - **Files (S3):**
    - Versioning enabled
    - Cross-region replication
    - Lifecycle policy (old versions to Glacier)
  
  - **Code:**
    - Git (GitHub) - already backed up
    - Docker images (GitHub Container Registry)

- [ ] Disaster recovery plan:
  1. **Data loss:** Restore from backup (RTO: 1 hour, RPO: 24 hours)
  2. **Region outage:** Failover to backup region (RTO: 4 hours)
  3. **Complete AWS failure:** Export data to GCP (RTO: 1 day)
  
- [ ] Test disaster recovery:
  - Quarterly DR drill
  - Restore from backup (verify data)
  - Failover to backup region (verify app works)

**Deliverables:**
- CloudWatch monitoring (logs, metrics, dashboards)
- Sentry error tracking
- Alerting (email, Slack, PagerDuty)
- Security hardened (HTTPS, firewall, rate limiting)
- Performance optimized (caching, database indexes)
- Backup strategy (database, files, code)
- Disaster recovery plan (tested quarterly)

**Learning Focus:**
- Observability (logs, metrics, traces)
- Alerting strategies
- Security best practices
- Performance optimization
- Disaster recovery planning

---

### **Module 3: Marketing Site & Billing** (Week 4)
**Deliverables:** Landing page, pricing, payments

---

#### Week 4: Go-to-Market Preparation
**Focus:** Marketing site, billing, support

**Tasks:**

**Day 1: Marketing Site (Landing Page)**
- [ ] Design landing page:
  - **Hero section:**
    - Headline: "AI-Powered Resume Screening That Saves You 90% of Time"
    - Subheadline: "Screen hundreds of resumes in minutes, not days. Match candidates to jobs with 95% accuracy."
    - CTA button: "Start Free Trial" (14 days free)
    - Hero image: Dashboard screenshot or animated demo
  
  - **Social proof:**
    - "Trusted by 500+ companies"
    - Logos (if any customers yet, or use "As seen in...")
    - Testimonials (get from beta users)
  
  - **Features section:**
    - Resume parsing (OCR, NLP)
    - AI matching (ranked candidates)
    - Interview scheduling
    - Team collaboration
    - Analytics & insights
  
  - **How it works:**
    - Step 1: Upload resumes (drag & drop)
    - Step 2: Create job posting (set requirements)
    - Step 3: Get ranked candidates (with explanations)
    - Step 4: Schedule interviews (1-click)
  
  - **Pricing:**
    - Teaser: "Plans starting at $99/month"
    - Link to pricing page
  
  - **CTA section:**
    - "Ready to hire faster and smarter?"
    - "Start Free Trial" button

- [ ] Build landing page:
  - **Tech stack:** Next.js (SEO-friendly, fast)
  - **Styling:** Tailwind CSS
  - **Components:** Hero, Features, Testimonials, CTA
  - **Animations:** Framer Motion (smooth animations)
  - **Analytics:** Google Analytics (track conversions)

**Day 2: Pricing Page**
- [ ] Define pricing tiers:
  - **Free (Beta):**
    - 10 resumes/month
    - 1 job posting
    - Basic matching
    - Email support
    - **Price:** $0/month (limited time)
  
  - **Starter:**
    - 100 resumes/month
    - 5 job postings
    - AI matching with explanations
    - Interview scheduling
    - Team collaboration (3 users)
    - Email support
    - **Price:** $99/month
  
  - **Professional:**
    - 500 resumes/month
    - Unlimited job postings
    - Advanced matching (custom scoring)
    - Predictive analytics
    - Team collaboration (10 users)
    - API access
    - Priority support
    - **Price:** $299/month
  
  - **Enterprise:**
    - Unlimited resumes
    - Unlimited job postings
    - White-label (custom branding)
    - Dedicated account manager
    - Custom integrations (ATS)
    - SLA (99.9% uptime)
    - Phone support
    - **Price:** Custom (starting at $999/month)

- [ ] Pricing page design:
  - Comparison table (features by tier)
  - FAQ section ("Can I change plans?", "What happens after trial?")
  - CTA: "Start Free Trial" or "Contact Sales" (Enterprise)

**Day 3: Stripe Integration**
- [ ] Setup Stripe:
  - Create Stripe account
  - Create products & prices:
    ```bash
    stripe products create --name="IntelliMatch Starter" --description="100 resumes/month"
    stripe prices create --product=prod_xxx --unit-amount=9900 --currency=usd --recurring="{'interval': 'month'}"
    ```

- [ ] Integrate Stripe (backend):
  ```python
  # src/services/billing.py
  import stripe
  
  stripe.api_key = STRIPE_SECRET_KEY
  
  def create_checkout_session(user_id: int, price_id: str):
      session = stripe.checkout.Session.create(
          customer_email=user.email,
          payment_method_types=['card'],
          line_items=[{
              'price': price_id,
              'quantity': 1,
          }],
          mode='subscription',
          success_url='https://app.intellimatch.ai/success?session_id={CHECKOUT_SESSION_ID}',
          cancel_url='https://app.intellimatch.ai/pricing',
          metadata={'user_id': user_id},
      )
      return session.url
  
  def handle_webhook(payload, sig_header):
      event = stripe.Webhook.construct_event(
          payload, sig_header, STRIPE_WEBHOOK_SECRET
      )
      
      if event['type'] == 'checkout.session.completed':
          session = event['data']['object']
          user_id = session['metadata']['user_id']
          # Activate subscription for user
          activate_subscription(user_id, session['subscription'])
      
      elif event['type'] == 'invoice.payment_failed':
          # Send email to user (payment failed)
          pass
  ```

- [ ] Integrate Stripe (frontend):
  ```tsx
  // src/pages/UpgradePage.tsx
  const handleUpgrade = async (priceId: string) => {
      const response = await api.post('/billing/create-checkout-session', { priceId });
      const { url } = response.data;
      window.location.href = url;  // Redirect to Stripe checkout
  };
  ```

**Day 4: Subscription Management**
- [ ] Subscription model:
  ```python
  # src/models/subscription.py
  class Subscription(Base):
      id = Column(Integer, primary_key=True)
      user_id = Column(Integer, ForeignKey('users.id'))
      stripe_subscription_id = Column(String)
      plan = Column(Enum('free', 'starter', 'professional', 'enterprise'))
      status = Column(Enum('active', 'canceled', 'past_due'))
      current_period_start = Column(DateTime)
      current_period_end = Column(DateTime)
      
      # Usage tracking
      resumes_uploaded = Column(Integer, default=0)
      resumes_limit = Column(Integer)
  ```

- [ ] Usage limits:
  ```python
  # src/middleware/usage_limits.py
  def check_usage_limit(user: User):
      subscription = user.subscription
      
      if subscription.resumes_uploaded >= subscription.resumes_limit:
          raise HTTPException(
              status_code=403,
              detail="You've reached your monthly resume limit. Upgrade to continue."
          )
      
      subscription.resumes_uploaded += 1
      db.commit()
  ```

- [ ] Subscription management UI:
  - View current plan
  - Upgrade/downgrade (Stripe billing portal)
  - Cancel subscription
  - View invoices
  - Update payment method

**Day 5: Support System**
- [ ] Help center:
  - **Knowledge base:**
    - Getting started guide
    - How-to articles (upload resume, create job, etc.)
    - FAQ (common questions)
    - Video tutorials
  
  - **Tech stack:** Notion (easy to edit) or custom (Next.js)
  - **Search:** Algolia or simple fuzzy search

- [ ] In-app chat (Intercom or similar):
  - Live chat widget (bottom-right corner)
  - Chatbot for common questions
  - Route to human (if chatbot can't help)
  - Track conversations (history)

- [ ] Ticketing system:
  - Email support (support@intellimatch.ai)
  - Ticket tracking (Zendesk, Help Scout, or custom)
  - SLA: Respond within 24 hours (Starter), 4 hours (Professional)

**Deliverables:**
- Marketing site (landing page, pricing, docs)
- Stripe integration (checkout, subscriptions)
- Usage limits (enforce plan limits)
- Subscription management UI
- Help center (knowledge base, search)
- Support system (chat, ticketing)

**Learning Focus:**
- Landing page design & conversion optimization
- Subscription billing (Stripe)
- Usage tracking and limits
- Customer support systems

---

### **Module 4: Launch & Customer Acquisition** (Weeks 5-6)
**Deliverables:** Beta launch, public launch, first customers

---

#### Week 5: Beta Launch
**Focus:** Soft launch to beta users

**Tasks:**

**Day 1: Beta User Recruitment**
- [ ] Identify beta users:
  - Personal network (friends, colleagues)
  - LinkedIn connections (recruiters, HR)
  - Reddit (r/recruiting, r/startups)
  - Twitter/X (tweet about beta)
  - Product Hunt "upcoming" page

- [ ] Beta criteria:
  - Target 20-50 beta users
  - Mix of company sizes (startups, SMBs, enterprises)
  - Active recruiters (will actually use product)
  - Willing to provide feedback

- [ ] Beta incentives:
  - Free access (no credit card required)
  - Lifetime discount (50% off when launching)
  - Early access to features
  - Name on "Early Adopters" page

**Day 2: Onboarding Beta Users**
- [ ] Onboarding email sequence:
  - **Email 1 (Day 0):** Welcome + getting started guide
  - **Email 2 (Day 1):** "Did you upload your first resume?"
  - **Email 3 (Day 3):** "Top 3 features you should try"
  - **Email 4 (Day 7):** "How's it going? Any questions?"
  - **Email 5 (Day 14):** "Share your feedback (get $50 Amazon gift card)"

- [ ] Personal onboarding calls:
  - Schedule 30-min call with each beta user
  - Walk through product
  - Answer questions
  - Gather feedback (pain points, missing features)

**Day 3: Feedback Collection**
- [ ] Feedback mechanisms:
  - In-app feedback button (Typeform or custom)
  - Weekly check-in emails
  - User interviews (1-on-1 calls)
  - Analytics (track feature usage)

- [ ] Metrics to track:
  - Activation rate (% who upload resume)
  - Retention (% who return after 7 days)
  - Feature usage (which features used most?)
  - NPS (Net Promoter Score: "Would you recommend?")
  - Time-to-value (how long to first match?)

**Day 4-5: Iterate Based on Feedback**
- [ ] Common feedback themes:
  - "Feature X is confusing" → Improve UI/UX
  - "I wish I could do Y" → Add feature (if quick)
  - "It's slow" → Optimize performance
  - "I don't understand scores" → Better explanations

- [ ] Bug fixes:
  - Prioritize critical bugs (data loss, crashes)
  - Fix in 24 hours (for beta users)

- [ ] Quick wins:
  - UI tweaks (better labels, tooltips)
  - Onboarding improvements
  - Bug fixes

**Deliverables:**
- 20-50 beta users recruited
- Onboarding sequence (emails, calls)
- Feedback collected (surveys, interviews)
- Iterations based on feedback (bug fixes, UX improvements)

**Learning Focus:**
- Customer development
- Feedback collection
- Product iteration
- User onboarding

---

#### Week 6: Public Launch
**Focus:** Launch to the world, acquire customers

**Tasks:**

**Day 1: Pre-Launch Preparation**
- [ ] Final checklist:
  - ✅ All critical bugs fixed
  - ✅ Beta users happy (NPS > 8/10)
  - ✅ Marketing site live
  - ✅ Billing working (Stripe tested)
  - ✅ Support system ready
  - ✅ Monitoring & alerts configured
  - ✅ Legal (privacy policy, terms of service)
  - ✅ Analytics (Google Analytics, Mixpanel)

- [ ] Launch assets:
  - Product screenshots (dashboard, matching, analytics)
  - Demo video (2-minute walkthrough)
  - Logo (high-res PNG, SVG)
  - Press kit (for journalists)

**Day 2: Product Hunt Launch**
- [ ] Prepare Product Hunt submission:
  - **Tagline:** "AI-powered resume screening that saves 90% of your time"
  - **Description:** Problem, solution, key features
  - **Media:** Screenshots, demo video
  - **Makers:** Add yourself (profile photo, bio)
  - **First comment:** Introduce yourself, share story

- [ ] Launch strategy:
  - Submit at 12:01 AM PST (Product Hunt day starts)
  - Share with network (upvote, comment)
  - Respond to every comment (engage)
  - Goal: Top 5 of the day (get "Product of the Day" badge)

**Day 3: Social Media Blitz**
- [ ] Twitter/X launch:
  - Thread (10+ tweets):
    - Tweet 1: "Today we're launching IntelliMatch AI! 🚀"
    - Tweet 2: "The problem: Recruiters spend 80% of time on admin"
    - Tweet 3: "Our solution: AI screens resumes in seconds"
    - Tweet 4-8: Key features (with GIFs)
    - Tweet 9: "Try free for 14 days"
    - Tweet 10: "Thank you to beta users!"
  
  - Engage with replies
  - Retweet mentions
  - Join relevant conversations (#recruiting, #AI)

- [ ] LinkedIn launch:
  - Personal post (on your profile)
  - Company page post
  - Share in relevant groups (recruiting, HR tech)
  - Ask connections to share

- [ ] Reddit launch:
  - r/recruiting: "I built an AI tool to help you screen resumes faster"
  - r/SaaS: "Launched my SaaS today! [Launch story]"
  - r/startups: "Lessons from launching my startup"
  - **Be genuine, not spammy** (share journey, ask for feedback)

**Day 4: Content Marketing**
- [ ] Launch blog posts:
  - "Why We Built IntelliMatch AI" (founder story)
  - "How AI Is Transforming Recruitment" (thought leadership)
  - "5 Tips to Screen Resumes 10x Faster" (actionable tips)

- [ ] Guest posts:
  - Pitch to HR Tech blogs (ERE, TLNT, HR Dive)
  - Share expertise (not sales pitch)

- [ ] SEO:
  - Target keywords: "AI resume screening", "automated resume parser", "resume matching software"
  - Create content for each keyword
  - Build backlinks (guest posts, directories)

**Day 5: Outreach & Sales**
- [ ] Direct outreach:
  - LinkedIn messages (recruiters, HR managers)
  - Email (recruiting agencies, HR consultants)
  - Cold email template:
    ```
    Subject: Screen 100 resumes in 5 minutes (not 5 hours)
    
    Hi [Name],
    
    I noticed you're hiring for [role]. Screening resumes is a pain, right?
    
    We just launched IntelliMatch AI - it uses AI to:
    - Parse resumes (PDF, DOCX) in seconds
    - Rank candidates by fit (with explanations)
    - Save you 90% of screening time
    
    Want to try it free for 14 days?
    
    [Your name]
    P.S. Here's a 2-min demo: [link]
    ```

- [ ] Partnerships:
  - Reach out to recruiting agencies (white-label opportunity)
  - ATS companies (integration partnership)
  - HR consultants (affiliate program)

**Day 6: Monitor & Respond**
- [ ] Track metrics:
  - Website traffic (Google Analytics)
  - Signups (conversion rate)
  - Activation rate (% who upload resume)
  - Paying customers (conversion from trial)
  - Churn rate (% who cancel)

- [ ] Respond to feedback:
  - Support tickets (respond within 4 hours)
  - Social media mentions (respond within 1 hour)
  - Product feedback (acknowledge, prioritize)

**Day 7: Celebrate & Reflect**
- [ ] Celebrate launch:
  - Thank beta users (email, social media)
  - Share metrics (if impressive: "100 signups in 24 hours!")
  - Team celebration (if you have team)

- [ ] Reflect on launch:
  - What went well?
  - What could be improved?
  - What surprised you?
  - Key learnings for next launch

**Deliverables:**
- Product Hunt launch (Top 5 of the day - goal)
- Social media campaign (Twitter, LinkedIn, Reddit)
- Content marketing (blog posts, guest posts)
- Direct outreach (100+ prospects contacted)
- First 10+ paying customers acquired
- Launch metrics tracked (traffic, signups, conversions)

**Learning Focus:**
- Product launch strategies
- Social media marketing
- Content marketing
- Sales outreach
- Customer acquisition

---

## 📊 Phase 5 Success Criteria

### Infrastructure
- ✅ Production environment live (AWS/GCP)
- ✅ 99.9% uptime (SLA)
- ✅ Auto-scaling (2-10 instances)
- ✅ Database backups (daily, 7-day retention)
- ✅ CDN configured (CloudFront)

### CI/CD
- ✅ Automated testing (on every commit)
- ✅ Automated deployment (on merge to main)
- ✅ Zero-downtime deployment
- ✅ Rollback procedure (tested)

### Monitoring & Security
- ✅ Monitoring (CloudWatch, Sentry)
- ✅ Alerting (email, Slack, PagerDuty)
- ✅ Security hardened (HTTPS, firewall, rate limiting)
- ✅ Disaster recovery plan (tested)

### Marketing & Billing
- ✅ Marketing site live (landing page, pricing, docs)
- ✅ Stripe integrated (subscriptions working)
- ✅ Support system (help center, chat)

### Launch
- ✅ Beta launch (20-50 users)
- ✅ Public launch (Product Hunt, social media)
- ✅ First 10+ paying customers
- ✅ Customer feedback collected
- ✅ Iterations based on feedback

---

## 🎯 Post-Launch Roadmap (Months 2-12)

### Month 2-3: Product-Market Fit
- Iterate based on feedback
- Double down on what works
- Kill features that don't work
- Achieve NPS > 50

### Month 4-6: Growth
- Content marketing (SEO, blog)
- Paid ads (Google, LinkedIn)
- Partnerships (ATS, recruiting agencies)
- Referral program

### Month 7-9: Scale
- Hire team (engineers, sales, support)
- Enterprise features (SSO, white-label)
- International expansion (EU, Asia)

### Month 10-12: Fundraising (Optional)
- Pitch to investors (seed round)
- Or: Bootstrap to profitability
- Or: Acquisition talks

---

## 💰 Financial Projections

### Revenue Model
- **Starter:** $99/month × 50 customers = $4,950/month
- **Professional:** $299/month × 20 customers = $5,980/month
- **Enterprise:** $999/month × 5 customers = $4,995/month
- **Total MRR (Month 6):** $15,925/month (~$191K/year)

### Costs (Monthly)
- AWS: $500 (infrastructure)
- SendGrid: $100 (email)
- Stripe: 2.9% + $0.30 per transaction (~$500)
- Tools (Sentry, analytics): $200
- Domain, SSL: $50
- **Total costs:** ~$1,350/month

### Profitability
- **Break-even:** ~10 customers (Month 2-3)
- **Profitable:** $14,575/month after Month 6
- **Annual profit (Year 1):** ~$175K (if hitting targets)

---

## ✅ Phase 5 Completion Checklist

### Infrastructure & Deployment
- [ ] Cloud infrastructure setup (AWS/GCP)
- [ ] CI/CD pipeline automated
- [ ] Monitoring & alerting configured
- [ ] Security hardened (penetration test passed)
- [ ] Disaster recovery tested

### Marketing & Billing
- [ ] Marketing site live
- [ ] Stripe integration working
- [ ] Support system operational

### Launch
- [ ] Beta launch complete (20-50 users)
- [ ] Product Hunt launch (Top 5 - goal)
- [ ] Social media campaign executed
- [ ] First 10+ paying customers acquired

### Legal & Compliance
- [ ] Privacy policy published
- [ ] Terms of service published
- [ ] GDPR compliance (if EU customers)
- [ ] Business registered (LLC, Inc.)

---

## 🎉 Congratulations! You've Built a Startup!

By completing all 5 phases, you'll have:
- ✅ **Research-grade ML engine** (Phase 1)
- ✅ **Production backend** (Phase 2)
- ✅ **Professional frontend** (Phase 3)
- ✅ **Advanced features** (Phase 4)
- ✅ **Live product with paying customers** (Phase 5)

**Total timeline:** 9-12 months (November 2025 → August 2026)

**Next steps:**
1. Iterate based on customer feedback
2. Grow to 100+ customers
3. Hire your first team member
4. Raise funding or bootstrap to profitability
5. Exit strategy (acquisition, IPO, or lifestyle business)

---

## 💬 Final Thoughts

### What Makes This Different
- Not just a portfolio project → **Real startup**
- Not just ML demo → **Production SaaS**
- Not just code → **Business + product + customers**

### Key Success Factors
1. **Start with customers** (not tech) → Solve real problem
2. **Ship fast, iterate** → Don't over-engineer
3. **Focus on value** → Features that matter
4. **Talk to users** → Feedback > assumptions
5. **Stay lean** → Bootstrap as long as possible

### When Things Get Hard (They Will)
- Remember why you started
- Talk to happy customers
- Take breaks (avoid burnout)
- Ask for help (community, mentors)
- Celebrate small wins

**You've got this! 🚀**

---

**Questions before starting Phase 5?**

1. **Cloud platform?** AWS (recommended) or GCP or Railway?
2. **Billing?** Stripe (easy) or custom?
3. **Launch channel?** Product Hunt priority or social media blitz?
4. **Support?** Intercom (paid) or custom chat?

**When Phase 4 is complete, come back and we'll start Phase 5 Week 1!** 💪

**Or, if you're ready to start Phase 1 right now, say "start phase 1" and we'll begin Week 1 Day 1!** 🎯

---

*Created: November 1, 2025*  
*Start Date: After Phase 4 completion (July 2026)*  
*Duration: 4-6 weeks*  
*Target: Live product with paying customers by August 2026*  
*Total journey: 9-12 months to launch* 🚀
