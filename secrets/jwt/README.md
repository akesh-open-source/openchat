# Local JWT signing keys (RS256)
#
# Generate a new key pair:
#
#   mkdir -p secrets/jwt
#   openssl genrsa -out secrets/jwt/private.pem 2048
#   openssl rsa -in secrets/jwt/private.pem -pubout -out secrets/jwt/public.pem
#   chmod 600 secrets/jwt/private.pem
#
# Docker Compose mounts:
#   auth:    private.pem + public.pem → /run/secrets/
#   gateway: public.pem only          → /run/secrets/
#
# Never commit private.pem. public.pem may be committed for local/dev
# convenience, but prefer regenerating per environment in production.
