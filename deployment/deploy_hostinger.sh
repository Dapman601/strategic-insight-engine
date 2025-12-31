#!/bin/bash

# Hostinger Deployment Script for Weekly Strategic Insight Engine
# This script deploys the Docker containerized application to Hostinger VPS

set -e

echo "=========================================="
echo "Hostinger Deployment Script"
echo "Weekly Strategic Insight Engine"
echo "=========================================="

# Configuration
APP_NAME="strategic-insight"
DEPLOY_DIR="/opt/${APP_NAME}"
BACKUP_DIR="/opt/${APP_NAME}-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "Please run as root (use sudo)"
    exit 1
fi

# Check prerequisites
log_info "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose is not installed. Installing..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

log_info "Prerequisites OK"

# Create deployment directory
log_info "Creating deployment directory..."
mkdir -p ${DEPLOY_DIR}
mkdir -p ${BACKUP_DIR}

# Backup existing installation if it exists
if [ -d "${DEPLOY_DIR}" ] && [ "$(ls -A ${DEPLOY_DIR})" ]; then
    log_warn "Existing installation found. Creating backup..."
    tar -czf "${BACKUP_DIR}/backup_${TIMESTAMP}.tar.gz" -C ${DEPLOY_DIR} . 2>/dev/null || true
    log_info "Backup created: ${BACKUP_DIR}/backup_${TIMESTAMP}.tar.gz"
fi

# Stop existing containers
log_info "Stopping existing containers..."
cd ${DEPLOY_DIR}
docker-compose down 2>/dev/null || true

# Copy application files
log_info "Deploying application files..."
cp -r ./* ${DEPLOY_DIR}/

# Check for .env file
if [ ! -f "${DEPLOY_DIR}/.env" ]; then
    log_warn ".env file not found. Copying from .env.production template..."
    cp ${DEPLOY_DIR}/.env.production ${DEPLOY_DIR}/.env
    log_error "IMPORTANT: Edit ${DEPLOY_DIR}/.env with your actual credentials before continuing!"
    exit 1
fi

# Build and start containers
log_info "Building Docker images..."
cd ${DEPLOY_DIR}
docker-compose build

log_info "Starting containers..."
docker-compose up -d

# Wait for services to be healthy
log_info "Waiting for services to start..."
sleep 10

# Check service health
log_info "Checking service health..."
docker-compose ps

# Test API endpoint
log_info "Testing API endpoint..."
if curl -f http://localhost:8000/health &>/dev/null; then
    log_info "API is healthy!"
else
    log_error "API health check failed!"
    docker-compose logs api
    exit 1
fi

# Display logs
log_info "Recent logs:"
docker-compose logs --tail=50

echo ""
echo "=========================================="
log_info "Deployment completed successfully!"
echo "=========================================="
echo ""
echo "Service Status:"
docker-compose ps
echo ""
echo "Access the API at: http://your-server-ip:8000"
echo "Health check: http://your-server-ip:8000/health"
echo "Stats: http://your-server-ip:8000/stats"
echo ""
echo "To view logs: cd ${DEPLOY_DIR} && docker-compose logs -f"
echo "To restart: cd ${DEPLOY_DIR} && docker-compose restart"
echo "To stop: cd ${DEPLOY_DIR} && docker-compose down"
echo ""
echo "Weekly processing runs every Monday at 9 AM UTC"
echo "Manual run: docker exec insight-processor python scripts/weekly_run.py"
echo "=========================================="
