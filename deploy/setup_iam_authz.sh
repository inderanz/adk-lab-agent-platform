#!/usr/bin/env bash
# ==============================================================================
# Setup IAM, Agent Identity, and AuthZ Roles for Google Agent Platform
# ==============================================================================
set -euo pipefail

echo "======================================================================"
echo "🔐 Setting up Enterprise IAM & Agent Identities for Agent Platform"
echo "======================================================================"

PROJECT_ID=$(gcloud config get-value project)
REGION=$(gcloud compute project-info describe \
  --format="value(commonInstanceMetadata.items[google-compute-default-region])")
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

echo "Project ID:       $PROJECT_ID"
echo "Region:           $REGION"
echo "Project Number:   $PROJECT_NUMBER"
echo "Service Account:  $SERVICE_ACCOUNT"

# 1. Grant Vertex AI User role for Gemini 3.7 Flash inference
echo "Granting roles/aiplatform.user..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user"

# 2. Grant Cloud Run Invoker role for downstream MCP Server access
echo "Granting roles/run.invoker..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/run.invoker"

# 3. Grant Cloud Trace Agent for distributed telemetry
echo "Granting roles/cloudtrace.agent..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/cloudtrace.agent"

# 4. Grant Cloud Datastore / Firestore User for persistent sessions
echo "Granting roles/datastore.user..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/datastore.user"

echo "======================================================================"
echo "✅ IAM and Agent Identity setup complete!"
echo "======================================================================"
