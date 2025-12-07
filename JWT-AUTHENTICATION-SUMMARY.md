# Jitsi Telehealth - JWT Authentication Summary

## ✅ Configuration Complete

Jitsi has been configured for **JWT (JSON Web Token) authentication** for seamless OpenEMR integration.

## 🔑 How It Works

1. **OpenEMR** generates a JWT token containing:
   - Room name (e.g., appointment ID)
   - User information (name, email)
   - Moderator status (doctor vs patient)
   - Expiration time (1 hour)

2. **Meeting URL** is created with embedded token:
   ```
   https://telehealth.apps-o.hinisoft.com/appointment-123?jwt=<token>
   ```

3. **User clicks link** and joins automatically - no login required!

## 📝 Key Changes Made

### Jitsi Configuration
- ✅ Changed `AUTH_TYPE` from `internal` to `jwt`
- ✅ Set `ENABLE_GUESTS=0` (all users authenticate via JWT)
- ✅ Configured JWT parameters:
  - `JWT_APP_ID`: openemr_telehealth
  - `JWT_ACCEPTED_ISSUERS`: openemr
  - `JWT_ACCEPTED_AUDIENCES`: openemr_telehealth

### OpenEMR Integration Scripts
- ✅ PHP script: `openemr-integration/generate-jwt-token.php`
- ✅ Python script: `openemr-integration/generate_jwt_token.py`
- ✅ Comprehensive documentation
- ✅ Dependencies configured (composer.json, requirements.txt)

## 🚀 Quick Start for OpenEMR

### PHP Example
```php
<?php
require_once 'generate-jwt-token.php';

// Generate token for doctor (moderator)
$doctorToken = generate_jwt_token(
    'appointment-123',           // room name
    'Dr. Smith',                 // user name
    'dr.smith@clinic.com',       // user email
    true                         // is moderator
);

// Generate token for patient
$patientToken = generate_jwt_token(
    'appointment-123',
    'John Doe',
    'john.doe@email.com',
    false                        // not moderator
);

// Create meeting URLs
$doctorUrl = "https://telehealth.apps-o.hinisoft.com/appointment-123?jwt={$doctorToken}";
$patientUrl = "https://telehealth.apps-o.hinisoft.com/appointment-123?jwt={$patientToken}";

// Send URLs via email/SMS
sendEmail($doctorEmail, "Your Telehealth Meeting", $doctorUrl);
sendEmail($patientEmail, "Your Appointment", $patientUrl);
```

### Python Example
```python
from generate_jwt_token import generate_jwt_token

# Generate tokens
doctor_token = generate_jwt_token(
    'appointment-123',
    'Dr. Smith',
    'dr.smith@clinic.com',
    is_moderator=True
)

patient_token = generate_jwt_token(
    'appointment-123',
    'John Doe',
    'john.doe@email.com',
    is_moderator=False
)

# Create URLs
doctor_url = f"https://telehealth.apps-o.hinisoft.com/appointment-123?jwt={doctor_token}"
patient_url = f"https://telehealth.apps-o.hinisoft.com/appointment-123?jwt={patient_token}"
```

## 🔒 Security Setup

### 1. Generate JWT Secret

```bash
openssl rand -hex 32
```

Example output:
```
1390a420a59995b91cd2a277b1cc9724846c52aa3e9965a82f2298119d8c60ff
```

### 2. Update Jitsi Secret

Edit `manifests/dev/02-secrets.yaml`:
```yaml
JWT_APP_SECRET: "1390a420a59995b91cd2a277b1cc9724846c52aa3e9965a82f2298119d8c60ff"
```

### 3. Update OpenEMR Scripts

Update the same secret in:
- `openemr-integration/generate-jwt-token.php` (line 22)
- `openemr-integration/generate_jwt_token.py` (line 20)

```php
const JWT_APP_SECRET = '1390a420a59995b91cd2a277b1cc9724846c52aa3e9965a82f2298119d8c60ff';
```

```python
JWT_APP_SECRET = '1390a420a59995b91cd2a277b1cc9724846c52aa3e9965a82f2298119d8c60ff'
```

### 4. Deploy Updated Secret

```bash
kubectl delete -f manifests/dev/02-secrets.yaml
kubectl apply -f manifests/dev/02-secrets.yaml
kubectl rollout restart deployment -n jitsi
```

## 📦 Repository

**GitHub**: https://github.com/sivakumard/jitsi-telehealth
**Commit**: e2d264b

## 📚 Documentation

- **Main README**: [README.md](../README.md)
- **Integration Guide**: [openemr-integration/README.md](../openemr-integration/README.md)

## 🎯 Benefits

✅ **No user accounts** - No need to create/manage individual users
✅ **Simple integration** - Just generate tokens in OpenEMR
✅ **Secure** - Tokens expire after 1 hour
✅ **Flexible** - Different permissions for doctors vs patients
✅ **Scalable** - Works for unlimited appointments
✅ **Professional** - No Jitsi watermark

## ⚠️ Important Notes

1. **JWT_APP_SECRET must match** in both Jitsi and OpenEMR
2. **Keep secret secure** - Never commit to version control
3. **Use HTTPS only** - Tokens contain sensitive information
4. **Token expiration** - Default 1 hour (adjustable)
5. **Moderator control** - Doctors should be moderators, patients should not

## 🔗 Next Steps

1. Generate and configure JWT secret
2. Deploy Jitsi to Kubernetes
3. Integrate token generation into OpenEMR
4. Test with a sample appointment
5. Configure email/SMS delivery for meeting links
