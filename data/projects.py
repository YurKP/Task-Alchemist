import sqlalchemy

from sqlalchemy_serializer import SerializerMixin

from data import db_session


class Project(db_session.SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'projects'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    founder = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=True, )
    participants = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    is_finished = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    deadline = sqlalchemy.Column(sqlalchemy.Date, nullable=True)