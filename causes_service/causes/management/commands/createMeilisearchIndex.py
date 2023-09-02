from django.core.management.base import BaseCommand
from causes.search import SEARCH_INDICIES
from utils.meilisearch import create_meilisearch_client

class Command(BaseCommand):
    help = 'Create Meilisearch indicies'

    def handle(self, *args, **options):
        client = create_meilisearch_client()

        for index in SEARCH_INDICIES:
            try:
                index.delete_search_index(client)
            except Exception:
                print(f"Failed to delete index {index.index_name}")

        for index in SEARCH_INDICIES:
            index.create_search_index(client)
