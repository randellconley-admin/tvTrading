

# 🏗️ Centralized EC2 Trading Platform Architecture

## 🎯 Single EC2 Instance Design
**Optimized for cost-effectiveness while maintaining enterprise-grade functionality**

### AWS Services Used (Minimal Approach)
- **EC2**: Single instance hosting all components
- **Route53**: Domain management and health checks
- **S3**: Static file storage and backups
- **SNS**: Critical alert notifications only

---

## 🖥️ EC2 Instance Specifications

### Recommended Instance Type
```
Instance: t3.large (2 vCPU, 8 GB RAM)
Storage: 100 GB gp3 SSD
OS: Ubuntu 22.04 LTS
Security Groups: HTTP(80), HTTPS(443), SSH(22)
```

### Instance Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    EC2 Instance (t3.large)                 │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │    Nginx    │  │   Flask     │  │     PostgreSQL      │  │
│  │ (Port 80)   │  │ (Port 5000) │  │    (Port 5432)      │  │
│  │ Reverse     │  │ Trading     │  │   Local Database    │  │
│  │ Proxy       │  │ Platform    │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │    Redis    │  │   Celery    │  │      OpenSearch     │  │
│  │ (Port 6379) │  │  Workers    │  │    (Port 9200)      │  │
│  │   Cache     │  │ Background  │  │   Analytics DB      │  │
│  │             │  │   Tasks     │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              React Dashboard (Static)                  │  │
│  │                 Served by Nginx                        │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Deployment Configuration

### Docker Compose Setup (Single Instance)
```yaml
version: '3.8'

services:
  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - ./frontend/build:/usr/share/nginx/html
    depends_on:
      - flask-app
    restart: unless-stopped

  # Flask Trading Platform
  flask-app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://trading:password@postgres:5432/trading_db
      - REDIS_URL=redis://redis:6379/0
      - ALPACA_PAPER_KEY=${ALPACA_PAPER_KEY}
      - ALPACA_PAPER_SECRET=${ALPACA_PAPER_SECRET}
      - ALPACA_LIVE_KEY=${ALPACA_LIVE_KEY}
      - ALPACA_LIVE_SECRET=${ALPACA_LIVE_SECRET}
    depends_on:
      - postgres
      - redis
      - opensearch
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs

  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=trading_db
      - POSTGRES_USER=trading
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped

  # Redis Cache
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # Celery Worker
  celery-worker:
    build: .
    command: celery -A app.celery worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://trading:password@postgres:5432/trading_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # OpenSearch (Single Node)
  opensearch:
    image: opensearchproject/opensearch:2.11.0
    environment:
      - discovery.type=single-node
      - plugins.security.disabled=true
      - "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - opensearch_data:/usr/share/opensearch/data
    restart: unless-stopped

  # OpenSearch Dashboards
  opensearch-dashboards:
    image: opensearchproject/opensearch-dashboards:2.11.0
    ports:
      - "5601:5601"
    environment:
      - 'OPENSEARCH_HOSTS=["http://opensearch:9200"]'
      - "DISABLE_SECURITY_DASHBOARDS_PLUGIN=true"
    depends_on:
      - opensearch
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  opensearch_data:
```

---

## 🌐 Route53 Configuration

### Domain Setup
```yaml
# Route53 Hosted Zone Configuration
Domain: trading-platform.com
Records:
  - Type: A
    Name: trading-platform.com
    Value: [EC2_ELASTIC_IP]
    TTL: 300
  
  - Type: A  
    Name: api.trading-platform.com
    Value: [EC2_ELASTIC_IP]
    TTL: 300
    
  - Type: A
    Name: dashboard.trading-platform.com  
    Value: [EC2_ELASTIC_IP]
    TTL: 300

# Health Check
Health Check:
  - Protocol: HTTPS
  - Path: /health
  - Port: 443
  - Interval: 30 seconds
```

---

## 📦 S3 Integration (Minimal Usage)

### S3 Buckets
```yaml
Buckets:
  trading-platform-backups:
    Purpose: Database backups and logs
    Lifecycle: Delete after 90 days
    
  trading-platform-static:
    Purpose: Static assets and reports
    Public Read: No
    
  trading-platform-config:
    Purpose: Configuration files and secrets
    Encryption: AES-256
```

### Backup Strategy
```bash
#!/bin/bash
# Daily backup script
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump trading_db > /tmp/db_backup_$DATE.sql
aws s3 cp /tmp/db_backup_$DATE.sql s3://trading-platform-backups/database/

# Application logs
tar -czf /tmp/logs_$DATE.tar.gz /app/logs/
aws s3 cp /tmp/logs_$DATE.tar.gz s3://trading-platform-backups/logs/

# Cleanup local files
rm /tmp/db_backup_$DATE.sql /tmp/logs_$DATE.tar.gz
```

