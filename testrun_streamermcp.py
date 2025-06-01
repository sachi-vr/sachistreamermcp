import sys
import streamermcp  # モジュール名を修正
import time

"""
This script is a test runner for the streammcp module.
"""

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_streammcp.py [windows|speak|audio_devices|window_capture|datetime|wait_datetime|askstring|obs_list|obs_create|obs_remove|obs_switch]")
        return

    cmd = sys.argv[1].lower()
    if cmd == "windows":
        print("Hello from streammcp! "+cmd)
        tmp: list[str] = streamermcp.streamer_get_windowname_list()
        print("Visible windows:", tmp)
    elif cmd == "speak":
        print("Hello from streammcp! "+cmd)
        device = None
        if "--device" in sys.argv:
            idx = sys.argv.index("--device")
            if idx + 1 < len(sys.argv):
                device = sys.argv[idx + 1]
        streamermcp.speak_tts("こんにちは、世界！日本語のテストです。マイクテストです。", device=device)
    elif cmd == "audio_devices":
        print("Hello from streammcp! "+cmd)
        devices = streamermcp.streamer_get_audio_devices()
        print("Audio output devices:")
        for d in devices:
            print(d)
    elif cmd == "full_capture":
        print("Testing full_capture...")
        img = streamermcp.streamer_fullscreen_capture()
        with open("test_capture.png", "wb") as f:
            f.write(img.data)
        print("Saved capture to test_capture.png")
    elif cmd == "window_capture":
        print("Testing window_capture...")
        windows = streamermcp.streamer_get_windowname_list()
        if not windows:
            print("No windows found.")
            return
        print("Available windows:")
        for i, w in enumerate(windows):
            print(f"{i}: {w}")
        idx = 0
        if len(sys.argv) > 2:
            try:
                idx = int(sys.argv[2])
            except Exception:
                pass
        windowname = windows[idx]
        print(f"Capturing window: {windowname}")
        img = streamermcp.streamer_window_capture(windowname)
        with open("test_capture.png", "wb") as f:
            f.write(img.data)
        print("Saved capture to test_capture.png")
    elif cmd == "datetime":
        print("Testing get_current_datetime...")
        print(streamermcp.get_current_datetime())
    elif cmd == "wait_datetime":
        seconds = 2
        if len(sys.argv) > 2:
            try:
                seconds = int(sys.argv[2])
            except Exception:
                pass
        print(f"Testing wait_and_get_current_datetime({seconds})...")
        print(streamermcp.wait_and_get_current_datetime(seconds))
    elif cmd == "askstring":
        print("Testing show_askstring_dialog...")
        result = streamermcp.show_askstring_dialog("テスト", "何か入力してください")
        print("Dialog result:", result)
    elif cmd == "obs_list":
        print("Testing obs_list_scenes...")
        try:
            scenes = streamermcp.obs_list_scenes()
            print("OBS scenes:", scenes)
        except Exception as e:
            print("OBS error:", e)
    elif cmd == "obs_switch":
        if len(sys.argv) < 3:
            print("Usage: python run_streammcp.py obs_switch <scene_name>")
            return
        scene_name = sys.argv[2]
        print(f"Switching to OBS scene: {scene_name}")
        try:
            result = streamermcp.obs_switch_scene(scene_name)
            print("Result:", result)
        except Exception as e:
            print("OBS error:", e)
    elif cmd == "obs_update_text":
        if len(sys.argv) < 4:
            print("Usage: python run_streammcp.py obs_update_text <source_name> <new_text>")
            return
        source_name = sys.argv[2]
        new_text = sys.argv[3]
        print(f"Updating OBS text source '{source_name}' with new text: {new_text}")
        try:
            result = streamermcp.obs_update_text_source_in_scene(source_name, new_text)
            print("Result:", result)
        except Exception as e:
            print("OBS error:", e)
    elif cmd == "obs_list_sources":
        print("Testing obs_list_sources_in_current_scene...")
        try:
            sources = streamermcp.obs_list_sources_in_current_scene()
            print("Sources in current OBS scene:", sources)
        except Exception as e:
            print("OBS error:", e)
    elif cmd == "obs_get_current_scene":
        print("Testing obs_get_current_scene...")
        try:
            current_scene = streamermcp.obs_get_current_scene()
            print("Current OBS scene:", current_scene)
        except Exception as e:
            print("OBS error:", e)
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python run_streammcp.py [windows|speak|audio_devices|window_capture|datetime|wait_datetime|askstring|obs_list|obs_create|obs_remove|obs_switch|obs_update_text|obs_list_sources]")



if __name__ == "__main__":
    print("Starting script...")
    start_time = time.time()
    main()
    elapsed = time.time() - start_time
    print(f"main() elapsed time: {elapsed:.3f} sec")
    print("Script finished.")