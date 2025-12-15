# models.py
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True, index=True)  # или UUID(as_uuid=True) для PostgreSQL
    creator_id = Column(String, nullable=False)         # 32-символьный hex или UUID — всё равно строка
    video_created_at = Column(DateTime(timezone=True), nullable=False)

    views_count = Column(Integer, default=0, nullable=False)
    likes_count = Column(Integer, default=0, nullable=False)
    comments_count = Column(Integer, default=0, nullable=False)
    reports_count = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class VideoSnapshot(Base):
    __tablename__ = "video_snapshots"

    id = Column(String, primary_key=True, index=True)
    video_id = Column(String, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)

    views_count = Column(Integer, nullable=False)
    likes_count = Column(Integer, nullable=False)
    comments_count = Column(Integer, nullable=False)
    reports_count = Column(Integer, nullable=False)

    delta_views_count = Column(Integer, nullable=False, default=0)
    delta_likes_count = Column(Integer, nullable=False, default=0)
    delta_comments_count = Column(Integer, nullable=False, default=0)
    delta_reports_count = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())