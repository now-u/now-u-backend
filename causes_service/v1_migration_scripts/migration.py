import requests
import json
import shutil
from datetime import datetime


# TODO Every campaign has a short name
# Map through all short names
# TODO Remove everything from topics except campaigns...
# TODO Add header image to topics which is used as fallback to optional header image for campaign 

def get_duplicate_actions(actions):
    print(set(action['type'] for action in actions))

    titles: dict[str, int] = {}
    # X is a duplicate of Y
    duplicate_titles_ids: dict[int, int] = {}
    for action in actions:
        if action['title'] in titles:
            duplicate_titles_ids[action['id']] = titles[action['title']]
        else:
            titles[action['title']] = action['id']

    print(duplicate_titles_ids)
    return duplicate_titles_ids

def get_duplicate_learning_resources(learning_resources):
    print(set(resource['type'] for resource in learning_resources))

    titles: dict[str, int] = {}
    # X is a duplicate of Y
    duplicate_titles_ids: dict[int, int] = {}
    for resource in learning_resources:
        if resource['title'] in titles:
            duplicate_titles_ids[resource['id']] = titles[resource['title']]
        else:
            titles[resource['title']] = resource['id']

    print(duplicate_titles_ids)
    return duplicate_titles_ids

def organisation_type(organisation_type: str) -> str:
    match organisation_type:
        case "social enterprise" | "social_enterprise":
            return 'SOCIAL_ENTERPRISE'
        case "charity":
            return "CHARITY"
    print(f"Unkonwn charity type: {organisation_type}")
    return 'UNKNOWN' 

def learning_resource_type(learning_resource_type: str) -> str:
    # {'', 'Other', 'learn', 'Behaviour Change', 'other', 'Listen', 'reading', 'Video', 'infographic', 'Reading', 'Learn', 'Leanr', 'Infographic', 'video'}
    match learning_resource_type.lower().strip():
        case '' | 'other' | 'learn' | 'behaviour change' | 'leanr':
            return 'OTHER'
        case 'listen':
            return 'LISTEN'
        case 'reading':
            return 'READING'
        case 'video':
            return 'VIDEO'
        case 'infographic':
            return 'INFOGRAPHIC'
        case _:
            # TODO Come back and make sure we have all action types correctly mapped
            return 'OTHER'
            # raise Exception(f"Unknown learning resource type {learning_resource_type}")

def action_type(action_type: str) -> str:
    match action_type.lower().strip():
        case 'volunteer' | 'support':
            return 'VOLUNTEER'
        case 'donate':
            return 'DONATE'
        case 'fundraise':
            return 'FUNDRAISE'
        case 'awareness' | 'raise awareness':
            return 'RAISE_AWARENESS'
        case 'sign' | 'sign a petition' | 'sign an open letter':
            return 'SIGN'
        case 'behaviour' | 'behaviour change' | 'eco-cycle' | 'consumer pressure':
            return 'BEHAVIOR'
        case 'contact':
            return 'CONTACT'
        case 'protest':
            return 'PROTEST'
        case 'connect':
            return 'CONNECT'
        case 'learn' | 'reading' | 'infographic':
            return 'LEARN'
        case 'purchase':
            return 'PURCHASE'
        case 'quiz':
            return 'QUIZ'
        # TODO Handle these types
        case 'other' | '' | None | 'friends of the earth' | 'join' | 'share':
            return 'OTHER'
        case _:
            # TODO Come back and make sure we have all action types correctly mapped
            return 'OTHER'
            # raise Exception(f"Unknown action type {action_type}")


output_fixtures = []

print("Fetching causes")
causes: dict = requests.get('https://staging.api.now-u.com/api/v2/causes').json()['data']
print("Fetching campaings")
list_campaigns: dict = requests.get('https://staging.api.now-u.com/api/v2/campaigns').json()['data']
campaigns = [
    requests.get(f'https://staging.api.now-u.com/api/v2/campaigns/{campaign["id"]}').json()['data']
    for campaign in list_campaigns
]
print("Fetching actions")
actions: dict = requests.get('https://staging.api.now-u.com/api/v2/actions').json()['data']
print(set(action['type'] for action in actions))
print("Fetching learning resources")
learning_resources: dict = requests.get('https://staging.api.now-u.com/api/v2/learning_resources').json()['data']
print("Fetching articles")
articles: dict = requests.get('https://staging.api.now-u.com/api/v1/articles').json()['data']
print("Fetching organisations")
organisations: dict = requests.get('https://staging.api.now-u.com/api/v1/organisations').json()['data']
print("Fetching faqs")
faqs: dict = requests.get('https://staging.api.now-u.com/api/v1/faqs').json()['data']

