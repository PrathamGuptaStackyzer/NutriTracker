# admin/admin_auth.py

# Static admin credentials (change these in production!)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "nutri1234"  # Very simple for now

def authenticate(username: str, password: str) -> bool:
    """
    Check if username and password match the static admin credentials.
    Returns True if correct, False otherwise.
    """
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD