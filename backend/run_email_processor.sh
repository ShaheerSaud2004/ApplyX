#!/bin/bash

# Email Processor Runner for ApplyX
# This script runs the email processor to check for email approvals

cd "$(dirname "$0")"

echo "🔄 Running ApplyX Email Processor..."
echo "⏰ $(date)"

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run the email processor
python3 email_processor.py

echo "✅ Email processor completed at $(date)"
echo "---" 