from typing import Optional, List, Tuple, Any
from sqlalchemy.schema import Column
from sqlalchemy.types import Boolean, Integer, String
from sqlalchemy.orm import relationship, backref, Session

from sqlalchemy import cast, Numeric

from ..mixins import CRUDModel
from ..util import generate_random_token
from .vazby import User_has_group
from .carddata import Card
from .group import Group
from .grouphastimecard import Group_has_timecard
from .timecard import Timecard
from datetime import datetime
import calendar

class User(CRUDModel):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    activate_token = Column(String(128), nullable=True, doc="Activation token for email verification")
    email = Column(String(64), nullable=True, unique=True, index=True, doc="The user's email address.")
    password_hash = Column(String(128))
    username = Column(String(64), nullable=True, unique=True, index=True, doc="The user's username.")
    verified = Column(Boolean(name="verified"), nullable=False, default=False)
    card_number = Column(String(32), unique=False, index=True, doc="Card access number")
    name = Column(String(60), unique=False, index=True, doc="Name")
    second_name = Column(String(60), unique=False, index=True, doc="Second name")
    access = Column(String(1), index=True, doc="Access")
    chip_number = Column(String(10), unique=False, index= True, doc= "Chip number", nullable=False)
    mazej = Column(Boolean(name="mazej"),unique=False,doc="pro mazani")
    mysql_engine = 'InnoDB'
    mysql_charset = 'utf8-czech'
    mysql_key_block_size = "1024"



    # Use custom constructor
    # pylint: disable=W0231
    def __init__(self, **kwargs):
        self.activate_token = generate_random_token()
        self.access='U'
        for k, v in kwargs.items():
            setattr(self, k, v)

    @staticmethod
    def find_by_email(email: str) -> Optional['User']:
        """Find user by email address"""
        return db.session.query(User).filter_by(email=email).scalar()

    @staticmethod
    def find_by_username(username: str) -> Optional['User']:
        """Find user by username"""
        return db.session.query(User).filter_by(username=username).scalar()

    # pylint: disable=R0201
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password: str) -> None:
        """Set password hash from plain text password"""
        self.password_hash = bcrypt.generate_password_hash(password, app_config.BCRYPT_LOG_ROUNDS)

    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash"""
        return bcrypt.check_password_hash(self.password_hash, password)

    def is_verified(self) -> bool:
        """Returns whether a user has verified their email"""
        return self.verified is True

    @staticmethod
    def find_by_number(card_number: str) -> Optional['User']:
        """Find user by card number"""
        return db.session.query(User).filter_by(card_number=card_number).scalar()

    @staticmethod
    def getID(card_number: str) -> Optional[int]:
        """Get user ID by card number"""
        return db.session.query(User.id).filter_by(card_number=card_number).scalar()

    @staticmethod
    def getIDAndAccess(card_number: str) -> Optional[Tuple[int, str]]:
        """Get user ID and access level by card number"""
        return db.session.query(User.id, User.access).filter_by(card_number=card_number).first()


    @staticmethod
    def access_by_group(chip: int, fromcte: str) -> bool:
        """
        Check if user has access based on group permissions
        
        Args:
            chip: User's chip number
            fromcte: MQTT topic from card reader
            
        Returns:
            True if access granted, False otherwise
        """
        acctualtime = datetime.now()
        dayofweek = acctualtime.weekday()
        timenow = acctualtime.time()

        chip_str = str(chip).zfill(10)
        user_groups = db.session.query(Group)\
            .filter(getattr(Group, calendar.day_name[dayofweek]) == True).filter(Group.access_time_from <= timenow)\
            .filter(Group.access_time_to >= timenow)\
            .join(User_has_group).join(User).filter(User.chip_number.like(chip_str)).join(Group_has_timecard)\
            .join(Timecard).filter(Timecard.identreader == fromcte).all()
        if len(user_groups) > 0:
            return True
        return False

    @staticmethod
    def find_by_chip(chip_number: int) -> Optional['User']:
        """
        Find user by chip number
        
        Args:
            chip_number: Chip number to search for
            
        Returns:
            User if found, None otherwise
        """
        testchip = str(chip_number).zfill(10)
        return db.session.query(User).filter(User.chip_number.like(testchip)).first()

    @staticmethod
    def all_users() -> List[Tuple[int, str, str]]:
        """Get all users with ID, name, and second name"""
        return db.session.query(User.id, User.name, User.second_name).all()

    @staticmethod
    def all_names() -> List[Tuple[str]]:
        """Get all user names"""
        return db.session.query(User.name).all()

    @staticmethod
    def ingroup():
        """Get users in groups query"""
        return db.session.query(User.id, User.name, User.second_name)

    @staticmethod
    def findUserById(id: int) -> List['User']:
        """Find users by ID"""
        return db.session.query(User).filter_by(id=id).all()

    @staticmethod
    def user_in_group() -> List[Tuple[int, str, str, int, str]]:
        """Get users with their group information"""
        return db.session.query(User.id, User.name, User.second_name, User_has_group.group_id, Group.group_name).join(User_has_group).join(Group).all()

    @staticmethod
    def oneUserById(id: int) -> Optional[Tuple[str, str]]:
        """Get one user's name by ID"""
        return db.session.query(User.name, User.second_name).filter_by(id=id).first()

    @staticmethod
    def getName(id: int) -> Optional[Tuple[str]]:
        """Get user name by ID"""
        return db.session.query(User.name).filter_by(id=id).first()

    @staticmethod
    def usersInSpecificGroup(id: int) -> List[Tuple[int, str, str, int]]:
        """
        Get users in a specific group
        
        Args:
            id: Group ID
            
        Returns:
            List of user tuples with ID, name, second_name, and group_id
        """
        return db.session.query(User.id, User.name, User.second_name, User_has_group.group_id).join(User_has_group).filter_by(group_id=id).all()
