#!/bin/bash

# Install pySHACL for SHACL validation
echo "Installing pySHACL..."
uv tool install pyshacl

# Alternative: using conda
# conda install -c conda-forge pyshacl

echo "pySHACL installed successfully!"
echo ""
echo "Usage:"
echo "pyshacl -s actions-shapes.ttl -d test-data.ttl -f turtle"
echo ""
echo "Options:"
echo "-s : SHACL shapes file"
echo "-d : Data file to validate"  
echo "-f : Output format (turtle, json-ld, etc.)"
echo "-v : Verbose output"
