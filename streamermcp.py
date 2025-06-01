import pathlib
from pprint import pprint
from fastmcp import FastMCP, Image
# pip install pywin32 mss
import win32gui
import mss
# pip install Pillow
import PIL.Image
import tkinter as tk
from tkinter import simpledialog

# pip install openai
from openai import OpenAI
import pydub
from pydub import AudioSegment

import io
import time

# 追加: sounddevice, numpy
import sounddevice as sd
import numpy as np

# pip install obsws-python
import obsws_python as obs



# Create an MCP server
mcp = FastMCP("StreamerMCP",
              description="Tools that support video streaming via the Model Context Protocol(MCP)")

# 画像をキャプチャする
@mcp.tool()
def streamer_fullscreen_capture(resizeRatio:float=0.25) -> Image:
    """Capture full screen in PC."""

    with mss.mss() as sct:
        # 全画面キャプチャ
        monitor = sct.monitors[0]  # 全画面のモニター情報を取得
        screenshot = sct.grab(monitor)
        # mssのScreenShotオブジェクトをPillowのImageオブジェクトに変換
        img = PIL.Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        new_size = (int(img.width * resizeRatio), int(img.height * resizeRatio)) # 幅と高さを50%にリサイズ
        img_resized = img.resize(new_size, PIL.Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        img_resized.save(buffer, format='PNG', optimize=True, compress_level=9)
        # Reset the buffer position to the beginning
        buffer.seek(0)
        # Return an Image object with the data and format of the buffer
        return Image(data=buffer.getvalue(), format="png")

# Window一覧を取得する
@mcp.tool()
def streamer_get_windowname_list() -> list[str]:
    """Get a list of visible window titles."""
    windows = []

    def enum_handler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:  # 空でないタイトルのみ
                windows.append(title)

    win32gui.EnumWindows(enum_handler, None)
    return windows

# Windowをキャプチャする
@mcp.tool()
def streamer_window_capture(windowname: str, resizeRatio: float = 0.25) -> Image:
    """Capture the specified window by name."""
    hwnd = None

    def enum_handler(h, ctx):
        nonlocal hwnd
        if win32gui.IsWindowVisible(h):
            title = win32gui.GetWindowText(h)
            if title == windowname:
                hwnd = h

    win32gui.EnumWindows(enum_handler, None)
    if hwnd is None:
        raise ValueError(f"Window '{windowname}' not found.")

    # ウィンドウの位置とサイズを取得
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top

    with mss.mss() as sct:
        monitor = {"left": left, "top": top, "width": width, "height": height}
        screenshot = sct.grab(monitor)
        img = PIL.Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        new_size = (int(img.width * resizeRatio), int(img.height * resizeRatio))
        img_resized = img.resize(new_size, PIL.Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        img_resized.save(buffer, format='PNG', optimize=True, compress_level=9)
        buffer.seek(0)
        return Image(data=buffer.getvalue(), format="png")

# 現在の日時を取得する
@mcp.tool()
def get_current_datetime() -> str:
    """Get the current date and time."""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

# 指定秒数待機してから現在の日時を取得する
@mcp.tool()
def wait_and_get_current_datetime(seconds:int=180) -> str:
    """Wait for a specified number of seconds. 180 seconds is Maximum. return the current date and time."""
    if seconds > 180:
        time.sleep(180)
        return get_current_datetime()
    else:
        time.sleep(seconds)
        return  get_current_datetime()

# 音声出力デバイスの一覧を取得する
@mcp.tool()
def streamer_get_audio_devices() -> list[str]:
    """
    Get a list of available audio output device names.
    Returns a list of strings in the format: "[index] device name"
    """
    devices = sd.query_devices()
    output_devices = []
    for idx, d in enumerate(devices):
        # 出力チャンネルが1つ以上あるデバイスのみ
        if d['max_output_channels'] > 0:
            # インデックスとデバイス名をわかりやすく表示
            output_devices.append(f"[{idx}] {d['name']}")
    return output_devices

# 音声合成を行う
@mcp.tool()
def speak_tts(text:str, device:str|None=None) -> bool:
    """Speak a text string using the text-to-speech engine. Optionally specify output device name."""
    client = OpenAI(base_url="http://127.0.0.1:8880/v1", api_key="not-needed")

    buffer = io.BytesIO()
    # OpenAIの音声合成API互換のdocker imageを使用
    # https://github.com/remsky/Kokoro-FastAPI
    # 中身はKokoroの音声合成API
    # https://github.com/hexgrad/kokoro
    with client.audio.speech.with_streaming_response.create(
        model="kokoro",
        voice="jf_alpha", #single or multiple voicepack combo
        input=text
    ) as response:
        # レスポンスをバッファに書き込む
        for chunk in response.iter_bytes():
            buffer.write(chunk)
    buffer.seek(0)
    audio = AudioSegment.from_file(buffer, format="mp3")
    # sounddeviceで再生
    samples = np.array(audio.get_array_of_samples())
    if audio.channels == 2:
        samples = samples.reshape((-1, 2))
    sd.play(samples, samplerate=audio.frame_rate, device=device)
    sd.wait()
    return True

# ダイアログを表示して文字列を入力させる
@mcp.tool()
def show_askstring_dialog(title:str, message:str) -> str|None:
    """Show a dialog box to ask a string input from the human."""
    root = tk.Tk()
    root.withdraw()
    # 文字入力ダイアログを表示
    user_input:str|None = simpledialog.askstring(title, message)
    root.destroy()
    return user_input

# OBS接続設定
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = "your_password"  # OBSのWebSocketパスワードに合わせてください

def _obs_connect():
    cl = obs.ReqClient(host=OBS_HOST, port=OBS_PORT, password=OBS_PASSWORD)
    return cl 

# OBSのシーン一覧を取得
@mcp.tool()
def obs_list_scenes() -> list[str]:
    """Get a list of scene names from OBS."""
    cl = _obs_connect()
    try:
        scenes = cl.get_scene_list()
        scenes = [di.get("sceneName") for di in scenes.scenes] # シーンを逆順に取得
        return scenes
    finally:
        cl.disconnect()

# OBSのシーン切り替え
@mcp.tool()
def obs_switch_scene(scene_name: str) -> bool:
    """Switch to a specified scene in OBS."""
    cl = _obs_connect()
    try:
        cl.set_current_program_scene(scene_name)
        return True
    finally:
        cl.disconnect()

# OBSの現在のシーン名を取得
@mcp.tool()
def obs_get_current_scene() -> str:
    """Get the name of the current scene in OBS."""
    cl = _obs_connect()
    try:
        current = cl.get_current_program_scene()
        #pprint(current)
        return current.scene_name
    finally:
        cl.disconnect()

# OBSの現在のシーンにソースを一覧取得
@mcp.tool()
def obs_list_sources_in_current_scene() -> list[str]:
    """Get a list of source names in the current scene in OBS."""
    cs = _obs_connect()
    try:
        result = []
        current = cs.get_current_program_scene()
        scene_name = current.scene_name
        items = cs.get_scene_item_list(scene_name)
        #pprint(vars(items))
        for item in items.scene_items:
            #pprint(item)
            result.append(item.get("sourceName", "Unknown Source"))
        return result
    
    finally:
        cs.disconnect()

# OBSの現在のシーンのテキストソースを更新
@mcp.tool()
def obs_update_text_source_in_scene(source_name: str, text: str) -> bool:
    """
    Update the text of the specified text source in the scene in OBS.
    """
    ws = _obs_connect()
    try:
        # 現在の設定を取得して上書きする
        source_settings  = ws.get_input_settings(source_name)
        pprint(vars(source_settings ))
        input_settings = source_settings.input_settings
        pprint(input_settings)
        input_settings["text"] = text
        # 設定を更新
        ws.set_input_settings(source_name, input_settings, True)
        return True
    finally:
        ws.disconnect()

@mcp.tool()
def write_streamermcp_memo(content: str) -> bool:
    """
    Write the specified content to 'streamermcp_MEMO.txt'.
    Overwrites any existing content.
    """
    memo_path = pathlib.Path.cwd() / "streamermcp_MEMO.txt"
    with open(memo_path, "w", encoding="utf-8") as f:
        f.write(content)
    return True

@mcp.tool()
def read_streamermcp_memo() -> str:
    """
    Read and return the content of 'streamermcp_MEMO.txt'.
    Returns an empty string if the file does not exist.
    """
    memo_path = pathlib.Path.cwd() / "streamermcp_MEMO.txt"
    if memo_path.exists():
        with open(memo_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return ""

if __name__ == "__main__":
    mcp.run(transport="stdio")