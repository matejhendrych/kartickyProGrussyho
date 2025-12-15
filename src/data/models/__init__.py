"""
Base model imports for the data layer
Compatible with both old Flask and new FastAPI structure
"""
from .user import User
from .user_password_token import UserPasswordToken
from .carddata import Card
from .group import Group
from .vazby import User_has_group
from .timecard import Timecard
from .grouphastimecard import Group_has_timecard
from .logdata import Log

# For backward compatibility
try:
    from ..base import Base
except ImportError:
    # For FastAPI
    from src.database import Base

__all__ = [
    'Base',
    'User',
    'UserPasswordToken',
    'Card',
    'Group',
    'User_has_group',
    'Timecard',
    'Group_has_timecard',
    'Log'
]