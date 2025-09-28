# Deploy

## 🚀 Estratégias de Deploy

### Visão Geral dos Ambientes

```mermaid
graph LR
    DEV[Development] --> TEST[Testing]
    TEST --> STAGE[Staging]
    STAGE --> PROD[Production]

    subgraph "Development"
        DEV_API[FastAPI Dev Server]
        DEV_DB[SQLite Local]
    end

    subgraph "Testing"
        TEST_API[Docker Container]
        TEST_DB[PostgreSQL Test]
    end

    subgraph "Staging"
        STAGE_API[Kubernetes Pod]
        STAGE_DB[PostgreSQL Cloud]
        STAGE_LB[Load Balancer]
    end

    subgraph "Production"
        PROD_API1[API Instance 1]
        PROD_API2[API Instance 2]
        PROD_DB[PostgreSQL Cluster]
        PROD_LB[Load Balancer]
        PROD_CDN[CDN]
    end

    style DEV fill:#e8f5e8
    style TEST fill:#e3f2fd
    style STAGE fill:#fff3e0
    style PROD fill:#ffebee
```

## 🐳 Docker

### Dockerfile de Produção

```dockerfile
# Dockerfile
FROM python:3.13-slim as builder

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN pip install poetry

# Configurar Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

# Copiar arquivos de dependências
COPY pyproject.toml poetry.lock ./

# Instalar dependências
RUN poetry install --only=main && rm -rf $POETRY_CACHE_DIR

# Estágio de runtime
FROM python:3.13-slim as runtime

# Instalar dependências de runtime
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copiar virtual environment
ENV VIRTUAL_ENV=/app/.venv
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copiar código da aplicação
COPY --chown=appuser:appuser . .

# Configurar usuário
USER appuser

# Expor porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health_check || exit 1

# Comando padrão
CMD ["fastapi", "run", "car_api/app.py", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose para Produção

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+psycopg://car_api:${DB_PASSWORD}@db:5432/car_api
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - JWT_ALGORITHM=HS256
      - JWT_EXPIRATION_MINUTES=30
    depends_on:
      - db
      - redis
    restart: unless-stopped
    networks:
      - car_api_network
    volumes:
      - ./logs:/app/logs

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: car_api
      POSTGRES_USER: car_api
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    networks:
      - car_api_network
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    networks:
      - car_api_network
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - api
    restart: unless-stopped
    networks:
      - car_api_network

networks:
  car_api_network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

### Configuração do Nginx

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream car_api {
        server api:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    server {
        listen 80;
        server_name yourdomain.com;

        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        # SSL Configuration
        ssl_certificate /etc/ssl/certs/cert.pem;
        ssl_certificate_key /etc/ssl/certs/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Security Headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

        # API Proxy
        location /api/ {
            # Rate limiting
            limit_req zone=api burst=20 nodelay;

            proxy_pass http://car_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Health Check
        location /health_check {
            proxy_pass http://car_api/health_check;
            access_log off;
        }

        # Static files (if any)
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

## ☸️ Kubernetes

### Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: car-api
  labels:
    app: car-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: car-api
  template:
    metadata:
      labels:
        app: car-api
    spec:
      containers:
      - name: car-api
        image: car-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: car-api-secrets
              key: database-url
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: car-api-secrets
              key: jwt-secret-key
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health_check
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health_check
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: car-api-service
spec:
  selector:
    app: car-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: car-api-ingress
  annotations:
    nginx.ingress.kubernetes.io/rate-limit: "10"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: car-api-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: car-api-service
            port:
              number: 80
```

### Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: car-api-secrets
type: Opaque
data:
  database-url: <base64-encoded-database-url>
  jwt-secret-key: <base64-encoded-jwt-secret>
```

### ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: car-api-config
data:
  JWT_ALGORITHM: "HS256"
  JWT_EXPIRATION_MINUTES: "30"
  LOG_LEVEL: "INFO"
```

