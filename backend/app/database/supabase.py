"""Supabase client wrapper.

Provides functions to create user-scoped and service-role Supabase clients.
The service-role client bypasses RLS and should only be used for server-side
admin tasks or trusted ingestion. User-scoped operations should pass the user's
Bearer token.
"""

from supabase import Client, create_client

from app.config import settings


def get_service_role_client() -> Client:
    """Create a Supabase client authenticated with the service-role key.

    Bypasses Row Level Security (RLS). Use with caution for server-side data setup
    or admin operations.
    """
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


def get_anon_client() -> Client:
    """Create an unauthenticated Supabase client using the anon key."""
    return create_client(settings.supabase_url, settings.supabase_anon_key)


def get_user_scoped_client(access_token: str) -> Client:
    """Create a Supabase client scoped to an authenticated user's access token.

    Enforces Row Level Security (RLS) as that user.
    """
    client = create_client(settings.supabase_url, settings.supabase_anon_key)
    client.postgrest.auth(access_token)
    return client
