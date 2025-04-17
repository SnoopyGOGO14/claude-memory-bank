#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Sovereign AI Agents server...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker not found. Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Docker Compose not found. Installing Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create data directories
echo -e "${GREEN}Creating data directories...${NC}"
mkdir -p data/SORTED_DOCUMENTS

# Check if .env file exists, if not create from example
if [ ! -f .env ]; then
    echo -e "${YELLOW}.env file not found. Creating from example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please edit the .env file with your API keys and configuration.${NC}"
    echo -e "${YELLOW}Press Enter to continue after editing...${NC}"
    read
fi

# Build and start the containers
echo -e "${GREEN}Building and starting containers...${NC}"
docker-compose up -d

echo -e "${GREEN}Server setup complete!${NC}"
echo -e "${GREEN}You can access the agent service at http://localhost:8050${NC}"
echo -e "${GREEN}To check logs, run: docker-compose logs -f agent-service${NC}" 