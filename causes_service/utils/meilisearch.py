import meilisearch
from now_u_api.settings import MEILISEARCH

def create_meilisearch_client() -> meilisearch.Client:
    return meilisearch.Client(MEILISEARCH.URL, MEILISEARCH.MASTER_KEY)
