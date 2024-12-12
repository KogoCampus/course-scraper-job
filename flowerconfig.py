from config.settings import settings

# Basic configuration
port = 5555
address = '0.0.0.0'
logging = 'INFO'

basic_auth = [f'{settings.FLOWER_BASIC_AUTH_USERNAME}:{settings.FLOWER_BASIC_AUTH_PASSWORD}']