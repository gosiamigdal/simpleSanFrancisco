import config
import bcrypt
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey, UniqueConstraint
from sqlalchemy import Column, Integer, String, DateTime, Text

from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref

from flask.ext.login import UserMixin

engine = create_engine(config.DB_URI, echo=False) 
session = scoped_session(sessionmaker(bind=engine,
                         autocommit = False,
                         autoflush = False))

Base = declarative_base()
Base.query = session.query_property()




class User(Base, UserMixin):
    __tablename__ = "users" 

    id = Column(Integer, primary_key=True)
    email = Column(String(64), nullable=False)
    password = Column(String(64), nullable=False)
    salt = Column(String(64), nullable=False)

    plans = relationship("Plan", uselist=True)

    def set_password(self, password):
        self.salt = bcrypt.gensalt()
        password = password.encode("utf-8")
        self.password = bcrypt.hashpw(password, self.salt)

    def authenticate(self, password):
        password = password.encode("utf-8")
        return bcrypt.hashpw(password, self.salt.encode("utf-8")) == self.password


# Each plan can have many timelines 
class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User")
    timelines = relationship("Timeline", uselist=True)


# Timeline belongs to plan 
class Timeline(Base):
    __tablename__ = "timelines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime)
    plan_id = Column(Integer, ForeignKey("plans.id"))

    plan = relationship("Plan")
    timeline_activities = relationship("TimelineActivity", uselist=True)


class TimelineActivity(Base):
    __tablename__ = "timeline_activities"

    activity_id = Column(Integer, ForeignKey("activities.id"))
    timeline_id = Column(Integer, ForeignKey("timelines.id"), primary_key=True)
    order = Column(Integer, primary_key=True)

    timeline = relationship("Timeline")
    activity = relationship("Activity")



# Activity belong to category 
class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(80))
    photo_url = Column(String(120))
    description = Column(String(1000))
    
    timeline_activities = relationship("TimelineActivity", uselist=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category")




# Each Category has many activities 
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer,primary_key=True, autoincrement=True)
    name = Column(String(80))
    symbol_url = Column(String(120))

    activities = relationship("Activity", uselist=True) 



def create_tables():
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    create_tables()



