from django.core.management.base import BaseCommand
from causes.search import SEARCH_INDICIES
from utils.meilisearch import create_meilisearch_client

class Command(BaseCommand):
    help = 'Populate Meilisearch indicies'

    def handle(self, *args, **options):
        # TODO Static client
        client = create_meilisearch_client()
        for index in SEARCH_INDICIES:
            index.populate_search_index(client)
