#!/usr/bin/env bash
set -euo pipefail

RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-rg-logo-verification-poc}"
LOCATION="${AZURE_LOCATION:-westeurope}"
SUBSCRIPTION_ID="${AZURE_SUBSCRIPTION_ID:-}"

if [[ -n "$SUBSCRIPTION_ID" ]]; then
  az account set --subscription "$SUBSCRIPTION_ID"
fi

az group create --name "$RESOURCE_GROUP" --location "$LOCATION"

az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file infra/bicep/main.bicep \
  --parameters infra/bicep/main.parameters.json
