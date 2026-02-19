"""Unit tests for video editor data models."""

from pathlib import Path
from apps.video.models import VideoProject, Track, Clip, MediaItem, TrackType


def test_project_default_tracks():
    project = VideoProject()
    project.add_default_tracks()
    assert len(project.tracks) == 4
    assert project.tracks[0].name == "V1"
    assert project.tracks[0].track_type == TrackType.VIDEO
    assert project.tracks[2].name == "A1"
    assert project.tracks[2].track_type == TrackType.AUDIO


def test_add_media():
    project = VideoProject()
    item = project.add_media(Path("test.mp4"), duration_ms=5000, media_type="video")
    assert item.name == "test.mp4"
    assert item.duration_ms == 5000
    assert item.media_type == "video"
    assert len(project.media_items) == 1


def test_get_media_item():
    project = VideoProject()
    item = project.add_media(Path("test.mp4"), duration_ms=5000)
    found = project.get_media_item(item.id)
    assert found is item
    assert project.get_media_item("nonexistent") is None


def test_add_clip_to_track():
    project = VideoProject()
    project.add_default_tracks()
    item = project.add_media(Path("clip.mp4"), duration_ms=3000, media_type="video")
    clip = project.add_clip_to_track(0, item, position_ms=1000)
    assert clip is not None
    assert clip.position_ms == 1000
    assert clip.duration_ms == 3000
    assert clip.name == "clip.mp4"
    assert len(project.tracks[0].clips) == 1


def test_add_clip_invalid_track():
    project = VideoProject()
    project.add_default_tracks()
    item = project.add_media(Path("clip.mp4"), duration_ms=3000)
    result = project.add_clip_to_track(10, item)
    assert result is None


def test_remove_clip():
    project = VideoProject()
    project.add_default_tracks()
    item = project.add_media(Path("clip.mp4"), duration_ms=3000)
    clip = project.add_clip_to_track(0, item)
    assert project.remove_clip(clip.id)
    assert len(project.tracks[0].clips) == 0
    assert not project.remove_clip("nonexistent")


def test_duration_auto_expands():
    project = VideoProject()
    project.add_default_tracks()
    item = project.add_media(Path("long.mp4"), duration_ms=120000)
    project.add_clip_to_track(0, item, position_ms=0)
    assert project.duration_ms > 120000


def test_media_item_unique_ids():
    item1 = MediaItem()
    item2 = MediaItem()
    assert item1.id != item2.id


def test_clip_unique_ids():
    clip1 = Clip()
    clip2 = Clip()
    assert clip1.id != clip2.id
