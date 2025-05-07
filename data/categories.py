import sqlalchemy

from data import db_session


class Category(db_session.SqlAlchemyBase):
    __tablename__ = 'categories'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)