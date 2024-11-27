# generate_jwt_secret.py

import secrets

# Generate a secure random key
jwt_secret_key = secrets.token_hex(32)  # Generates a 64-character hex string

# Print the generated key
print("Your generated JWT secret key is:")
print(jwt_secret_key)