# duplicate_action_ids = { 770: 746, 322: 761, 411: 762, 421: 154, 481: 100, 577: 764, 586: 765 }
duplicate_action_ids = get_duplicate_actions(actions)
# duplicate_learning_resource_ids = {1061: 604, 1062: 620, 397: 390, 497: 496, 660: 632, 802: 801, 1035: 544, 976: 150, 144: 973, 145: 974, 146: 961, 148: 975, 830: 927}
duplicate_learning_resource_ids = get_duplicate_learning_resources(learning_resources)
duplicate_campaign_map_ids = { 115: 118 }

number_of_created_images = 0

DOWNLOAD_IMAGES = False

missing_images = []

def create_image(current_image_url: str, image_location: str, resource_id: int) -> int:
    global number_of_created_images
    number_of_created_images += 1

    print(f"File name from url {current_image_url}")
    try:
        file_name = f"{number_of_created_images}"
        if DOWNLOAD_IMAGES:
            response = requests.get(current_image_url, stream = True)
            if response.status_code == 200:
            # file_name_from_url = current_image_url.split('filename%2A%3DUTF-8%27%27')[-1].split('&')[0]
            # print(f"File name from url {file_name_from_url}")
            # file_name = f"{number_of_created_images}-{file_name_from_url}"
                with open(f"./images/{file_name}", 'wb') as f:
                # with open(f"../deploy/causes_service/media/images/{file_name}", 'wb') as f:
                    shutil.copyfileobj(response.raw, f)
                    print('Image sucessfully Downloaded: ', file_name)
            else:
                missing_images.append(f"resource and field: {image_location}, resource id: {resource_id}, image url: {current_image_url}")
                raise Exception("Image donwload failed")
    except Exception:
        file_name = "error.png"
        print('Image Couldn\'t be retrieved')

    # TODO For now if we cannot donwload an image we just use some other image

    output_fixtures.append({
        'model': 'images.image',
        'pk': number_of_created_images,
        'fields': {
            'image': f"images/{file_name}",
        }
    })
    return number_of_created_images

output_fixtures.extend([
    {
        'model': 'causes.cause',
        'pk': cause['id'],
        'fields': {
            'title': cause['name'],
            'icon': cause['icon'],
            'description': cause['description'],
            'header_image': create_image(cause['image'], "cause_header", cause['id']),
            'actions': [],
            'learning_resources': [],
            'campaigns': [],
        }
    }
    for cause in causes
])

def get_cause_from_output(cause_id: int) -> dict:
    return next(fixture for fixture in output_fixtures if fixture['model'] == 'causes.cause' and fixture['pk'] == cause_id)

for action in actions:
    for cause in action['causes']:
        cause_model = get_cause_from_output(cause['id'])
        cause_model['fields']['actions'].append(
            action['id'] if action['id'] not in duplicate_action_ids else duplicate_action_ids[action['id']]
        )

for learning_resource in learning_resources:
    for cause in learning_resource['causes']:
        cause_model = get_cause_from_output(cause['id'])
        cause_model['fields']['learning_resources'].append(
            learning_resource['id'] if learning_resource['id'] not in duplicate_learning_resource_ids else duplicate_learning_resource_ids[learning_resource['id']]
        )

for campaign in campaigns:
    for cause in campaign['causes']:
        cause_model = get_cause_from_output(cause['id'])
        cause_model['fields']['campaigns'].append(
            campaign['id'] if campaign['id'] not in duplicate_campaign_map_ids else duplicate_campaign_map_ids[campaign['id']]
        )

output_fixtures.extend([
    {
        'model': 'causes.action',
        'pk': action['id'],
        'fields': {
            'title': action['title'],
            'action_type': action_type(action['type']),
            'what_description': action['what_description'],
            'why_description': action['why_description'],
            'link': action['link'],
            'time': action['time'],
            'of_the_month': action['of_the_month'],
            'suggested': action['recommended'],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }
    }
    for action in actions
    # The following are duplicate and should be squashed (including user completions)
    if action['id'] not in duplicate_action_ids.keys()
])

output_fixtures.extend([
    {
        'model': 'causes.learningresource',
        'pk': resource['id'],
        'fields': {
            'title': resource['title'],
            'time': resource['time'],
            'link': resource['link'],
            'learning_resource_type': learning_resource_type(resource['type']),
            'source': resource['source'],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }
    }
    for resource in learning_resources
    if resource['id'] not in duplicate_learning_resource_ids.keys()
])
    
