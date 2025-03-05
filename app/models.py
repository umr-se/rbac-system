from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    is_admin = Column(Boolean, default=False)
    
    events = relationship("CalendarEvent", back_populates="owner")
    
class CalendarEvent(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    summary = Column(String(255), index=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    location = Column(String(255), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="events")    