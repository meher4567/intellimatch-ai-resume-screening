# Production Deployment Checklist

## Pre-Deployment Checks

### 1. Security
- [ ] Change `SECRET_KEY` in `.env` to a strong random value
- [ ] Set `DEBUG=False` in production
- [ ] Update `CORS_ORIGINS` to only allow your frontend domain
- [ ] Review and restrict database permissions
- [ ] Enable HTTPS/SSL certificates
- [ ] Set up API key authentication for sensitive endpoints
- [ ] Review all environment variables for sensitive data

### 2. Database
- [ ] Run all Alembic migrations: `alembic upgrade head`
- [ ] Set up database backups (automated daily)
- [ ] Configure connection pooling
- [ ] Set up read replicas for scaling (optional)
- [ ] Index optimization for frequently queried fields
- [ ] Set up database monitoring

### 3. Configuration
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure production database URL
- [ ] Set up Redis for caching and rate limiting
- [ ] Configure SMTP for email notifications
- [ ] Set proper file upload limits
- [ ] Configure logging to external service (e.g., CloudWatch, Datadog)

### 4. Infrastructure
- [ ] Set up load balancer (if needed)
- [ ] Configure CDN for static assets
- [ ] Set up auto-scaling policies
- [ ] Configure health check endpoints
- [ ] Set up monitoring and alerting
- [ ] Configure backup and disaster recovery

### 5. ML Models
- [ ] Download and verify all required models
- [ ] Test model inference performance
- [ ] Set up model versioning
- [ ] Configure GPU if available
- [ ] Pre-load models in memory for faster response

### 6. API Documentation
- [ ] Review Swagger UI at `/docs`
- [ ] Verify all endpoints are documented
- [ ] Check example requests/responses
- [ ] Update API version if changed

### 7. Performance
- [ ] Enable response compression (gzip)
- [ ] Set up caching for frequently accessed data
- [ ] Optimize database queries (check for N+1 problems)
- [ ] Configure connection pooling
- [ ] Set up CDN for static files
- [ ] Implement pagination on all list endpoints

### 8. Monitoring & Logging
- [ ] Set up application monitoring (New Relic, Datadog, etc.)
- [ ] Configure error tracking (Sentry)
- [ ] Set up log aggregation (ELK, CloudWatch)
- [ ] Create dashboards for key metrics
- [ ] Set up alerts for errors and performance issues
- [ ] Monitor rate limit violations

### 9. Testing
- [ ] Run full test suite: `pytest tests/`
- [ ] Perform load testing
- [ ] Test file upload limits
- [ ] Verify rate limiting works
- [ ] Test authentication flow
- [ ] Verify email notifications (if configured)

### 10. Documentation
- [ ] Update README with production setup
- [ ] Document deployment process
- [ ] Create runbook for common issues
- [ ] Document rollback procedure
- [ ] Update API documentation version

## Deployment Steps

### Using Docker

1. **Build the image:**
   ```bash
   docker build -t intellimatch-api:latest .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name intellimatch-api \
     -p 8000:8000 \
     --env-file .env.production \
     -v $(pwd)/data:/app/data \
     intellimatch-api:latest
   ```

3. **Verify deployment:**
   ```bash
   curl http://localhost:8000/health
   ```

### Using Docker Compose

1. **Start all services:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Check logs:**
   ```bash
   docker-compose -f docker-compose.prod.yml logs -f api
   ```

### Manual Deployment

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

2. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

3. **Start server:**
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

## Post-Deployment

### 1. Smoke Tests
- [ ] Health check: `GET /health`
- [ ] API docs: `GET /docs`
- [ ] Authentication: `POST /api/v1/auth/login`
- [ ] Upload resume: `POST /api/v1/resumes/upload`
- [ ] Find matches: `POST /api/v1/matches/find`

### 2. Monitoring
- [ ] Check application logs
- [ ] Verify database connections
- [ ] Monitor CPU/Memory usage
- [ ] Check rate limit statistics
- [ ] Review error rates

### 3. Performance Baselines
- [ ] Measure average response time
- [ ] Check concurrent user capacity
- [ ] Verify rate limits are working
- [ ] Test file upload performance

## Rollback Plan

If issues occur:

1. **Quick rollback:**
   ```bash
   docker-compose -f docker-compose.prod.yml down
   docker-compose -f docker-compose.prod.yml up -d --no-deps api-previous
   ```

2. **Database rollback:**
   ```bash
   alembic downgrade -1
   ```

3. **Check logs:**
   ```bash
   tail -f app.log
   ```

## Environment Variables Checklist

### Required
- `SECRET_KEY` - Strong random key
- `DATABASE_URL` - Production database
- `DEBUG=False`
- `ENVIRONMENT=production`

### Optional but Recommended
- `REDIS_URL` - For caching
- `SMTP_*` - For email notifications
- `SENTRY_DSN` - For error tracking
- `CORS_ORIGINS` - Restrict to frontend domain

## Security Best Practices

1. **Never commit:**
   - `.env` files
   - Database credentials
   - Secret keys
   - API keys

2. **Use secrets management:**
   - AWS Secrets Manager
   - HashiCorp Vault
   - Azure Key Vault

3. **Regular updates:**
   - Update dependencies monthly
   - Patch security vulnerabilities immediately
   - Rotate credentials quarterly

## Performance Tuning

### Database
- Connection pool: 10-20 connections
- Query timeout: 30 seconds
- Enable query logging in development only

### API
- Workers: 2 * CPU cores + 1
- Max requests per worker: 1000
- Request timeout: 60 seconds
- Rate limit: 100 requests/minute per IP

### File Upload
- Max size: 10MB
- Allowed types: PDF, DOCX, DOC
- Scan for viruses in production

## Monitoring Metrics

Track these key metrics:

- **Request rate**: requests/second
- **Response time**: p50, p95, p99
- **Error rate**: 4xx, 5xx percentage
- **Database**: query time, connection pool usage
- **ML inference**: model loading time, prediction time
- **Rate limiting**: violations per hour
- **File uploads**: success rate, average size

## Support Contacts

- **DevOps**: devops@intellimatch.ai
- **On-call**: +1-XXX-XXX-XXXX
- **Incident Slack**: #incidents

---

**Last Updated**: November 24, 2025
**Version**: 1.0.0
