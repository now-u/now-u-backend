from django.core.management.base import BaseCommand
from django.core import files
import requests
import tempfile
from causes.models import Campaign
from images.models import Image

class Command(BaseCommand):
    help = 'Fix images'

    def add_arguments(self, parser):
        parser.add_argument("--max", type=int)

    def handle(self, *args, **options):
        count = 0
        max_count = options['max']

        campaigns_with_broken_images = [campaign for campaign in Campaign.objects.all() if campaign.header_image.id == 441]
        print([c.id for c in campaigns_with_broken_images])

        for campaign in campaigns_with_broken_images:
            if max_count and count >= max_count:
                print("Reached max")
                return

            # Fetch the campaign from the staging api
            staging_campaign = requests.get(f'https://staging.api.now-u.com/api/v2/campaigns/{campaign.id}').json()['data']

            # Create an image from it
            image_url = staging_campaign['header_image']
            response = requests.get(image_url, stream=True)

            if response.status_code != 200:
                print(f'Skipping campaign {campaign.id} because failed to download image')
                return

            tf = tempfile.NamedTemporaryFile()
            for block in response.iter_content(1024 * 8):
                if not block:
                    break
                tf.write(block)

            print(f'Updating image of campaign {campaign.id}')
            image = Image.objects.create(
                image = files.File(tf),
                alt_text = f"{campaign.title} header image",
                internal_name = f"Campaign header image - {campaign.title}",
            )
            image_extension = image_url.split('.')[-1].split('&')[0]
            print(f'Image extension is {image_extension}')
            image.image.save(
                f"{campaign.id}-{campaign.title.replace(' ', '_')}-header_image.{image_extension}",
                files.File(tf),
                save = True,
            )

            # Update the campaign with the new image
            campaign.header_image = image
            campaign.save()
            
            print(f'{campaign.id} compelte')
            count += 1
