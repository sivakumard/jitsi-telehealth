#!/bin/bash
# Script to create a new Jitsi user for authenticated meetings

set -e

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <username> <password>"
    echo "Example: $0 doctor1 SecurePassword123"
    exit 1
fi

USERNAME=$1
PASSWORD=$2
DOMAIN="meet.jitsi"

echo "Creating user: $USERNAME@$DOMAIN"

# Check if prosody pod is running
if ! kubectl get deployment prosody -n jitsi &> /dev/null; then
    echo "Error: Prosody deployment not found. Please deploy Jitsi first."
    exit 1
fi

# Get the prosody pod name
POD_NAME=$(kubectl get pod -n jitsi -l component=prosody -o jsonpath='{.items[0].metadata.name}')

if [ -z "$POD_NAME" ]; then
    echo "Error: Prosody pod not found or not running."
    exit 1
fi

echo "Using pod: $POD_NAME"

# Create the user
kubectl exec -it -n jitsi "$POD_NAME" -- prosodyctl --config /config/prosody.cfg.lua register "$USERNAME" "$DOMAIN" "$PASSWORD"

if [ $? -eq 0 ]; then
    echo "✅ User created successfully!"
    echo ""
    echo "Login credentials:"
    echo "  Username: $USERNAME@$DOMAIN"
    echo "  Password: $PASSWORD"
    echo ""
    echo "The user can now create meetings at: https://telehealth.apps-o.hinisoft.com"
else
    echo "❌ Failed to create user"
    exit 1
fi
