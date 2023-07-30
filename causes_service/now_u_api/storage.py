from storages.backends.azure_storage import AzureStorage

from now_u_api.settings import STATIC_FILES_STORAGE_ACCOUNT_KEY, STATIC_FILES_STORAGE_ACCOUNT_NAME, STATIC_FILES_STORAGE_CONTAINER

class PublicAzureStorage(AzureStorage):
    account_name = STATIC_FILES_STORAGE_ACCOUNT_NAME
    account_key = STATIC_FILES_STORAGE_ACCOUNT_KEY
    azure_container = STATIC_FILES_STORAGE_CONTAINER
    expiration_secs = None
