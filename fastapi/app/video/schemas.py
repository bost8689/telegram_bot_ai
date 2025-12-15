from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# Video
class VideoBase(BaseModel):
    creator_id: str
    video_created_at: datetime

    views_count: int = 0
    likes_count: int = 0
    comments_count: int = 0
    reports_count: int = 0


class VideoCreate(VideoBase):
    id: str 


class VideoUpdate(BaseModel):
    views_count: Optional[int] = None
    likes_count: Optional[int] = None
    comments_count: Optional[int] = None
    reports_count: Optional[int] = None


class VideoInDBBase(VideoBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Video(VideoInDBBase):
    pass


class VideoWithSnapshots(VideoInDBBase):
    snapshots: List["VideoSnapshot"] = []

# VideoSnapshot
class VideoSnapshotBase(BaseModel):
    video_id: str

    views_count: int
    likes_count: int
    comments_count: int
    reports_count: int

    delta_views_count: int = 0
    delta_likes_count: int = 0
    delta_comments_count: int = 0
    delta_reports_count: int = 0


class VideoSnapshotCreate(VideoSnapshotBase):
    id: str
    created_at: Optional[datetime] = None  # можно не указывать — будет now()


class VideoSnapshotUpdate(BaseModel):
    views_count: Optional[int] = None
    likes_count: Optional[int] = None
    comments_count: Optional[int] = None
    reports_count: Optional[int] = None

    delta_views_count: Optional[int] = None
    delta_likes_count: Optional[int] = None
    delta_comments_count: Optional[int] = None
    delta_reports_count: Optional[int] = None


class VideoSnapshotInDBBase(VideoSnapshotBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VideoSnapshot(VideoSnapshotInDBBase):
    pass

VideoWithSnapshots.model_rebuild()