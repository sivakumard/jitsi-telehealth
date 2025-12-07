"""
OpenEMR Jitsi JWT Token Generator (Python)

This script generates JWT tokens for Jitsi Meet authentication
from OpenEMR. Use this to create meeting links for patients.

Requirements:
- Python 3.7+
- PyJWT library (install via pip)

Installation:
pip install PyJWT

Usage:
python generate_jwt_token.py <room_name> <user_name> <user_email> [--moderator]

Example:
python generate_jwt_token.py "patient-consultation-123" "Dr. Smith" "dr.smith@clinic.com" --moderator
"""

import jwt
import time
import sys
from urllib.parse import quote

# Configuration - MUST match Jitsi deployment
JWT_APP_ID = 'openemr_telehealth'
JWT_APP_SECRET = 'CHANGE_ME_TO_SECURE_RANDOM_STRING_MIN_32_CHARS'  # MUST match secret in Kubernetes
JWT_ISSUER = 'openemr'
JWT_AUDIENCE = 'openemr_telehealth'
JITSI_DOMAIN = 'telehealth.apps-o.hinisoft.com'

def generate_jwt_token(room_name, user_name, user_email, is_moderator=False):
    """Generate a JWT token for Jitsi Meet authentication"""
    
    now = int(time.time())
    
    payload = {
        'iss': JWT_ISSUER,
        'aud': JWT_AUDIENCE,
        'sub': JITSI_DOMAIN,
        'room': room_name,
        'context': {
            'user': {
                'name': user_name,
                'email': user_email,
                'moderator': 'true' if is_moderator else 'false'
            }
        },
        'iat': now,
        'exp': now + 3600,  # Token valid for 1 hour
        'nbf': now - 10     # Not before (10 seconds ago to account for clock skew)
    }
    
    token = jwt.encode(payload, JWT_APP_SECRET, algorithm='HS256')
    
    # Handle both PyJWT 1.x (returns bytes) and 2.x (returns string)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    
    return token

def main():
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} <room_name> <user_name> <user_email> [--moderator]")
        print(f"Example: {sys.argv[0]} 'patient-consultation-123' 'Dr. Smith' 'dr.smith@clinic.com' --moderator")
        sys.exit(1)
    
    room_name = sys.argv[1]
    user_name = sys.argv[2]
    user_email = sys.argv[3]
    is_moderator = '--moderator' in sys.argv
    
    try:
        token = generate_jwt_token(room_name, user_name, user_email, is_moderator)
        
        # Generate the meeting URL
        meeting_url = f"https://{JITSI_DOMAIN}/{quote(room_name)}?jwt={token}"
        
        print("JWT Token Generated Successfully!")
        print("=" * 50)
        print()
        print(f"Room: {room_name}")
        print(f"User: {user_name} ({user_email})")
        print(f"Moderator: {'Yes' if is_moderator else 'No'}")
        print(f"Valid for: 1 hour")
        print()
        print("Meeting URL:")
        print(meeting_url)
        print()
        print("JWT Token (for API use):")
        print(token)
        
    except Exception as e:
        print(f"Error generating JWT token: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
