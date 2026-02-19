"""Video Editor data models."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from enum import Enum, auto
import uuid


class TrackType(Enum):
    VIDEO = auto()
    AUDIO = auto()


@dataclass
class MediaItem:
    """An imported media file in the project bin."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    file_path: Path = field(default_factory=Path)
    name: str = ""
    duration_ms: int = 0
    media_type: str = ""  # "video", "audio", "image"


@dataclass
class Clip:
    """A clip placed on a timeline track."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    media_item_id: str = ""
    source_path: Path = field(default_factory=Path)
    track_index: int = 0
    position_ms: int = 0
    duration_ms: int = 0
    in_point_ms: int = 0
    out_point_ms: int = 0
    name: str = ""
    color: str = "#3498db"


@dataclass
class Track:
    """A single track in the timeline."""
    name: str = ""
    track_type: TrackType = TrackType.VIDEO
    index: int = 0
    clips: list[Clip] = field(default_factory=list)


@dataclass
class VideoProject:
    """Top-level project container."""
    name: str = "Untitled"
    media_items: list[MediaItem] = field(default_factory=list)
    tracks: list[Track] = field(default_factory=list)
    duration_ms: int = 60_000
    playhead_ms: int = 0

    def add_default_tracks(self):
        self.tracks = [
            Track(name="V1", track_type=TrackType.VIDEO, index=0),
            Track(name="V2", track_type=TrackType.VIDEO, index=1),
            Track(name="A1", track_type=TrackType.AUDIO, index=2),
            Track(name="A2", track_type=TrackType.AUDIO, index=3),
        ]

    def get_media_item(self, media_id: str) -> Optional[MediaItem]:
        for item in self.media_items:
            if item.id == media_id:
                return item
        return None

    def add_media(self, file_path: Path, duration_ms: int = 0, media_type: str = "video") -> MediaItem:
        item = MediaItem(
            file_path=file_path,
            name=file_path.name,
            duration_ms=duration_ms,
            media_type=media_type,
        )
        self.media_items.append(item)
        return item

    def add_clip_to_track(self, track_index: int, media_item: MediaItem,
                          position_ms: int = 0) -> Optional[Clip]:
        if track_index < 0 or track_index >= len(self.tracks):
            return None
        track = self.tracks[track_index]
        clip = Clip(
            media_item_id=media_item.id,
            source_path=media_item.file_path,
            track_index=track_index,
            position_ms=position_ms,
            duration_ms=media_item.duration_ms,
            in_point_ms=0,
            out_point_ms=media_item.duration_ms,
            name=media_item.name,
            color="#3498db" if track.track_type == TrackType.VIDEO else "#2c3e50",
        )
        track.clips.append(clip)
        end = position_ms + clip.duration_ms
        if end > self.duration_ms:
            self.duration_ms = end + 5000
        return clip

    def remove_clip(self, clip_id: str) -> bool:
        for track in self.tracks:
            for i, clip in enumerate(track.clips):
                if clip.id == clip_id:
                    track.clips.pop(i)
                    return True
        return False
