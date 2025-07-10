from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Date, create_engine
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

Base = declarative_base()

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    tasks = relationship('Task', back_populates='project', cascade='all, delete-orphan')

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(Date, nullable=True)
    completed = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    project = relationship('Project', back_populates='tasks')

class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    completed = Column(Boolean, default=False)

# SQLite engine setup
engine = create_engine('sqlite:///app.db', connect_args={"check_same_thread": False})

# Project Schemas
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}

# Task Schemas
class TaskCreate(BaseModel):
    project_id: int
    name: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    completed: Optional[bool] = False
    order: Optional[int] = 0

class TaskRead(BaseModel):
    id: int
    project_id: int
    name: str
    description: Optional[str]
    due_date: Optional[date]
    completed: bool
    order: int
    model_config = {"from_attributes": True}

# Event Schemas
class EventCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_time: datetime
    completed: Optional[bool] = False

class EventRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_time: datetime
    completed: bool
    model_config = {"from_attributes": True} 