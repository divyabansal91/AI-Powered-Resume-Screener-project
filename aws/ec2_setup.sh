#!/bin/bash
# EC2 Ubuntu Setup Script for AI Resume Screener
# Run: bash ec2_setup.sh

set -e
echo "=== AI Resume Screener — EC2 Setup ==="

# System update
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Docker
echo "--- Installing Docker ---"
sudo apt-get install -y docker.io docker-compose-plugin
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Install Git
sudo apt-get install -y git curl

# Clone the project (replace with your repo URL)
echo "--- Cloning project ---"
# git clone https://github.com/YOUR_USERNAME/AI-Resume-Screening.git
# cd AI-Resume-Screening

# Setup environment file
echo "--- Setting up environment ---"
cp .env.example .env
echo "⚠️  Edit .env with your actual values before running!"

# Build and run with Docker Compose
echo "--- Building Docker image ---"
docker compose build

echo "--- Starting services ---"
docker compose up -d

echo "=== Setup complete! ==="
echo "App running at: http://$(curl -s ifconfig.me):5000"
echo "Health check:   http://$(curl -s ifconfig.me):5000/health"