import pytest
import types

import streamermcp

def test_streamer_get_windows():
    result = streamermcp.streamer_get_windowname_list()
    assert isinstance(result, list)
    assert all(isinstance(w, str) for w in result)

def test_streamer_fullscreen_capture():
    img = streamermcp.streamer_fullscreen_capture()
    assert hasattr(img, "data")
    assert hasattr(img, "format")
    assert img.format == "png"

def test_get_current_datetime():
    dt = streamermcp.get_current_datetime()
    assert isinstance(dt, str)
    assert len(dt) >= 10

def test_wait_and_get_current_datetime():
    dt = streamermcp.wait_and_get_current_datetime(1)
    assert isinstance(dt, str)

def test_streamer_get_audio_devices():
    devices = streamermcp.streamer_get_audio_devices()
    assert isinstance(devices, list)
    assert all(isinstance(d, str) for d in devices)

def test_obs_list_scenes(monkeypatch):
    # OBS接続をモック
    class DummyWS:
        def connect(self): pass
        def disconnect(self): pass
        def call(self, req):
            class DummyResp:
                def getScenes(self):
                    return [{"sceneName": "Scene1"}, {"sceneName": "Scene2"}]
            return DummyResp()
    monkeypatch.setattr(streamermcp, "_obs_connect", lambda: DummyWS())
    scenes = streamermcp.obs_list_scenes()
    assert scenes == ["Scene1", "Scene2"]

def test_obs_get_current_scene(monkeypatch):
    class DummyWS:
        def connect(self): pass
        def disconnect(self): pass
        def call(self, req):
            class DummyResp:
                def getName(self): return "Scene1"
            return DummyResp()
    monkeypatch.setattr(streamermcp, "_obs_connect", lambda: DummyWS())
    scene = streamermcp.obs_get_current_scene()
    assert scene == "Scene1"

def test_obs_update_text_source_in_current_scene(monkeypatch):
    class DummyWS:
        def connect(self): pass
        def disconnect(self): pass
        def call(self, req): return None
    monkeypatch.setattr(streamermcp, "_obs_connect", lambda: DummyWS())
    assert streamermcp.obs_update_text_source_in_current_scene("src", "text", "#00FF00")

# GUIや音声再生、実際のOBS操作などは自動テストが難しいため省略または手動確認推奨

# pytest test_streamermcp.py で実行可能