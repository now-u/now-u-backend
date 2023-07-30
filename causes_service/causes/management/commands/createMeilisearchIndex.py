from django.core.management.base import BaseCommand
import meilisearch
from causes.search import SEARCH_INDICIES

class Command(BaseCommand):
    help = 'Create Meilisearch indicies'

    def handle(self, *args, **options):
        # TODO Create static client
        client = meilisearch.Client('http://127.0.0.1:7700', 'masterKey')

        for index in SEARCH_INDICIES:
            try:
                index.delete_search_index(client)
            except Exception:
                print(f"Failed to delete index {index.index_name}")

        for index in SEARCH_INDICIES:
            index.create_search_index(client)
