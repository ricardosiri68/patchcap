from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

#engine = create_engine('sqlite:///:memory:', echo=False)
engine = create_engine('sqlite:///patchcap.db')
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
Base = declarative_base()


class Plate(Base):
    __tablename__ = 'plates'
    id = Column(Integer, primary_key=True)
    code = Column(String(6))
    enabled = Column(Boolean, nullable=False, default=True)
    children = relationship("PlateLog")
    session = Session()

    def __repr__(self):
        return "<Plate('%s - %i')>" % (self.code, int(self.enabled))

class PlateLog(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    plate_id = Column(Integer, ForeignKey('plates.id'))
    plate = relationship("Plate", backref=backref('logs', order_by=id))
     
    def __repr__(self):
        return "<Log('%s')>" %(self.timestamp)
