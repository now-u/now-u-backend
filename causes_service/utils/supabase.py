import logging
from supabase import create_client, Client

from now_u_api.settings import SUPABASE

logger = logging.getLogger(__name__)

def get_supabase_client() -> Client:
    logger.info(f"Creating Supabase client supabase_url={SUPABASE.URL}")
    return create_client(SUPABASE.URL, SUPABASE.KEY)
