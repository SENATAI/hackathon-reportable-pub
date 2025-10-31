from enum import Enum

class UserRole(str, Enum):
    """
    Enum for user roles.
    """
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class Race(str, Enum):
    """
    Enum for character races.
    """
    HUMAN = "human"
    ELF = "elf"
    ORC = "orc"