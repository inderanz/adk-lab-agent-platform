#!/usr/bin/env bash
# ==============================================================================
# Deploy Enterprise Multi-Agent System to Cloud Run & Google Agent Platform
# ==============================================================================
set -euo pipefail

echo "======================================================================"
echo "🚀 Deploying Enterprise ADK 2.x Agent to Google Agent Platform"
echo "======================================================================"

# Load environment configuration if present
if [ -f .env ]; then
  source .env
fi

PROJECT_ID=$(gcloud config get-value project)
REGION=$(gcloud compute project-info describe \
  --format="value(commonInstanceMetadata.items[google-compute-default-region])")
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
SERVICE_NAME="zoo-tour-guide-enterprise"

echo "Project:      $PROJECT_ID"
echo "Region:       $REGION"
echo "Service:      $SERVICE_NAME"
echo "Model:        ${MODEL:-gemini-3.7-flash}"
echo "MCP Endpoint: ${MCP_SERVER_URL:-https://zoo-mcp-server-${PROJECT_NUMBER}.${REGION}.run.app/mcp/}"

# Deploy using ADK 2.x CLI with enterprise telemetry & UI
echo "Launching ADK deployment..."
adk deploy cloud_run \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --service_name="$SERVICE_NAME" \
  --trace_to_cloud \
  --otel_to_cloud \
  --with_ui \
  src/ \
  -- \
  --allow-unauthenticated

# Update runtime environment configuration
echo "Configuring enterprise environment variables and metadata labels..."
gcloud run services update "$SERVICE_NAME" \
  --region="$REGION" \
  --update-labels=tier=enterprise,framework=adk-2x,app=zoo-tour-guide \
  --set-env-vars="MODEL=${MODEL:-gemini-3.7-flash},MCP_SERVER_URL=${MCP_SERVER_URL:-https://zoo-mcp-server-${PROJECT_NUMBER}.${REGION}.run.app/mcp/},GOOGLE_CLOUD_LOCATION=global,PROJECT_ID=${PROJECT_ID}"

SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)")

echo "======================================================================"
echo "🎉 Deployment successful!"
echo "Service URL: $SERVICE_URL"
echo "======================================================================"
