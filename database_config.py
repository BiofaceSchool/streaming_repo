from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

MYSQL_USER = 'avnadmin'
MYSQL_PASSWORD = 'AVNS_p4eqcG5krosx1-Xrwja'
MYSQL_HOST = 'bioface-enzotrujilloacosta-8de3.h.aivencloud.com'
MYSQL_PORT = '28733'
MYSQL_DATABASE = 'defaultdb'

URL_DATABASE = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'

engine = create_engine(URL_DATABASE, connect_args={"ssl": {"ssl-mode": "REQUIRED"}})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

