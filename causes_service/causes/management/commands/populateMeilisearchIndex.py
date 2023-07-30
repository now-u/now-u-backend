from django.core.management.base import BaseCommand
import meilisearch
from causes.search import SEARCH_INDICIES

class Command(BaseCommand):
    help = 'Populate Meilisearch indicies'

    def handle(self, *args, **options):
        # TODO Static client
        client = meilisearch.Client('http://127.0.0.1:7700', 'masterKey')
        for index in SEARCH_INDICIES:
            index.populate_search_index(client)
