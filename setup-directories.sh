#!/bin/bash

# NeuroInsight - Directory Setup Script
# Creates required data directories for uploads and outputs

echo "=========================================="
echo "  NeuroInsight Directory Setup"
echo "=========================================="
echo ""

# Create data directories
echo "Creating data directories..."
mkdir -p data/uploads
mkdir -p data/outputs
mkdir -p data/logs

# Set permissions (make them writable by Docker containers)
chmod 755 data
chmod 777 data/uploads
chmod 777 data/outputs
chmod 777 data/logs

echo "✓ Created: data/uploads"
echo "✓ Created: data/outputs"
echo "✓ Created: data/logs"
echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "You can now run: docker-compose up -d"
echo ""
