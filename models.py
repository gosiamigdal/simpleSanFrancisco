from datetime import timedelta
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship
from flask.ext.login import UserMixin
from flask.ext.sqlalchemy import SQLAlchemy

from app import app

db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    __tablename__ = "users" 

    id = Column(Integer, primary_key=True)
    fb_id = Column(String(64))



# Each plan can have many timelines 
class Plan(db.Model):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hashed_url = Column(String(80))

    user = relationship("User",backref="plans")
    timelines = relationship("Timeline", uselist=True)

    def date_range(self):
        result = []
        current = self.start_date
        while current <= self.end_date:
            result.append(current)
            current = current + timedelta(days=1)
        return result



# Timeline belongs to plan 
class Timeline(db.Model):
    __tablename__ = "timelines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime)
    plan_id = Column(Integer, ForeignKey("plans.id"),nullable=False)

    plan = relationship("Plan")
    timeline_activities = relationship("TimelineActivity", uselist=True)
    


class TimelineActivity(db.Model):
    __tablename__ = "timeline_activities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey("activities.id"),nullable=False)
    timeline_id = Column(Integer, ForeignKey("timelines.id"),nullable=False)
    order = Column(Integer)

    timeline = relationship("Timeline")
    activity = relationship("Activity")

    __table_args__ = (Index("unique_timeline_activities", "timeline_id", "order", unique=True),)



# Activity belong to category 
class Activity(db.Model):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(80))
    photo_url = Column(String(150))
    description = Column(String(1500))
    category_id = Column(Integer, ForeignKey("categories.id"),nullable=False)
    website_url = Column(String(150))
    google_map_url = Column(String(150))

    category = relationship("Category")

    timeline_activities = relationship("TimelineActivity", uselist=True)



# Each Category has many activities 
class Category(db.Model):
    __tablename__ = "categories"

    id = Column(Integer,primary_key=True, autoincrement=True)
    name = Column(String(80))
    symbol_url = Column(String(120))

    activities = relationship("Activity", uselist=True) 




class WeatherCache(db.Model):
    __tablename__ = "weather_cache"

    id = Column(Integer, primary_key=True)
    weather = Column(String(1024))
    update_time = Column(DateTime)


    
