#!/bin/bash
# Caldera Initialization Script
# This script helps set up a new Caldera installation with secure defaults

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "  _____      _     _                 _____      _ _   "
echo " / ____|    | |   | |               |_   _|    (_) |  "
echo "| |     __ _| | __| | ___ _ __ __ _   | |  _ __ _| |_ "
echo "| |    / _\` | |/ _\` |/ _ \ '__/ _\` |  | | | '__| | __|"
echo "| |___| (_| | | (_| |  __/ | | (_| | _| |_| |  | | |_ "
echo " \_____\__,_|_|\__,_|\___|_|  \__,_||_____|_|  |_|\__|"
echo -e "${NC}"
echo -e "${GREEN}Caldera Initialization Script${NC}"
echo -e "This script will help you set up a secure Caldera installation.\n"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Create .env file
echo -e "${BLUE}Creating .env file...${NC}"
if [ -f .env ]; then
    echo -e "${YELLOW}Warning: .env file already exists. Creating .env.new instead.${NC}"
    ENV_FILE=".env.new"
else
    ENV_FILE=".env"
fi

# Generate random values
ADMIN_PASSWORD=$(openssl rand -hex 8)
API_KEY_RED=$(openssl rand -hex 16)
API_KEY_BLUE=$(openssl rand -hex 16)
CRYPT_SALT=$(openssl rand -hex 8)
ENCRYPTION_KEY=$(openssl rand -hex 16)

# Create .env file
cat > $ENV_FILE << EOF
# Caldera Environment Configuration
# Generated on $(date)

# Version tag for the Docker image
CALDERA_VERSION=latest

# Variant: 'full' includes all plugins and dependencies, 'slim' is a minimal installation
CALDERA_VARIANT=slim

# Timezone
TZ=UTC

# Port configuration
CALDERA_HTTP_PORT=8888
CALDERA_HTTPS_PORT=8443
CALDERA_TCP_PORT=7010
CALDERA_UDP_PORT=7011
CALDERA_WS_PORT=7012
CALDERA_DNS_PORT=8853
CALDERA_SSH_PORT=8022
CALDERA_FTP_PORT=2222

# Configuration path (relative to docker-compose.yml or absolute)
CALDERA_CONFIG_PATH=./conf

# Data volume name
CALDERA_DATA_VOLUME=caldera-data

# Authentication
CALDERA_ADMIN_USER=admin
CALDERA_ADMIN_PASSWORD=$ADMIN_PASSWORD

# API Keys
CALDERA_API_KEY_RED=$API_KEY_RED
CALDERA_API_KEY_BLUE=$API_KEY_BLUE

# Encryption settings
CALDERA_CRYPT_SALT=$CRYPT_SALT
CALDERA_ENCRYPTION_KEY=$ENCRYPTION_KEY

# Additional arguments for the server
CALDERA_ARGS=--environment local
EOF

echo -e "${GREEN}Created $ENV_FILE with secure random values.${NC}"
echo -e "${YELLOW}IMPORTANT: Keep these credentials safe!${NC}"
echo -e "Admin password: ${BLUE}$ADMIN_PASSWORD${NC}"
echo -e "Red API key: ${BLUE}$API_KEY_RED${NC}"
echo -e "Blue API key: ${BLUE}$API_KEY_BLUE${NC}"

# Create a backup of the original docker-compose.yml if it exists
if [ -f docker-compose.yml ]; then
    echo -e "${BLUE}Creating backup of original docker-compose.yml...${NC}"
    cp docker-compose.yml docker-compose.yml.bak
fi

# Check if docker-compose.improved.yml exists
if [ -f docker-compose.improved.yml ]; then
    echo -e "${BLUE}Using improved Docker Compose file...${NC}"
    cp docker-compose.improved.yml docker-compose.yml
    
    # Set default database type to sqlite in .env file
    if [ -f .env ]; then
        if ! grep -q "CALDERA_DB_TYPE" .env; then
            echo -e "\n# Database configuration\nCALDERA_DB_TYPE=sqlite" >> .env
            echo -e "${BLUE}Set default database type to SQLite in .env file${NC}"
        fi
    fi
else
    echo -e "${YELLOW}Warning: docker-compose.improved.yml not found. Using existing docker-compose.yml.${NC}"
fi

# Check if Dockerfile.improved exists
if [ -f Dockerfile.improved ]; then
    echo -e "${BLUE}Using improved Dockerfile...${NC}"
    cp Dockerfile.improved Dockerfile
else
    echo -e "${YELLOW}Warning: Dockerfile.improved not found. Using existing Dockerfile.${NC}"
fi

echo -e "\n${GREEN}Initialization complete!${NC}"
echo -e "To start Caldera, run: ${BLUE}docker-compose up -d${NC}"
echo -e "To view logs, run: ${BLUE}docker-compose logs -f${NC}"
echo -e "To access the web interface, go to: ${BLUE}http://localhost:8888${NC}"
echo -e "Login with username ${BLUE}admin${NC} and password ${BLUE}$ADMIN_PASSWORD${NC}"
