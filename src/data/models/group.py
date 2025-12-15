"""Group model with type hints"""
from typing import List, Optional, Tuple
from sqlalchemy import Time, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, Boolean
from datetime import time

from ..mixins import CRUDModel
from .grouphastimecard import Group_has_timecard
from ..database import db


class Group(CRUDModel):
    """Model for user groups with access control"""
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    Monday = Column("Monday", Integer, default=False)
    Tuesday = Column("Tuesday", Integer, default=False)
    Wednesday = Column("Wednesday", Integer, default=False)
    Thursday = Column("Thursday", Integer, default=False)
    Friday = Column("Friday", Integer, default=False)
    Saturday = Column("Saturday", Integer, default=False)
    Sunday = Column("Sunday", Integer, default=False)
    group_name = Column("group_name", String(40), nullable=False, index=True)
    access_time_from = Column("access_time_from", Time, nullable=True, index=True)
    access_time_to = Column("access_time_to", Time, nullable=True, index=True)
    timecard = relationship(Group_has_timecard, backref='group')
    
    mysql_engine = 'InnoDB'
    mysql_charset = 'utf8-czech'
    mysql_key_block_size = "1024"

    def __init__(self, **kwargs):
        """Initialize group"""
        for k, v in kwargs.items():
            setattr(self, k, v)

    @staticmethod
    def getGroupList() -> List[Tuple[int, str, Optional[time], Optional[time]]]:
        """Get list of all groups with their details"""
        return db.session.query(Group.id, Group.group_name, Group.access_time_from, Group.access_time_to).all()

    @staticmethod
    def find_access_time(id: int) -> List['Group']:
        """Find group access time by ID"""
        return db.session.query(Group).filter_by(id=id).all()

    @staticmethod
    def getGroupName(id: int) -> Optional[str]:
        """Get group name by ID"""
        return db.session.query(Group.group_name).filter_by(id=id).scalar()

    @staticmethod
    def getIdName() -> List[Tuple[int, str]]:
        """Get all group IDs and names"""
        return db.session.query(Group.id, Group.group_name).all()

    @staticmethod
    def getTimeFrom(id: int) -> Optional[time]:
        """Get access time from for group"""
        return db.session.query(Group.access_time_from).filter_by(id=id).scalar()

    @staticmethod
    def getTimeTo(id: int) -> Optional[time]:
        """Get access time to for group"""
        return db.session.query(Group.access_time_to).filter_by(id=id).scalar()



