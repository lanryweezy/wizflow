#!/bin/bash
# WizFlow Installation Script

set -e

echo "🧙‍♂️ Installing WizFlow - AI-Powered Automation CLI Tool"
echo "=================================================="

# Check Python version
python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
echo "📋 Python version: $python_version"

if [[ $(python3 -c "import sys; print(sys.version_info >= (3, 7))") == "False" ]]; then
    echo "❌ Python 3.7 or higher is required"
    exit 1
fi

# Install in development mode
echo "📦 Installing WizFlow..."
pip3 install -e .

# Verify installation
echo "✅ Testing installation..."
if command -v wizflow &> /dev/null; then
    echo "🎉 WizFlow installed successfully!"
    echo ""
    echo "🚀 Quick start:"
    echo "  wizflow \"Send me an email reminder every Friday\""
    echo "  wizflow list"
    echo "  wizflow --help"
    echo ""
    echo "📚 See README.md for more examples and configuration options"
else
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi
