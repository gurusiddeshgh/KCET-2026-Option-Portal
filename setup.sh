#!/usr/bin/env bash

# KCET 2026 Portal - Setup Script
# This script automates the setup process for both backend and frontend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 KCET 2026 Portal Setup Script${NC}"
echo "======================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}⚠️  PostgreSQL is not installed${NC}"
    echo "Please install PostgreSQL: https://www.postgresql.org/download/"
fi

echo -e "${GREEN}✅ All prerequisites found${NC}"
echo ""

# Backend Setup
echo -e "${YELLOW}Setting up Backend...${NC}"
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env with your database credentials${NC}"
fi

cd ..
echo -e "${GREEN}✅ Backend setup complete${NC}"
echo ""

# Frontend Setup
echo -e "${YELLOW}Setting up Frontend...${NC}"
cd frontend

echo "Installing dependencies..."
npm install

if [ ! -f ".env.local" ]; then
    echo "Creating .env.local file..."
    cp .env.local.example .env.local
fi

cd ..
echo -e "${GREEN}✅ Frontend setup complete${NC}"
echo ""

# Database Setup
echo -e "${YELLOW}Setting up Database...${NC}"
echo "Creating PostgreSQL database..."
psql -U postgres -c "CREATE DATABASE kcet_2026;" 2>/dev/null || echo "Database may already exist"

echo "Initializing schema..."
psql -U postgres -d kcet_2026 -f database/schema.sql

echo -e "${GREEN}✅ Database setup complete${NC}"
echo ""

echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your database credentials"
echo "2. Run: cd backend && source venv/bin/activate && python main.py"
echo "3. In another terminal: cd frontend && npm run dev"
echo "4. Visit http://localhost:3000"
