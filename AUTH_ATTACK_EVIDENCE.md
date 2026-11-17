# Authentication Attack Challenge Evidence

## 1. Database Stores One-Way scrypt Hash Only
- id: 1
- username: alice_updated
- password_hash: scrypt:32768:8:1$mlQeGNEo5un45a2D$ac044074f237296e70468dd4e0249daf2694957fc9044742501dd60db770129770dc308790e63dce39d8b9aa588b1e6bdc49894ccf1f6055430544a37d79436a
- **What this proves:** Plaintext passwords are never saved to SQLite; every account uses a salted, one-way scrypt hash.
- **What this does not prove:** It does not prevent offline dictionary/brute-force cracking if a user picks a weak password or reuses a password from another breached site.

## 2. Incorrect Password Rejection (401 Unauthorized)
- Request: POST /auth/login with username=normaluser, password=WRONG_PASSWORD
- Response: HTTP/1.1 401 UNAUTHORIZED -> {"error": "Invalid credentials"}
- **What this proves:** check_password_hash() actively verifies incoming passwords against the stored hash and returns a generic 401 without revealing whether the username exists.
- **What this does not prove:** It does not protect against automated credential-stuffing or high-volume brute-force attacks without rate limiting or account lockout.

## 3. Hash-as-Password Attack Rejection (401 Unauthorized)
- Request: POST /auth/login with username=alice_updated, password=scrypt:32768:8:1$...
- Response: HTTP/1.1 401 UNAUTHORIZED -> {"error": "Invalid credentials"}
- **What this proves:** Leaking or reading the stored password_hash string does not let an attacker log in directly, because login re-hashes the submitted value with the salt instead of comparing raw strings.
- **What this does not prove:** It does not protect active sessions if an attacker steals the server JWT_SECRET_KEY or intercepts a valid Bearer JWT.
