#!/bin/bash

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found"
    exit 1
fi

# Read each line from .env file, ignore empty lines and comments
while IFS= read -r line || [ -n "$line" ]; do
    # Skip empty lines and comments
    if [ -z "$line" ] || [[ $line == \#* ]]; then
        continue
    fi
    
    # Export the variable
    export "$line"
    
done < .env

echo "Environment variables from .env have been exported"