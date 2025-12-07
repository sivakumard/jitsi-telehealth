# Jitsi Telehealth Deployment

Kubernetes deployment for Jitsi Meet configured for telehealth services with authentication and no watermark.

## Features

- ✅ **Authenticated meetings** - Only authorized users can create meetings
- ✅ **Guest access** - Guests can join meetings created by authenticated users
- ✅ **No Jitsi watermark** - Clean, professional interface
- ✅ **Custom domain** - https://telehealth.apps-o.hinisoft.com
- ✅ **TLS/SSL enabled** - Secure HTTPS connections
- ✅ **Persistent storage** - Configuration persists across restarts

## Architecture

The deployment consists of 4 main components:

1. **Prosody** - XMPP server for authentication and signaling
2. **Jicofo** - Jitsi Conference Focus for managing conferences
3. **JVB** - Jitsi Videobridge for handling media streams
4. **Web** - Web interface for users

## Prerequisites

- Kubernetes cluster with Longhorn storage
- NGINX Ingress Controller
- cert-manager for TLS certificates
- DNS record pointing `telehealth.apps-o.hinisoft.com` to your ingress

## Deployment

### 1. Deploy all manifests

```bash
kubectl apply -f manifests/dev/
```

### 2. Wait for all pods to be running

```bash
kubectl get pods -n jitsi -w
```

### 3. Create authenticated users

Use the helper script to create users:

```bash
./create-jitsi-user.sh <username> <password>
```

Example:
```bash
./create-jitsi-user.sh doctor1 SecurePassword123
./create-jitsi-user.sh nurse1 AnotherSecure456
```

### 4. Verify deployment

```bash
kubectl get all -n jitsi
```

## Configuration

### Authentication

Authentication is enabled by default with these settings:
- `ENABLE_AUTH=1` - Requires authentication to create meetings
- `ENABLE_GUESTS=1` - Allows guests to join existing meetings
- `AUTH_TYPE=internal` - Uses Prosody's internal authentication

### Watermark Removal

Watermark is disabled with:
- `DISABLE_WATERMARK=true`
- `INTERFACE_CONFIG_SHOW_JITSI_WATERMARK=false`
- `INTERFACE_CONFIG_SHOW_WATERMARK_FOR_GUESTS=false`
- `INTERFACE_CONFIG_SHOW_BRAND_WATERMARK=false`

### Domain Configuration

- **Public URL**: https://telehealth.apps-o.hinisoft.com
- **XMPP Domain**: meet.jitsi
- **Auth Domain**: auth.meet.jitsi

## User Management

### Create a new user

```bash
kubectl exec -it -n jitsi deployment/prosody -- prosodyctl --config /config/prosody.cfg.lua register <username> meet.jitsi <password>
```

Or use the helper script:
```bash
./create-jitsi-user.sh <username> <password>
```

### List users

```bash
kubectl exec -it -n jitsi deployment/prosody -- prosodyctl --config /config/prosody.cfg.lua list meet.jitsi
```

### Delete a user

```bash
kubectl exec -it -n jitsi deployment/prosody -- prosodyctl --config /config/prosody.cfg.lua deluser <username>@meet.jitsi
```

## Accessing Jitsi

1. Navigate to https://telehealth.apps-o.hinisoft.com
2. Enter a room name
3. Login with your authenticated user credentials
4. Share the room link with guests (they can join without authentication)

## Troubleshooting

### Check pod logs

```bash
# Web interface
kubectl logs -n jitsi deployment/web

# Prosody (XMPP)
kubectl logs -n jitsi deployment/prosody

# Jicofo
kubectl logs -n jitsi deployment/jicofo

# JVB
kubectl logs -n jitsi deployment/jvb
```

### Check services

```bash
kubectl get svc -n jitsi
```

### Check ingress

```bash
kubectl get ingress -n jitsi
kubectl describe ingress jitsi-ingress -n jitsi
```

### Verify TLS certificate

```bash
kubectl get certificate -n jitsi
```

## Scaling

### Scale JVB for more capacity

```bash
kubectl scale deployment jvb -n jitsi --replicas=3
```

## Security Notes

1. **Change default secrets** in `02-secrets.yaml` before deploying to production
2. **Use strong passwords** for authenticated users
3. **Regularly update** Jitsi images to get security patches
4. **Monitor access logs** for suspicious activity

## Storage

Each component has persistent storage:
- Web config: 1Gi
- Prosody config: 1Gi
- Jicofo config: 1Gi
- JVB config: 1Gi

## Network Ports

- **80/443** - HTTP/HTTPS (Web interface)
- **5222** - XMPP client connections
- **5347** - XMPP component connections
- **10000/UDP** - RTP media (exposed via NodePort 30000)

## Support

For issues or questions, refer to:
- [Jitsi Documentation](https://jitsi.github.io/handbook/)
- [Jitsi Community](https://community.jitsi.org/)
