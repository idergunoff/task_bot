import datetime

from sqlalchemy import create_engine, Column, Integer, BigInteger, String, DateTime, Text, Boolean, ForeignKey, Float, func, desc, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


DATABASE_NAME = 'task_db.sqlite'

engine = create_engine(f'sqlite:///{DATABASE_NAME}', echo=False)
Session = sessionmaker(bind=engine)

Base = declarative_base()


class Chat(Base):
    __tablename__ = 'chat'

    chat_id = Column(BigInteger, primary_key=True)
    title = Column(String)

    participants = relationship('Participant', back_populates='chat')
    tasks = relationship('Task', back_populates='chat')


class User(Base):
    __tablename__ = 'user'

    t_id = Column(BigInteger, primary_key=True)
    name = Column(String)
    super_admin = Column(Boolean, default=False)
    task_list = Column(String, default='all')

    participants = relationship('Participant', back_populates='user')
    task_create = relationship('Task', back_populates='user_create')
    task_for = relationship('TaskForUser', back_populates='user')


class Participant(Base):
    __tablename__ = 'participant'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('user.t_id'))
    chat_id = Column(BigInteger, ForeignKey('chat.chat_id'))
    admin = Column(Boolean, default=False)
    moderator = Column(Boolean, default=False)

    user = relationship('User', back_populates='participants')
    chat = relationship('Chat', back_populates='participants')


class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, ForeignKey('chat.chat_id'))
    title = Column(String)
    description = Column(Text)
    date_create = Column(DateTime)
    date_edit = Column(DateTime)
    date_end = Column(DateTime)
    user_id_create = Column(BigInteger, ForeignKey('user.t_id'))
    user_id_edit = Column(BigInteger)
    photo = Column(String)
    completed = Column(Boolean, default=False)
    date_complete = Column(DateTime)
    show_chat = Column(Boolean, default=False)

    chat = relationship('Chat', back_populates='tasks')
    user_create = relationship('User', back_populates='task_create')
    for_user = relationship('TaskForUser', back_populates='task')


class TaskForUser(Base):
    __tablename__ = 'task_for_user'

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id'))
    user_id = Column(BigInteger, ForeignKey('user.t_id'))

    task = relationship('Task', back_populates='for_user')
    user = relationship('User', back_populates='task_for')


Base.metadata.create_all(engine)
