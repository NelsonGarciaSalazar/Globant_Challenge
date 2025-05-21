#!/bin/bash

# ACR variables
ACR_NAME="globantregistry"
ACR_LOGIN_SERVER="${ACR_NAME}.azurecr.io"
IMAGE_NAME="$ACR_LOGIN_SERVER/globant_challenge:latest"
RESOURCE_GROUP="Globant_Challenge"
ACI_WORKER_NAME="globant-celery-worker"

# Redis (Azure Cache)
REDIS_PASSWORD="QYIdF9GKf2GLNkZgZfUcdAPH9GmeP2chLAzCaCxtGrk"
REDIS_HOST="globantchallenge-redis.redis.cache.windows.net"
REDIS_PORT_TLS=6380
REDIS_URL="rediss://:$REDIS_PASSWORD@$REDIS_HOST:$REDIS_PORT_TLS/0"

# Azure Web App
WEBAPP_NAME="GlobantChallenge"

echo "🚀 Building and pushing image to ACR..."
docker buildx build --platform linux/amd64 -t $IMAGE_NAME --push .

echo "🔁 Restarting Azure Web App..."
az webapp restart --name $WEBAPP_NAME --resource-group $RESOURCE_GROUP

echo "🔐 Getting ACR credentials..."
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query "username" -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

echo "🧹 Deleting previous Celery Worker (if exists)..."
az container delete \
  --resource-group $RESOURCE_GROUP \
  --name $ACI_WORKER_NAME \
  --yes

echo "🚀 Deploying new Celery Worker using ACR image..."
az container create \
  --resource-group $RESOURCE_GROUP \
  --name $ACI_WORKER_NAME \
  --image $IMAGE_NAME \
  --os-type Linux \
  --cpu 1 --memory 1.5 \
  --environment-variables \
    CELERY_BROKER_URL="$REDIS_URL" \
    CELERY_RESULT_BACKEND="$REDIS_URL" \
  --command-line "celery -A celery_worker.celery_app worker --loglevel=info" \
  --location westus \
  --registry-login-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD

echo "✅ Celery Worker deployed with ACR image."
