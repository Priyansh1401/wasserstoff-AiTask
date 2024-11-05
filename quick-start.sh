#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Starting RAG Chatbot Setup...${NC}\n"

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if (( $(echo "$python_version < 3.9" | bc -l) )); then
    echo -e "${RED}Error: Python 3.9 or higher is required${NC}"
    exit 1
fi

# Create project structure
echo -e "${GREEN}Creating project structure...${NC}"
mkdir -p rag-chatbot/{backend,wordpress-plugin}
cd rag-chatbot

# Setup backend
echo -e "${GREEN}Setting up backend...${NC}"
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
echo -e "${GREEN}Installing Python dependencies...${NC}"
pip install --no-cache-dir -r requirements.txt

# Create .env file
echo -e "${GREEN}Creating .env file...${NC}"
cat > .env << EOF
DEBUG=True
API_KEY=development_key
ALLOWED_ORIGINS=["http://localhost"]
EOF

# Start backend server
echo -e "${GREEN}Starting backend server...${NC}"
uvicorn main:app --reload --port 8000 &

# Setup WordPress plugin
echo -e "${GREEN}Setting up WordPress plugin...${NC}"
cd ../wordpress-plugin

# Create plugin directory structure
mkdir -p assets/{css,js}

# Copy plugin files
echo -e "${GREEN}Copying plugin files...${NC}"
# Copy your plugin files here

echo -e "${BLUE}Setup complete!${NC}"
echo -e "Backend running at: http://localhost:8000"
echo -e "Next steps:"
echo -e "1. Copy the WordPress plugin to your wp-content/plugins directory"
echo -e "2. Activate the plugin in WordPress admin panel"
echo -e "3. Update the API URL in the plugin settings"

# Keep script running
wait
