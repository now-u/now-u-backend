from django.core.management.base import BaseCommand
from causes.search import SEARCH_INDICIES
from utils.meilisearch import create_meilisearch_client
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populate Meilisearch indicies'

    def handle(self, *args, **options):
        now = timezone.now()

        # TODO Static client
        client = create_meilisearch_client()
        for index in SEARCH_INDICIES:
            index.populate_search_index(client, now)
