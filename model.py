import config
import bcrypt
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey
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

    posts = relationship("Post", uselist=True)

    def set_password(self, password):
        self.salt = bcrypt.gensalt()
        password = password.encode("utf-8")
        self.password = bcrypt.hashpw(password, self.salt)

    def authenticate(self, password):
        password = password.encode("utf-8")
        return bcrypt.hashpw(password, self.salt.encode("utf-8")) == self.password


# Each plan can have many timelines 
class Plan(Base):
    __tablename__ = "plan"

    id = Column(Integer, autoincrement=True)
    name = Column(String(80))
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    def __init__(self, name, start_date, end_date,id):
        self.id = id
        self.name = name
        self.start_date = start_date
        self.end_date = end_date


# Each Category has many activities 
class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, autoincrement=True)
    name = Column(String(80))
    symbol_url = Column(String(100)) 

    def __init__(self, name, symbol_url,id):
        self.id = id
        self.name = name
        self.symbol_url = symbol_url


# Timeline belongs to plan 
class Timeline(Base):
    __tablename__ = "timeline"

    id = Column(Integer, autoincrement=True)
    date = Column(DateTime)
    timeslot1 = Column(String(80))
    timeslot2 = Column(String(80))
    timeslot3 = Column(String(80))
    timeslot4 = Column(String(80))
    timeslot5 = Column(String(80))

    def __init__(self, id, date, timeslot1, timeslot2, timeslot3, timeslot4, timeslot5):
        self.id = id
        self.date = date
        self.timeslot1 = timeslot1
        self.timeslot2 = timeslot2
        self.timeslot3 = timeslot3
        self.timeslot4 = timeslot4
        self.timeslot5 = timeslot5


# Activity belong to category 
class Activity(Base):
    __tablename__ = "activity"

    id = Column(Integer, autoincrement=True)
    title = Column(String(80))
    photo_url = Column(String(100))
    description = Column(String(200000))
    category = Column(String(80))  # NOT SURE

    def __init__(self, id, title, photo_url, description):
        self.id = id
        self.title = title
        self.photo_url = photo_url
        self.description = description
        self.category = category # NOT SURE


class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(64), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    posted_at = Column(DateTime, nullable=True, default=None)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User")


def create_tables():
    Base.metadata.create_all(engine)
    """
    u = User(email="test@test.com")
    u.set_password("unicorn")
    session.add(u)
    p = Post(title="This is a test post", body="This is the body of a test post.")
    u.posts.append(p)
    session.commit()
    """

if __name__ == "__main__":
    create_tables()



