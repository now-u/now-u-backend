from app_links_client.api.default_api import DefaultApi as AppLinksClient
from app_links_client.api_client import ApiClient as AppLinksApiClient
from app_links_client.configuration import Configuration as AppLinksClientConfig

from now_u_api.settings import APP_LINKS_SERVICE

def create_app_links_client() -> AppLinksClient:
    config = AppLinksClientConfig(
        host=APP_LINKS_SERVICE.URL,
        api_key={"ApiKeyAuth": APP_LINKS_SERVICE.API_KEY},
    )
    return AppLinksClient(AppLinksApiClient(configuration=config))
