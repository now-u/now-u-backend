from now_u_api.settings import SUPABASE
from supabase import create_client, Client


def get_supabase_client() -> Client:
    return create_client(SUPABASE.URL, SUPABASE.KEY)
