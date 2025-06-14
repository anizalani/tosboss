# EULA Comparison Platform

A comprehensive platform for comparing End User License Agreements and Terms of Service across major companies to promote consumer awareness and fair competition.

## Project Overview
This platform scrapes, analyzes, and compares EULAs/ToS from major companies, highlighting problematic terms and suggesting consumer-friendly alternatives.

## Architecture
- **Backend**: Python Flask/FastAPI
- **Frontend**: React/Vue.js
- **Database**: PostgreSQL
- **Cache**: Redis
- **Search**: Elasticsearch
- **Deployment**: Docker containers on Linux ARM

## Development Sessions
This project is designed for modular development across multiple LLM sessions:
1. Database & Models
2. Web Scraping Engine  
3. Content Analysis System
4. API Backend
5. Frontend Application
6. Infrastructure & Deployment

## Quick Start
1. Copy `.env.template` to `.env` and configure
2. Run `docker-compose up -d`
3. Access application at `http://localhost:3000`

## Documentation
See `/docs` directory for detailed specifications and session handoffs.