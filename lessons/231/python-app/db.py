import os

from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, create_engine


POSTGRES_URI = os.environ['POSTGRES_URI']
POSTGRES_POOL_SIZE = int(os.environ['POSTGRES_POOL_SIZE'])


engine = create_engine(POSTGRES_URI, pool_size=POSTGRES_POOL_SIZE)


def get_postgres_session():
    with Session(engine) as session:
        yield session


PostgresDep = Annotated[Session, Depends(get_postgres_session)]
