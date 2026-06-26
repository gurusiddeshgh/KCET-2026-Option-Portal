# Configuration Guide

## Environment Variables

### Backend (.env)

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/kcet_2026

# Server Configuration
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Cache Configuration (Optional)
REDIS_URL=redis://localhost:6379/0
CACHE_ENABLED=False
```

### Frontend (.env.local)

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Analytics (Optional)
NEXT_PUBLIC_ANALYTICS_ID=

# Feature Flags
NEXT_PUBLIC_DEBUG_MODE=true
```

### Frontend (.env.production)

```env
# API Configuration - Point to production backend
NEXT_PUBLIC_API_URL=https://api.kcet.example.com/api

# Analytics
NEXT_PUBLIC_ANALYTICS_ID=your-analytics-id

# Feature Flags
NEXT_PUBLIC_DEBUG_MODE=false
```

## Docker Environment

### docker-compose.yml Variables

```yaml
# PostgreSQL
POSTGRES_USER: postgres
POSTGRES_PASSWORD: kcet_password
POSTGRES_DB: kcet_2026

# Backend
DATABASE_URL: postgresql://postgres:kcet_password@postgres:5432/kcet_2026
ENVIRONMENT: development

# Frontend
NEXT_PUBLIC_API_URL: http://localhost:8000/api
```

## Development vs Production

### Development
- Debug mode: ON
- CORS: Allow all origins
- Database: Local PostgreSQL
- Cache: Disabled
- SSL: Not required

### Production
- Debug mode: OFF
- CORS: Whitelist specific origins
- Database: Managed PostgreSQL (AWS RDS)
- Cache: Redis enabled
- SSL: Required (HTTPS)
- Authentication: JWT tokens
- Rate limiting: Enabled
- Logging: Structured (JSON)

## How to Set Environment Variables

### Windows
```batch
# Set in .env file and load via python-dotenv
set DATABASE_URL=postgresql://...
```

### Linux/macOS
```bash
# Set in .env file
export DATABASE_URL=postgresql://...

# Or add to .bashrc/.zshrc for persistence
echo "export DATABASE_URL=postgresql://..." >> ~/.bashrc
```

### Docker
```yaml
environment:
  DATABASE_URL: postgresql://user:password@host:5432/db
  DEBUG: "False"
```

## Database Configuration

### Local PostgreSQL
```
Host: localhost
Port: 5432
User: postgres
Password: your_password
Database: kcet_2026
```

### Production (AWS RDS)
```
Host: kcet-db.c5jblkmq0l1p.us-east-1.rds.amazonaws.com
Port: 5432
User: admin
Password: (from AWS Secrets Manager)
Database: kcet_2026
SSL: Required
```

## API Configuration

### Base URLs
- Local: `http://localhost:8000/api`
- Staging: `https://staging-api.kcet.example.com/api`
- Production: `https://api.kcet.example.com/api`

### Headers
```json
{
  "Content-Type": "application/json",
  "Accept": "application/json"
}
```

## Logging Configuration

### Backend Logging Levels
- DEBUG: Detailed information
- INFO: General information
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical errors

### Frontend Logging
- Console: Development only
- Sentry: Production only

## Cache Configuration

### Redis Configuration
```python
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
```

### Cache Keys
- `cutoffs_{category}`: College cutoffs per category
- `colleges_list`: All colleges
- `courses_list`: All courses
- `student_predictions_{rank}_{category}`: User predictions

## Security Configuration

### CORS (FastAPI)
```python
allow_origins=["http://localhost:3000", "https://example.com"]
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

### Rate Limiting (Nginx)
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req zone=api_limit burst=20 nodelay;
```

## Deployment Configuration

### AWS ECS
```json
{
  "environment": [
    {"name": "DATABASE_URL", "value": "..."},
    {"name": "ENVIRONMENT", "value": "production"}
  ]
}
```

### Heroku
```bash
heroku config:set DATABASE_URL=postgresql://...
heroku config:set ENVIRONMENT=production
```

### Vercel (Frontend)
```bash
vercel env add NEXT_PUBLIC_API_URL
vercel env add NEXT_PUBLIC_ANALYTICS_ID
```

---

For detailed setup instructions, see [README.md](README.md) and [QUICKSTART.md](QUICKSTART.md).
