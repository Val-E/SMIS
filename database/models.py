import os

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base

from settings import DATABASE_PATH


# create engine
engine = create_engine(f"sqlite:///{DATABASE_PATH}")

# create Session Object
Session = sessionmaker(bind=engine)
session = Session()

# create base
base = declarative_base()


# database schema
class User(base):
    """the table stores information about users"""
    __tablename__ = "User"

    # scraped information
    user_id = Column("id", Integer, primary_key=True)
    user_handle = Column("user_handle", String, unique=True)
    username = Column("full_name", String)
    biography = Column("biography", String)
    
    # processed or calculated information
    age = Column("age", Integer)
    sex = Column("sex", String)
    cities = Column("cities", String)
    nationalities = Column("nationalities", String)
    sexual_orientations = Column("sexual_orientations", String)
    political_classifications = Column("political_orientations", String)


class Following(base):
    """the table outlines the following relations"""
    __tablename__ = "Following"

    relation_id = Column("id", Integer, primary_key=True)
    following_user = Column("following_user", String)
    followed_user = Column("followed_user", String)


# create database, if it does not exist
if not os.path.exists(DATABASE_PATH):
    base.metadata.create_all(engine)

