import sqlalchemy
from sqlalchemy import orm

from sqlalchemy_serializer import SerializerMixin

from data import db_session


class Task(db_session.SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'tasks'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    founder = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    project = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('projects.id'), nullable=True)
    category = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('categories.id'))

    deadline_date = sqlalchemy.Column(sqlalchemy.Date, nullable=True)
    deadline_time = sqlalchemy.Column(sqlalchemy.Time, nullable=True)

    replay_every_day = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    replay_every_week = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    finish_date = sqlalchemy.Column(sqlalchemy.Date, nullable=True)

    # непонятно, зачем они
    fnd = orm.relationship('User')
    prj = orm.relationship('Project')

    ct = orm.relationship('Category')