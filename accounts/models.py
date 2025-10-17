# Stateless user data - no database required
USERS = [
    {"name": "noe", "display_name": "Noé"},
    {"name": "baz", "display_name": "Baz"},
    {"name": "philo", "display_name": "Philo"},
    {"name": "maya", "display_name": "Maya"},
    {"name": "jules", "display_name": "Jules"},
    {"name": "clotilde", "display_name": "Clotilde"},
    {"name": "pierre", "display_name": "Pierre"},
    {"name": "lorene", "display_name": "Lorene"},
]

VALID_USER_NAMES = {user["name"] for user in USERS}


def get_user(name):
    """Get user dict by name, or None if not found"""
    for user in USERS:
        if user["name"] == name:
            return user
    return None