---

## 📱 SNS Integration (Critical Alerts Only)

### SNS Topics
```yaml
Topics:
  trading-platform-critical:
    Purpose: System failures, trading errors
    Subscribers:
      - Email: admin@trading-platform.com
      - SMS: +1234567890
      
  trading-platform-performance:
    Purpose: Performance alerts, high latency
    Subscribers:
      - Email: devops@trading-platform.com
```

### Alert Integration
```python
import boto3

class AlertManager:
    def __init__(self):
        self.sns = boto3.client('sns')
        self.critical_topic = 'arn:aws:sns:us-east-1:123456789:trading-platform-critical'
    
    def send_critical_alert(self, message, subject):
        """Send critical system alerts via SNS"""
        self.sns.publish(
            TopicArn=self.critical_topic,
            Message=message,
            Subject=subject
        )
    
    def trading_error_alert(self, error_details):
        """Alert for trading execution failures"""
        message = f"""
        Trading Error Detected:
        Time: {datetime.utcnow()}
        Error: {error_details['error']}
        Ticker: {error_details.get('ticker', 'Unknown')}
        Signal ID: {error_details.get('signal_id', 'Unknown')}
        """
        self.send_critical_alert(message, "Trading Platform - Execution Error")
```

---

## 🔧 Installation Script

### EC2 Setup Script
```bash
#!/bin/bash
# EC2 Instance Setup for Trading Platform

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Create application directory
mkdir -p /opt/trading-platform
cd /opt/trading-platform

# Clone repository
git clone https://github.com/randellconley-admin/tvTrading.git .

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Start services
docker-compose up -d

# Set up SSL certificate (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d trading-platform.com

# Set up cron jobs
echo "0 2 * * * /opt/trading-platform/scripts/backup.sh" | sudo crontab -

echo "✅ Trading Platform deployed successfully!"
echo "🌐 Access dashboard at: https://trading-platform.com"
echo "📊 Access analytics at: https://trading-platform.com:5601"
```

---

## 📊 Monitoring & Maintenance

### System Monitoring
```python
# Built-in health monitoring
@app.route('/health')
def health_check():
    checks = {
        'database': check_database_connection(),
        'redis': check_redis_connection(),
        'opensearch': check_opensearch_connection(),
        'alpaca_paper': check_alpaca_paper_api(),
        'disk_space': check_disk_space(),
        'memory_usage': check_memory_usage()
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return jsonify({
        'status': 'healthy' if all_healthy else 'unhealthy',
        'checks': checks,
        'timestamp': datetime.utcnow().isoformat()
    }), status_code
```

### Automated Scaling (Vertical)
```bash
#!/bin/bash
# Auto-scaling script for high load periods

CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')

if (( $(echo "$CPU_USAGE > 80" | bc -l) )) || (( $(echo "$MEMORY_USAGE > 80" | bc -l) )); then
    echo "High resource usage detected. Consider upgrading instance."
    # Send SNS alert
    aws sns publish --topic-arn arn:aws:sns:us-east-1:123456789:trading-platform-performance \
        --message "High resource usage: CPU: ${CPU_USAGE}%, Memory: ${MEMORY_USAGE}%"
fi
```

---

## 💰 Cost Optimization

### Monthly Cost Estimate
```
EC2 t3.large (24/7):     ~$60/month
Route53 Hosted Zone:     ~$0.50/month  
S3 Storage (100GB):      ~$2.30/month
SNS (1000 messages):     ~$0.50/month
Data Transfer:           ~$5/month

Total Estimated Cost:    ~$68/month
```

### Cost Savings Features
- Single instance deployment
- Local PostgreSQL (no RDS)
- Local OpenSearch (no managed service)
- Minimal S3 usage
- SNS only for critical alerts
- No Load Balancer (single instance)

---

## 🔒 Security Considerations

### Security Measures
- SSL/TLS encryption via Let's Encrypt
- Firewall rules (UFW) restricting access
- Regular security updates via cron
- API key encryption at rest
- Database connection encryption
- Nginx rate limiting
- Fail2ban for SSH protection

### Backup & Recovery
- Daily automated backups to S3
- Database point-in-time recovery
- Configuration version control
- Disaster recovery documentation

This centralized architecture provides enterprise-grade trading automation while maintaining cost-effectiveness and simplicity through single EC2 instance deployment.


