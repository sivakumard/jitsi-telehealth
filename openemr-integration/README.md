# OpenEMR Jitsi Integration

This directory contains integration code for OpenEMR to generate JWT tokens for Jitsi Meet authentication.

## Overview

Instead of creating individual user accounts in Jitsi, OpenEMR generates JWT (JSON Web Token) tokens that authenticate users and create meeting rooms on-the-fly.

## How It Works

1. **OpenEMR** generates a JWT token with patient/doctor information
2. **Token** is embedded in the meeting URL
3. **Jitsi** validates the token and grants access to the meeting
4. **No user accounts** needed - authentication is handled via the token

## Configuration

### 1. Update JWT Secret

The JWT secret in both OpenEMR and Jitsi **MUST match**.

**In Jitsi (Kubernetes):**
Edit `manifests/dev/02-secrets.yaml`:
```yaml
JWT_APP_SECRET: "your-secure-random-string-here"
```

**In OpenEMR integration scripts:**
Update the `JWT_APP_SECRET` constant in:
- `generate-jwt-token.php`
- `generate_jwt_token.py`

### 2. Generate a Secure Secret

```bash
# Generate a secure random string
openssl rand -hex 32
```

Use this value for `JWT_APP_SECRET` in both Jitsi and OpenEMR.

## Usage

### PHP Example (for OpenEMR)

```php
require_once 'generate-jwt-token.php';

// Generate token for a doctor (moderator)
$token = generate_jwt_token(
    'patient-consultation-123',  // room name
    'Dr. Smith',                  // user name
    'dr.smith@clinic.com',        // user email
    true                          // is moderator
);

// Generate meeting URL
$meetingUrl = "https://telehealth.apps-o.hinisoft.com/patient-consultation-123?jwt={$token}";

// Send URL to patient via email/SMS
```

### Python Example

```python
from generate_jwt_token import generate_jwt_token

# Generate token for a patient (not moderator)
token = generate_jwt_token(
    'patient-consultation-123',  # room name
    'John Doe',                   # user name
    'john.doe@email.com',         # user email
    is_moderator=False
)

# Generate meeting URL
meeting_url = f"https://telehealth.apps-o.hinisoft.com/patient-consultation-123?jwt={token}"

# Send URL to patient
```

### Command Line

**PHP:**
```bash
php generate-jwt-token.php "room-name" "User Name" "user@email.com" true
```

**Python:**
```bash
python generate_jwt_token.py "room-name" "User Name" "user@email.com" --moderator
```

## Token Payload

The JWT token contains:

```json
{
  "iss": "openemr",
  "aud": "openemr_telehealth",
  "sub": "telehealth.apps-o.hinisoft.com",
  "room": "patient-consultation-123",
  "context": {
    "user": {
      "name": "Dr. Smith",
      "email": "dr.smith@clinic.com",
      "moderator": "true"
    }
  },
  "iat": 1234567890,
  "exp": 1234571490,
  "nbf": 1234567880
}
```

## Token Expiration

- Tokens are valid for **1 hour** by default
- Adjust the `exp` field in the payload to change expiration
- Users already in a meeting can stay after token expires
- New users cannot join after token expires

## Moderator vs Participant

- **Moderator** (`moderator: true`): Can manage the meeting, kick users, mute others
- **Participant** (`moderator: false`): Regular participant with limited controls

Typically:
- **Doctors/Providers**: Moderators
- **Patients**: Participants

## OpenEMR Integration Example

```php
<?php
// In OpenEMR appointment module

function createTelehealthMeeting($appointmentId, $providerId, $patientId) {
    // Get provider and patient info
    $provider = getProvider($providerId);
    $patient = getPatient($patientId);
    
    // Generate unique room name
    $roomName = "appointment-{$appointmentId}";
    
    // Generate token for provider (moderator)
    $providerToken = generate_jwt_token(
        $roomName,
        $provider['name'],
        $provider['email'],
        true  // moderator
    );
    
    // Generate token for patient (participant)
    $patientToken = generate_jwt_token(
        $roomName,
        $patient['name'],
        $patient['email'],
        false  // not moderator
    );
    
    // Create meeting URLs
    $providerUrl = "https://telehealth.apps-o.hinisoft.com/{$roomName}?jwt={$providerToken}";
    $patientUrl = "https://telehealth.apps-o.hinisoft.com/{$roomName}?jwt={$patientToken}";
    
    // Send URLs via email/SMS
    sendEmail($provider['email'], "Your Telehealth Meeting", $providerUrl);
    sendEmail($patient['email'], "Your Telehealth Appointment", $patientUrl);
    
    return [
        'provider_url' => $providerUrl,
        'patient_url' => $patientUrl
    ];
}
```

## Security Considerations

1. **Keep JWT_APP_SECRET secure** - Never commit to version control
2. **Use HTTPS only** - Tokens should never be sent over HTTP
3. **Short token expiration** - Default 1 hour is recommended
4. **Unique room names** - Use appointment IDs or UUIDs
5. **Validate on server side** - Jitsi validates tokens automatically

## Troubleshooting

### "Authentication failed" error

- Check that `JWT_APP_SECRET` matches in both Jitsi and OpenEMR
- Verify token hasn't expired
- Check that `iss`, `aud`, and `sub` fields match configuration

### Token not working

- Ensure Jitsi deployment has `AUTH_TYPE: "jwt"` in ConfigMap
- Verify JWT secret is correctly set in Kubernetes secret
- Check that pods have restarted after configuration changes

### Users can't join

- Verify token is included in URL: `?jwt=<token>`
- Check token expiration time
- Ensure DNS and ingress are configured correctly

## Dependencies

### PHP
```bash
composer require firebase/php-jwt
```

### Python
```bash
pip install PyJWT
```

## References

- [Jitsi JWT Documentation](https://github.com/jitsi/lib-jitsi-meet/blob/master/doc/tokens.md)
- [JWT.io](https://jwt.io/) - JWT debugger
- [OpenEMR Documentation](https://www.open-emr.org/wiki/index.php/OpenEMR_Documentation)
