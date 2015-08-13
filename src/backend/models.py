from sqlalchemy import  Column, Integer, UnicodeText, Unicode, DateTime
from sqlalchemy.ext.declarative import declarative_base, declared_attr
import datetime
from sqlalchemy_utils.types.password import PasswordType
from uuid import uuid4

class ModelBase(object):
    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime, default=datetime.datetime.now)
    updated_on = Column(DateTime, onupdate=datetime.datetime.now)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


Base = declarative_base(cls=ModelBase)



class User(Base):
    email = Column(Unicode(1024), unique=True)
    first_name = Column(Unicode(1024))
    last_name = Column(Unicode(1024))
    password = Column(PasswordType(schemes=['pbkdf2_sha512', ]), nullable=True)

    
class Command(Base):
    expire_on = Column(DateTime, nullable=False)
    command_id = Column(Unicode(36), default=lambda : str(uuid4()), unique=True)
    command_type = Column(Unicode(1024))
    command_date = Column(UnicodeText)
    identity = Column(Unicode(1024))
