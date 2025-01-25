import pytest
from catifier.auth.database import Base, engine


def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
