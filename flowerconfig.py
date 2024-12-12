import os

# Basic configuration
port = 5555
address = '0.0.0.0'
logging = 'INFO'

# OAuth configuration (only used in production)
if os.getenv('ENV') == 'production':
    auth_provider = os.getenv('FLOWER_AUTH_PROVIDER')
    oauth2_key = os.getenv('FLOWER_OAUTH2_KEY')
    oauth2_secret = os.getenv('FLOWER_OAUTH2_SECRET')
    oauth2_redirect_uri = os.getenv('FLOWER_OAUTH2_REDIRECT_URI')