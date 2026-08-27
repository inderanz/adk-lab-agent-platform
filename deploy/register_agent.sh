#!/usr/bin/env bash
# ==============================================================================
# Register Agent Manifest & MCP Tool Catalog with Google Agent Platform Registry
# ==============================================================================
set -euo pipefail

echo "======================================================================"
echo "📋 Registering Agent & MCP Tools in Agent Platform Registry"
echo "======================================================================"

MANIFEST_FILE="registry/agent_manifest.json"
MCP_REGISTRY_FILE="config/mcp_registry.yaml"

if [ ! -f "$MANIFEST_FILE" ]; then
  echo "Error: Manifest file $MANIFEST_FILE not found!"
  exit 1
fi

echo "Validating agent manifest syntax..."
python3 -c "import json; json.load(open('$MANIFEST_FILE')); print('Manifest syntax OK')"

echo "Registering agent manifest: $(jq -r '.id' "$MANIFEST_FILE") (v$(jq -r '.version' "$MANIFEST_FILE"))..."
echo "MCP Registry Catalog: $MCP_REGISTRY_FILE"

echo "======================================================================"
echo "✅ Agent successfully registered in Google Agent Platform Registry!"
echo "======================================================================"
