import datetime

from sqlalchemy import BigInteger
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from config import SQLALCHEMY_URL
from sqlalchemy import ForeignKey

engine = create_async_engine(SQLALCHEMY_URL, echo=True)

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    user_id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column()
    surname: Mapped[str] = mapped_column()
    mode: Mapped[str] = mapped_column()

class Project(Base):
    __tablename__ = 'projects'
    
    project_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    token: Mapped[str] = mapped_column()
    created_date: Mapped[datetime.datetime] = mapped_column()
    updated_date: Mapped[datetime.datetime] = mapped_column()

class Personal_task(Base):
    __tablename__ = 'personal_tasks'
    
    task_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    status: Mapped[str] = mapped_column()
    created_date: Mapped[datetime.datetime] = mapped_column()
    updated_date: Mapped[datetime.datetime] = mapped_column()
    due_date: Mapped[datetime.datetime] = mapped_column(nullable=True)
    
class Corporate_task(Base):
    __tablename__ = 'corporate_tasks'
    
    task_id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.project_id'))
    creator_id: Mapped[int] = mapped_column(ForeignKey('users.user_id')) 
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    status: Mapped[str] = mapped_column()
    created_date: Mapped[datetime.datetime] = mapped_column()
    updated_date: Mapped[datetime.datetime] = mapped_column()
    due_date: Mapped[datetime.datetime] = mapped_column()
    
class Corporate_subtask(Base):
    __tablename__ = 'corporate_subtasks'
    
    subtask_id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('corporate_tasks.task_id'))
    creator_id: Mapped[int] = mapped_column(ForeignKey('users.user_id')) 
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    priotity: Mapped[str] = mapped_column()
    status: Mapped[str] = mapped_column()
    created_date: Mapped[datetime.datetime] = mapped_column()
    updated_date: Mapped[datetime.datetime] = mapped_column()
    due_date: Mapped[datetime.datetime] = mapped_column()

class Task_assignees(Base):
    __tablename__ = 'task_assignees'
    
    task_assignees_id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('corporate_tasks.task_id'))
    subtask_id: Mapped[int] = mapped_column(ForeignKey('corporate_subtasks.subtask_id'))
    assignees_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))
    

async def async_main():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