output_fixtures.extend([
    {
        'model': 'causes.campaign',
        'pk': resource['id'],
        'fields': {
            'title': resource['title'],
            'short_name': resource['short_name'],
            'description': resource['description_app'],
            'header_image': create_image(resource['header_image'], "campaign_header", resource['id']),
            'of_the_month': resource['of_the_month'],
            'suggested': resource['recommended'],

            'actions': [
                action['id'] if action['id'] not in duplicate_action_ids else duplicate_action_ids[action['id']]
                for action in resource['campaign_actions']
            ],
            'learning_resources': [
                r['id'] if r['id'] not in duplicate_learning_resource_ids else duplicate_learning_resource_ids[r['id']] 
                for r in resource['learning_resources']
            ],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }
    }
    for resource in campaigns
    if resource['id'] not in duplicate_campaign_map_ids.keys()
])
    
output_fixtures.extend([
    {
        'model': 'causes.newsarticle',
        'pk': article['id'],
        'fields': {
            'title': article['title'],
            'subtitle': article['subtitle'],
            'header_image': create_image(article['header_image'], "news_article_header", article['id']),
            'link': article['full_article_link'],
            'source': article['source'] or 'TODO Source',
            'created_at': article['created_at'],
            'updated_at': article['updated_at'],
        }
    }
    for article in articles
])

organisation_extra_link_index = 1
for organisation in organisations:
    output_fixtures.append({
        'model': 'causes.organisation',
        'pk': organisation['id'],
        'fields': {
            'name': organisation['name'],
            'description': organisation['description'],
            'logo': create_image(organisation['logo_link'], "organisation_logo", organisation['id']),
            'website_link': organisation['website'],
            'email_address': organisation['email'],
            'geographic_reach': organisation['geographic_reach'],
            'instagram_link': organisation['IG_link'],
            'facebook_link': organisation['FB_link'],
            'twitter_link': organisation['twitter_link'],
            # TODO Parse
            'organisation_type': organisation_type(organisation['organisation_type']),
            'created_at': organisation['created_at'],
            'updated_at': organisation['updated_at'],
        }
    })
    for i in range(1, 4):
        if organisation[f'extra_text_{i}']:
            output_fixtures.append({
                'model': 'causes.organisationextralink',
                'pk': organisation_extra_link_index ,
                'fields': {
                    'organisation': organisation['id'],
                    'title': organisation[f'extra_text_{i}'],
                    'link': organisation[f'extra_link_{i}'],
                }
            })
            organisation_extra_link_index += 1

output_fixtures.extend([
    {
        'model': 'faqs.faq',
        'pk': faq['id'],
        'fields': {
            'question': faq['question'],
            'answer': faq['answer'],
        }
    }
    for faq in faqs
])

for (i, name) in enumerate(set(campaign['short_name'] for campaign in campaigns)):
    output_fixtures.append(
        {
            'model': 'causes.theme',
            'pk': i,
            'fields': {
                'title': name,
                'campaigns': [campaign['id'] for campaign in campaigns if campaign['short_name'] == name]
            }
        }
    )

with open('fixtures.json', 'w') as f:
    json.dump(output_fixtures, f, indent=2)

def get_duplicate_campaigns():
    list_campaigns: dict = requests.get('https://staging.api.now-u.com/api/v2/campaigns').json()['data']
    campaigns = [
        requests.get(f'https://staging.api.now-u.com/api/v2/campaigns/{campaign["id"]}').json()['data']
        for campaign in list_campaigns
    ]

    for campaign in campaigns:
        for action in campaign['campaign_actions']:
            if action['id'] in [770, 322, 411, 421, 481, 577, 586]:
                print(f'Duplicate action {action["id"]} in campaign {campaign["id"]}!')
        for learning_resources in campaign['learning_resources']:
            if learning_resources['id'] in [1061, 1062, 397, 497, 660, 802, 1035, 976, 144, 145, 146, 148, 830]:
                print(f'Duplicate learning resource {learning_resources["id"]} in campaign {campaign["id"]}!') 

def get_duplicate_organisations(organisations):
    print(set(organisation['organisation_type'] for organisation in organisations))
    print(list(organisation['id'] for organisation in organisations if organisation['organisation_type'] is None))

print("Short names")
print(set(campaign['short_name'] for campaign in campaigns))

print("Issues report:")

print("Actions with bad type:")
print(list(action['id'] for action in actions if action_type(action['type']) == "OTHER"))

print("Learning Resources with bad type:")
print(list(lr['id'] for lr in learning_resources if learning_resource_type(lr['type']) == "OTHER"))

print("Organisations with bad type:")
print(list(organisation['id'] for organisation in organisations if organisation_type(organisation['organisation_type']) == "UNKNOWN"))

print("Missing Images:")
for image in missing_images:
    print(image)

# actions()
# learning_resources()
# campaigns()
# causes()
# news_article()
# organisations()
