"""
Authentication and user management
"""

# User database
users = {
    "": {"password": "", "role": "User"},
    "admin@welvision.com": {"password": "admin123", "role": "Admin"},
    "superadmin@welvision.com": {"password": "super123", "role": "Super Admin"}
}


def authenticate_user(email, password, role):
    """
    Authenticate a user based on email, password, and role.
    
    Args:
        email (str): User email
        password (str): User password
        role (str): User role (User, Admin, Super Admin)
        
    Returns:
        bool: True if authentication successful, False otherwise
    """
    if email in users:
        user_data = users[email]
        return (user_data["password"] == password and 
                user_data["role"] == role)
    return False
