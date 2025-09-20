#!/bin/bash

# Trading Automation Platform - Deployment Script
# Multi-Team Coordination: DevOps Team Lead

set -e

echo "🚀 Trading Automation Platform Deployment"
echo "=========================================="

# Configuration
PROJECT_NAME="trading-platform"
DOMAIN=${DOMAIN:-"trading-platform.com"}
ENV=${ENV:-"production"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check AWS CLI (optional)
    if ! command -v aws &> /dev/null; then
        log_warning "AWS CLI not found - S3 backups will be disabled"
    fi
    
    log_success "Prerequisites check completed"
}

# Setup environment
setup_environment() {
    log_info "Setting up environment..."
    
    # Create necessary directories
    mkdir -p logs/{nginx,flask,postgres}
    mkdir -p backups/{database,logs}
    mkdir -p ssl
    mkdir -p charts/{mplfinance,plotly}
    mkdir -p webhooks
    
    # Copy environment template if not exists
    if [ ! -f .env ]; then
        log_info "Creating .env file from template..."
        cat > .env << EOF
# Trading Platform Configuration
FLASK_ENV=${ENV}
SECRET_KEY=$(openssl rand -hex 32)

# Database Configuration
DATABASE_URL=postgresql://trading:$(openssl rand -hex 16)@postgres:5432/trading_db
POSTGRES_DB=trading_db
POSTGRES_USER=trading
POSTGRES_PASSWORD=$(openssl rand -hex 16)

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Alpaca API Keys (REQUIRED - Set your actual keys)
ALPACA_PAPER_KEY=your_paper_key_here
ALPACA_PAPER_SECRET=your_paper_secret_here
ALPACA_LIVE_KEY=your_live_key_here
ALPACA_LIVE_SECRET=your_live_secret_here

# AWS Configuration (Optional)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_DEFAULT_REGION=us-east-1
S3_BACKUP_BUCKET=trading-platform-backups

# Domain Configuration
DOMAIN=${DOMAIN}
EOF
        log_warning "Please edit .env file with your actual API keys before continuing"
        log_warning "Especially set your Alpaca API keys for trading functionality"
    fi
    
    log_success "Environment setup completed"
}

# Build and start services
deploy_services() {
    log_info "Building and deploying services..."
    
    # Build custom images
    log_info "Building Flask application..."
    docker-compose build
    
    # Start services
    log_info "Starting services..."
    docker-compose up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to start..."
    sleep 30
    
    # Check service health
    if docker-compose ps | grep -q "Up"; then
        log_success "Services started successfully"
    else
        log_error "Some services failed to start"
        docker-compose logs
        exit 1
    fi
}

# Setup SSL certificate
setup_ssl() {
    if [ "$ENV" = "production" ]; then
        log_info "Setting up SSL certificate..."
        
        # Install certbot if not present
        if ! command -v certbot &> /dev/null; then
            log_info "Installing certbot..."
            sudo apt update
            sudo apt install -y certbot python3-certbot-nginx
        fi
        
        # Generate SSL certificate
        log_info "Generating SSL certificate for ${DOMAIN}..."
        sudo certbot --nginx -d ${DOMAIN} --non-interactive --agree-tos --email admin@${DOMAIN}
        
        log_success "SSL certificate configured"
    else
        log_info "Skipping SSL setup for development environment"
    fi
}

# Setup monitoring and backups
setup_monitoring() {
    log_info "Setting up monitoring and backups..."
    
    # Create backup script
    cat > bin/backup.sh << 'EOF'
#!/bin/bash
# Automated backup script

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/trading-platform/backups"

# Database backup
docker-compose exec -T postgres pg_dump -U trading trading_db > ${BACKUP_DIR}/database/db_backup_${DATE}.sql

# Application logs backup
tar -czf ${BACKUP_DIR}/logs/logs_${DATE}.tar.gz logs/

# Upload to S3 if configured
if [ ! -z "$S3_BACKUP_BUCKET" ]; then
    aws s3 cp ${BACKUP_DIR}/database/db_backup_${DATE}.sql s3://${S3_BACKUP_BUCKET}/database/
    aws s3 cp ${BACKUP_DIR}/logs/logs_${DATE}.tar.gz s3://${S3_BACKUP_BUCKET}/logs/
fi

# Cleanup old backups (keep last 7 days)
find ${BACKUP_DIR} -name "*.sql" -mtime +7 -delete
find ${BACKUP_DIR} -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: ${DATE}"
EOF
    
    chmod +x bin/backup.sh
    
    # Setup cron job for backups
    if [ "$ENV" = "production" ]; then
        log_info "Setting up daily backups..."
        (crontab -l 2>/dev/null; echo "0 2 * * * /opt/trading-platform/bin/backup.sh") | crontab -
    fi
    
    log_success "Monitoring and backups configured"
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    # Check Flask application
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        log_success "Flask application is healthy"
    else
        log_error "Flask application health check failed"
        return 1
    fi
    
    # Check database connection
    if docker-compose exec -T postgres pg_isready -U trading > /dev/null 2>&1; then
        log_success "Database is healthy"
    else
        log_error "Database health check failed"
        return 1
    fi
    
    # Check Redis
    if docker-compose exec -T redis redis-cli ping | grep -q PONG; then
        log_success "Redis is healthy"
    else
        log_error "Redis health check failed"
        return 1
    fi
    
    log_success "All health checks passed"
}

# Display deployment summary
deployment_summary() {
    echo ""
    echo "🎯 DEPLOYMENT COMPLETE!"
    echo "======================"
    echo ""
    echo "📊 Services Status:"
    docker-compose ps
    echo ""
    echo "🌐 Access Points:"
    echo "   • Main Application: http://localhost:5000"
    echo "   • Health Check: http://localhost:5000/health"
    echo "   • API Documentation: http://localhost:5000/api/docs"
    echo ""
    if [ "$ENV" = "production" ]; then
        echo "   • Production URL: https://${DOMAIN}"
        echo ""
    fi
    echo "📋 Next Steps:"
    echo "   1. Edit .env file with your Alpaca API keys"
    echo "   2. Configure TradingView webhooks to point to your domain"
    echo "   3. Test with paper trading before going live"
    echo ""
    echo "📊 Monitoring:"
    echo "   • Logs: docker-compose logs -f"
    echo "   • Backups: ./bin/backup.sh"
    echo "   • Health: curl http://localhost:5000/health"
    echo ""
    log_success "Trading Automation Platform is ready! 🚀"
}

# Main deployment flow
main() {
    log_info "Starting deployment process..."
    
    check_prerequisites
    setup_environment
    deploy_services
    
    if [ "$ENV" = "production" ]; then
        setup_ssl
    fi
    
    setup_monitoring
    
    # Wait a bit for services to fully initialize
    sleep 10
    
    if health_check; then
        deployment_summary
    else
        log_error "Deployment completed but health checks failed"
        log_error "Check logs with: docker-compose logs"
        exit 1
    fi
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "health")
        health_check
        ;;
    "backup")
        ./bin/backup.sh
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "stop")
        log_info "Stopping services..."
        docker-compose down
        log_success "Services stopped"
        ;;
    "restart")
        log_info "Restarting services..."
        docker-compose restart
        log_success "Services restarted"
        ;;
    *)
        echo "Usage: $0 {deploy|health|backup|logs|stop|restart}"
        echo ""
        echo "Commands:"
        echo "  deploy   - Full deployment (default)"
        echo "  health   - Run health checks"
        echo "  backup   - Run backup manually"
        echo "  logs     - Show service logs"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        exit 1
        ;;
esac

