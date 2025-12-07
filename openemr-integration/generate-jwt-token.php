#!/usr/bin/env php
<?php
/**
 * OpenEMR Jitsi JWT Token Generator
 * 
 * This script generates JWT tokens for Jitsi Meet authentication
 * from OpenEMR. Use this to create meeting links for patients.
 * 
 * Requirements:
 * - PHP 7.4+
 * - firebase/php-jwt library (install via composer)
 * 
 * Installation:
 * composer require firebase/php-jwt
 * 
 * Usage:
 * php generate-jwt-token.php <room_name> <user_name> <user_email> [moderator]
 * 
 * Example:
 * php generate-jwt-token.php "patient-consultation-123" "Dr. Smith" "dr.smith@clinic.com" true
 */

require_once __DIR__ . '/vendor/autoload.php';

use Firebase\JWT\JWT;

// Configuration - MUST match Jitsi deployment
const JWT_APP_ID = 'openemr_telehealth';
const JWT_APP_SECRET = 'CHANGE_ME_TO_SECURE_RANDOM_STRING_MIN_32_CHARS'; // MUST match secret in Kubernetes
const JWT_ISSUER = 'openemr';
const JWT_AUDIENCE = 'openemr_telehealth';
const JITSI_DOMAIN = 'telehealth.apps-o.hinisoft.com';

// Parse command line arguments
if ($argc < 4) {
    echo "Usage: {$argv[0]} <room_name> <user_name> <user_email> [moderator]\n";
    echo "Example: {$argv[0]} 'patient-consultation-123' 'Dr. Smith' 'dr.smith@clinic.com' true\n";
    exit(1);
}

$roomName = $argv[1];
$userName = $argv[2];
$userEmail = $argv[3];
$isModerator = isset($argv[4]) && $argv[4] === 'true';

// Generate JWT token
$payload = [
    'iss' => JWT_ISSUER,
    'aud' => JWT_AUDIENCE,
    'sub' => JITSI_DOMAIN,
    'room' => $roomName,
    'context' => [
        'user' => [
            'name' => $userName,
            'email' => $userEmail,
            'moderator' => $isModerator ? 'true' : 'false'
        ]
    ],
    'iat' => time(),
    'exp' => time() + 3600, // Token valid for 1 hour
    'nbf' => time() - 10    // Not before (10 seconds ago to account for clock skew)
];

try {
    $jwt = JWT::encode($payload, JWT_APP_SECRET, 'HS256');
    
    // Generate the meeting URL
    $meetingUrl = "https://" . JITSI_DOMAIN . "/" . urlencode($roomName) . "?jwt=" . $jwt;
    
    echo "JWT Token Generated Successfully!\n";
    echo "================================\n\n";
    echo "Room: {$roomName}\n";
    echo "User: {$userName} ({$userEmail})\n";
    echo "Moderator: " . ($isModerator ? 'Yes' : 'No') . "\n";
    echo "Valid for: 1 hour\n\n";
    echo "Meeting URL:\n";
    echo "{$meetingUrl}\n\n";
    echo "JWT Token (for API use):\n";
    echo "{$jwt}\n";
    
} catch (Exception $e) {
    echo "Error generating JWT token: " . $e->getMessage() . "\n";
    exit(1);
}
