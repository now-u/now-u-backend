import hashlib
import mailchimp_marketing as MailchimpMarketing

from now_u_api.settings import MAILCHIMP

def get_subscriber_hash(member_email: str):
    return hashlib.md5(member_email.lower().encode()).hexdigest()

def get_client() -> MailchimpMarketing.Client:
  client = MailchimpMarketing.Client()
  client.set_config({
    "api_key": MAILCHIMP['API_KEY'],
    "server": MAILCHIMP['SERVER'],
  })
  return client

def subscribe_to_mailing_list(email_address: str, name: str):
    client = get_client()
    client.lists.add_list_member(
        list_id=MAILCHIMP['LIST_ID'],
        body={
            "email_address": email_address,
            "name": name,
        }
    )

def unsubscribe_from_mailing_list(email_address: str):
    client = get_client()
    client.lists.delete_list_member(
        list_id=MAILCHIMP['LIST_ID'],
        subscriber_hash=get_subscriber_hash(email_address)
    )
