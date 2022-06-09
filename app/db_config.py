import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

engine = create_engine(
    os.getenv('SQLALCHEMY_DATABASE_URL')
)

# Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# session = Session()
conn = engine.connect()

# session.execute('create table review_videos (id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, user_id INT, file_url varchar(2000))')