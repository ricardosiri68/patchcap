from sqlalchemy import  Table, ForeignKey, Column, Integer, Text, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base, declared_attr
import datetime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.interfaces import MapperExtension
from sqlalchemy_utils.types.password import PasswordType
from uuid import uuid4

class BaseExtension(MapperExtension):
    """
    Base entension class for all entities
    """

    def before_insert(self, mapper, connection, instance):
        instance.created_on = datetime.now()

    def before_update(self, mapper, connection, instance):
        instance.updated_on = datetime.now()


class ModelBase(object):
    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime, default=datetime.datetime.now)
    updated_on = Column(DateTime, onupdate=datetime.datetime.now)
    
    __mapper_args__ = {'extension': BaseExtension()}

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


Base = declarative_base(cls=ModelBase)

association_table = Table('user_profile', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('profile_id', Integer, ForeignKey('profile.id'))
)


class Profile(Base):
    name = Column(String(100))


class User(Base):
    email = Column(String(100), unique=True)
    name = Column(String(100))
    username = Column(String(50))
    password = Column(PasswordType(schemes=['pbkdf2_sha512', ]), nullable=True)
    profiles = relationship('Profile',
                    secondary=association_table,
                    backref='users')


class Command(Base):
    expire_on = Column(DateTime, nullable=False)
    command_id = Column(String(36), default=lambda : str(uuid4()), unique=True)
    command_type = Column(String(400))
    command_date = Column(String(20))
    identity = Column(String(240))


class Device(Base):
    name = Column(String(100), nullable=False, unique=True)
    ip = Column(String(100), nullable=True, unique=False)
    username = Column(String(55), unique=False, nullable=True)
    password = Column(String(255), nullable=True)
    instream = Column(String(100), nullable=False)
    outstream = Column(String(100), nullable=False, unique=True)
    roi = Column(String(20), nullable=True, unique=False)
    logging = Column(Boolean, nullable=False, default=True)

    def __init__(self, name=None, src=None, sink=None):
        if not name:
            name = src
        else:
            self.name = name
        self.ip = name
        self.username= 'admin'
        self.password='admin'
        self.instream = src
        self.outstream = sink

    @classmethod
    def findBy(class_, id):
        return DBSession.query(class_).filter_by(id=id).first()

    @classmethod
    def enabled(class_,):
        return DBSession.query(class_).filter_by(logging=True).all()

    @classmethod
    def first(cls):
        return DBSession.query(Device).first()

    def __repr__(self):
        return "[%i]: in-> %s. out->%s" % (self.id,self.instream, self.outstream)