## 🔄 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  release:
    types: [ published ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.13'

    - name: Install Poetry
      uses: snok/install-poetry@v1

    - name: Install dependencies
      run: poetry install

    - name: Run tests
      run: |
        poetry run pytest --cov=car_api --cov-fail-under=90
        poetry run ruff check
        poetry run ruff format --check

  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}

    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: staging

    steps:
    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment"
        # Add staging deployment commands here

  deploy-production:
    needs: [build, deploy-staging]
    runs-on: ubuntu-latest
    if: github.event_name == 'release'
    environment: production

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Configure kubectl
      uses: azure/k8s-set-context@v3
      with:
        method: kubeconfig
        kubeconfig: ${{ secrets.KUBE_CONFIG }}

    - name: Deploy to Kubernetes
      run: |
        # Update image tag in deployment
        sed -i 's|car-api:latest|${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.event.release.tag_name }}|g' k8s/deployment.yaml

        # Apply Kubernetes manifests
        kubectl apply -f k8s/

        # Wait for rollout
        kubectl rollout status deployment/car-api

        # Verify deployment
        kubectl get pods -l app=car-api
```

## 🔧 Scripts de Deploy

### Script de Deploy Local

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

echo "🚀 Starting deployment process..."

# 1. Build Docker image
echo "📦 Building Docker image..."
docker build -t car-api:latest .

# 2. Run tests in container
echo "🧪 Running tests..."
docker run --rm car-api:latest poetry run pytest

# 3. Start services
echo "🐳 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# 4. Wait for services
echo "⏳ Waiting for services to be ready..."
sleep 30

# 5. Run migrations
echo "🗃️ Running database migrations..."
docker-compose -f docker-compose.prod.yml exec api poetry run alembic upgrade head

# 6. Health check
echo "🏥 Performing health check..."
if curl -f http://localhost:8000/health_check; then
    echo "✅ Deployment successful!"
else
    echo "❌ Health check failed!"
    exit 1
fi

echo "🎉 Deployment completed successfully!"
```

### Script de Rollback

```bash
#!/bin/bash
# scripts/rollback.sh

set -e

PREVIOUS_VERSION=${1:-"previous"}

echo "🔄 Rolling back to version: $PREVIOUS_VERSION"

# 1. Stop current containers
echo "🛑 Stopping current containers..."
docker-compose -f docker-compose.prod.yml down

# 2. Deploy previous version
echo "📦 Deploying previous version..."
docker tag car-api:$PREVIOUS_VERSION car-api:latest
docker-compose -f docker-compose.prod.yml up -d

# 3. Wait and verify
echo "⏳ Waiting for services..."
sleep 30

# 4. Health check
echo "🏥 Performing health check..."
if curl -f http://localhost:8000/health_check; then
    echo "✅ Rollback successful!"
else
    echo "❌ Rollback failed!"
    exit 1
fi
```

## 🗃️ Gestão de Banco de Dados

### Migrações em Produção

```bash
#!/bin/bash
# scripts/migrate.sh

set -e

echo "🗃️ Running database migrations..."

# 1. Backup database
echo "💾 Creating database backup..."
docker-compose exec db pg_dump -U car_api car_api > "backup_$(date +%Y%m%d_%H%M%S).sql"

# 2. Run migrations
echo "🔄 Running migrations..."
docker-compose exec api poetry run alembic upgrade head

# 3. Verify migrations
echo "✅ Verifying migrations..."
docker-compose exec api poetry run alembic current

echo "🎉 Migrations completed successfully!"
```

### Backup Automatizado

