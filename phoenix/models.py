import os
import datetime
import uuid
from hashlib import sha1

from sqlalchemy import (Table, Column, Integer, Float, Text, String, Boolean,
                        DateTime, Sequence, Unicode, ForeignKey, func)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.sql import desc

import logging

log = logging.getLogger(__name__)


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class ProcessHistory(Base):
    __tablename__ = 'process_history'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, Sequence('process_history_seq_id', optional=True),
                primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False)
    service_url = Column(String(255), nullable=False)
    status_location = Column(String(255), nullable=True)
    user_id = Column(String(255), nullable=False)
    identifier = Column(String(255), nullable=False)
    run_message = Column(Unicode(255), nullable=True)
    start_time = Column(DateTime, default=datetime.datetime.now())
    end_time = Column(DateTime)
    output_delete_time = Column(DateTime)
    output_size_mb = Column(Float, default=0.0)
    status_id = Column(Integer, ForeignKey('status.id', ondelete='CASCADE'))
    deleted = Column(Boolean, unique=False, default=False)

    def __init__(self, user_id, uuid, identifier, service_url, status_location=None):
        self.user_id = user_id
        self.uuid = uuid
        self.identifier = identifier
        self.service_url = service_url
        self.status_location = status_location

    @classmethod
    def by_uuid(cls, uuid):
        return DBSession.query(ProcessHistory).\
                   filter(ProcessHistory.uuid == uuid).\
                   filter(ProcessHistory.deleted == False).first()
                   
    @classmethod
    def by_userid(cls, userid):
        return DBSession.query(ProcessHistory).\
                   filter(ProcessHistory.user_id == userid).\
                   filter(ProcessHistory.deleted == False).\
                   order_by(desc(ProcessHistory.id)).all()

    @classmethod
    def by_process_identifier(cls, identifier):
        return DBSession.query(ProcessHistory).\
                   filter(ProcessHistory.identifier == identifier).\
                   filter(ProcessHistory.deleted == False).all()

    @classmethod
    def status_count_by_userid(cls, userid):
        return DBSession.query(Status.status, func.count(ProcessHistory.id)).\
                   outerjoin(ProcessHistory).\
                   group_by(Status.status).\
                   order_by(Status.id).all()


class Status(Base):
    __tablename__ = 'status'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, Sequence('status_seq_id', optional=True),
                primary_key=True, autoincrement=True)
    status = Column(Unicode(80), nullable=False, index=True, unique=True)
    processes = relationship(ProcessHistory, backref='status',
                             cascade='all, delete-orphan',
                             passive_deletes=True)

    def __init__(self, status):
        self.status = status

    @classmethod
    def by_id(cls, statusid):
        return DBSession.query(Status).filter(Status.id == statusid).first()
