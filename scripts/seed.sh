#!/bin/bash
set -e

# Load environment variables if needed
# source .env

echo "Running database seeding..."

# Run the seed script
python scripts/seed.py

echo "Seeding completed successfully."