```bash
#!/bin/bash
# scripts/backup.sh

set -e

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="car_api_backup_${DATE}.sql"

echo "💾 Creating database backup..."

# Create backup
docker-compose exec db pg_dump -U car_api -h localhost car_api > "${BACKUP_DIR}/${BACKUP_FILE}"

# Compress backup
gzip "${BACKUP_DIR}/${BACKUP_FILE}"

# Clean old backups (keep last 7 days)
find ${BACKUP_DIR} -name "car_api_backup_*.sql.gz" -mtime +7 -delete

echo "✅ Backup completed: ${BACKUP_FILE}.gz"

# Upload to S3 (optional)
if [ ! -z "$AWS_S3_BUCKET" ]; then
    aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}.gz" "s3://${AWS_S3_BUCKET}/backups/"
    echo "☁️ Backup uploaded to S3"
fi
```

## 📊 Monitoramento

### Prometheus Metrics

```python
# car_api/middleware/metrics.py
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Request, Response
import time

# Métricas
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
DATABASE_QUERIES = Counter('database_queries_total', 'Total database queries')

async def metrics_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    REQUEST_DURATION.observe(time.time() - start_time)

    return response

# Endpoint para métricas
@app.get('/metrics')
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Health Checks Avançados

```python
# car_api/core/health.py
from fastapi import APIRouter
from sqlalchemy import text
from car_api.core.database import engine

router = APIRouter()

@router.get('/health_check')
async def health_check():
    """Health check básico."""
    return {"status": "ok", "timestamp": datetime.utcnow()}

@router.get('/health_check/detailed')
async def detailed_health_check():
    """Health check detalhado."""
    checks = {}

    # Database check
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = {"status": "ok"}
    except Exception as e:
        checks["database"] = {"status": "error", "error": str(e)}

    # Memory check
    import psutil
    memory = psutil.virtual_memory()
    checks["memory"] = {
        "status": "ok" if memory.percent < 90 else "warning",
        "usage_percent": memory.percent
    }

    # Disk check
    disk = psutil.disk_usage('/')
    checks["disk"] = {
        "status": "ok" if disk.percent < 90 else "warning",
        "usage_percent": disk.percent
    }

    overall_status = "ok" if all(
        check["status"] == "ok" for check in checks.values()
    ) else "degraded"

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow(),
        "checks": checks
    }
```

## 🔒 Segurança em Produção

### Configurações de Segurança

```python
# car_api/core/security_config.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

def configure_security(app: FastAPI, settings):
    """Configurar middleware de segurança."""

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    # Trusted Host
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts
    )

    # Security Headers
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response
```

### Variáveis de Ambiente

```bash
# .env.production
# Database
DATABASE_URL=postgresql+psycopg://user:password@host:5432/db

# JWT
JWT_SECRET_KEY=your-production-secret-key-64-chars-minimum
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30

# Security
CORS_ORIGINS=["https://yourdomain.com"]
ALLOWED_HOSTS=["yourdomain.com", "api.yourdomain.com"]

# Monitoring
LOG_LEVEL=INFO
SENTRY_DSN=https://your-sentry-dsn

# Performance
WORKERS=4
MAX_CONNECTIONS=100
```

## 📈 Escalabilidade

### Auto Scaling (Kubernetes)

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: car-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: car-api
  minReplicas: 3
  maxReplicas: 10
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

### Load Balancer (AWS ALB)

```yaml
# aws/alb.yaml
apiVersion: v1
kind: Service
metadata:
  name: car-api-alb
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: car-api
```

## 🚨 Alertas e Notificações

### Alertmanager

```yaml
# alerts/rules.yml
groups:
- name: car-api
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors per second"

  - alert: HighMemoryUsage
    expr: memory_usage_percent > 90
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage"
      description: "Memory usage is {{ $value }}%"

  - alert: DatabaseDown
    expr: up{job="car-api-db"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Database is down"
      description: "Database has been down for more than 1 minute"
```

## 📚 Próximos Passos

Para melhorar o deploy:

1. 📝 [Contribuição](contributing.md) - Como contribuir
2. 📋 [Release Notes](release-notes.md) - Histórico de versões
3. 🔍 Implementar observabilidade completa
4. 🔐 Adicionar secrets management
5. 🌍 Setup multi-region
6. 📊 Dashboard de métricas customizado