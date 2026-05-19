from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base
import datetime

# This defines the structure of the table where our news will be saved
class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    url = Column(String)
    source = Column(String)
    summary = Column(Text, nullable=True)
    topic = Column(String, default="Unclustered")
    sentiment = Column(String, default="Neutral")
    fetched_at = Column(DateTime, default=datetime.datetime.utcnow)