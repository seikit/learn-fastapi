from starlette.config import Config

config = Config('.env')

APIKEY = config(key='APIKEY', default=None)
TENANT_ID = config(key='TENANT_ID', default=None)
API_URL = config(key='API_URL', default='http://localhost:8080')
SERVICE_URL = f"{API_URL}/maestro/v1"
