# Authentication Attack Challenge Evidence

## 1. Database Stores One-Way scrypt Hash Only
- id: 1
- username: alice_updated
- password_hash: scrypt:32768:8:1$mlQeGNEo5un45a2D$ac044074f237296e70468dd4e0249daf2694957fc9044742501dd60db770129770dc308790e63dce39d8b9aa588b1e6bdc49894ccf1f6055430544a37d79436a

## 2. Incorrect Password Rejection (401 Unauthorized)
- Request: POST /auth/login with username=normaluser, password=WRONG_PASSWORD
- Response: HTTP/1.1 401 UNAUTHORIZED -> {"error": "Invalid credentials"}

## 3. Hash-as-Password Attack Rejection (401 Unauthorized)
- Request: POST /auth/login with username=alice_updated, password=scrypt:32768:8:1$...
- Response: HTTP/1.1 401 UNAUTHORIZED -> {"error": "Invalid credentials"}
