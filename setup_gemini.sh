#!/bin/bash

# Setup script for Gemini API configuration
# This script helps configure the Gemini API for the CEFR Evaluation pipeline

set -e

PROJECT_DIR="/Users/hshekar/CEFR Evaluation"
cd "$PROJECT_DIR"

echo "======================================================================="
echo "CEFR Evaluation Pipeline - Gemini API Setup"
echo "======================================================================="
echo ""

# Check if .env file exists
if [ -f ".env" ]; then
    echo "✅ .env file found"
    echo ""
    echo "Current environment variables:"
    cat .env
    echo ""
    read -p "Do you want to update the GEMINI_API_KEY? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping API key update"
        echo ""
    else
        read -p "Enter your Gemini API key: " gemini_key
        # Remove existing GEMINI_API_KEY line and add new one
        grep -v "GEMINI_API_KEY" .env > .env.tmp && mv .env.tmp .env || true
        echo "GEMINI_API_KEY=$gemini_key" >> .env
        echo "✅ API key updated in .env"
    fi
else
    echo "⚠️  .env file not found. Creating one..."
    read -p "Enter your Gemini API key (or press Enter to skip): " gemini_key

    if [ -z "$gemini_key" ]; then
        echo "Skipping .env creation"
    else
        cat > .env << EOF
# Gemini API Configuration
GEMINI_API_KEY=$gemini_key

# Optional: Other API keys
# OPENAI_API_KEY=sk-...
# OPENROUTER_API_KEY=sk-or-...
EOF
        echo "✅ .env file created with GEMINI_API_KEY"
    fi
fi

echo ""
echo "======================================================================="
echo "Installing required dependencies..."
echo "======================================================================="
echo ""

pip install google-generativeai

echo ""
echo "✅ google-generativeai installed successfully"
echo ""

echo "======================================================================="
echo "Configuration Summary"
echo "======================================================================="
echo ""
echo "To use Gemini API, make sure config.py has:"
echo ""
echo "  API_PROVIDER = \"gemini\""
echo "  MODEL_NAME = \"gemini-1.5-flash\"  # or gemini-1.5-pro"
echo ""
echo "Then run: python main.py"
echo ""
echo "For more information, see: GEMINI_API_SETUP.md"
echo ""
