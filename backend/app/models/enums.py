import enum

class VIPLevel(enum.Enum):
    free = "Free"
    pro = "Pro"
    premium = "Premium"
    ultimate = "Ultimate"
    team = "Team"

class UserRole(enum.Enum):
    normal = "normal"
    promoter = "promoter"
    admin = "admin"

class AdminLevel(enum.Enum):
    super_admin = 1
    admin = 2
    moderator = 3
    editor = 4
    viewer = 5
