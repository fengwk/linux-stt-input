import logging
import sys
from pynput import keyboard
from src.config import config
from src.stt_engine import STTEngine
import signal
import zhconv
import subprocess
import time
import threading

class HotkeyListener:
    """
    Listens for a global hotkey to start and stop the STT engine.
    Press and hold the hotkey to record, release to stop.
    """
    def __init__(self):
        self.config = config
        self.hotkey_str = self.config.get('hotkey', '<alt>+z')
        self.type_delay = self.config.get('type_delay', 30)
        self.engine = STTEngine(on_record_callback=self._print_text)
        self.listener = None
        self.text_buffer = []
        self.buffer_lock = threading.Lock()
        
        self.target_modifier = None
        self.target_key = None
        self._parse_hotkey()

        self.modifier_keys = set()
        self.hotkey_active = False

    def _parse_hotkey(self):
        """Parses the hotkey string from config into pynput key objects."""
        try:
            parts = self.hotkey_str.lower().split('+')
            if len(parts) != 2:
                raise ValueError("Hotkey must be in the format '<modifier>+<key>'")
            
            modifier_str = parts[0]
            key_str = parts[1]

            # Map string to pynput Key object
            modifier_map = {
                '<alt>': keyboard.Key.alt,
                '<ctrl>': keyboard.Key.ctrl,
                '<shift>': keyboard.Key.shift,
                '<cmd>': keyboard.Key.cmd,
            }
            self.target_modifier = modifier_map.get(modifier_str)
            if not self.target_modifier:
                raise ValueError(f"Unknown modifier: {modifier_str}")

            self.target_key = keyboard.KeyCode.from_char(key_str)

        except Exception as e:
            logging.error(f"Invalid hotkey string '{self.hotkey_str}': {e}")
            sys.exit(1)

    def _print_text(self, text):
        """Callback to collect transcribed text chunks."""
        print("print_text:", text)
        if text:
            with self.buffer_lock:
                self.text_buffer.append(text)
        self._type_text_if_needed()

    def _type_text_if_needed(self):
        """Joins, converts, and types out the collected text if allowed."""
        with self.buffer_lock:
            if self.hotkey_active or not self.text_buffer:
                return
            
            full_text = "".join(self.text_buffer)
            self.text_buffer.clear()

            simplified_text = zhconv.convert(full_text, 'zh-cn')
            if simplified_text:
                try:
                    time.sleep(0.1) # Ensure modifier key release is processed
                    cmd = [
                        "xdotool", "type",
                        "--delay", str(self.type_delay),
                        "--clearmodifiers", simplified_text
                    ]
                    subprocess.run(cmd, check=True)
                except FileNotFoundError:
                    logging.error("xdotool not found. Please install it to use text input.")
                except subprocess.CalledProcessError as e:
                    logging.error(f"Error using xdotool: {e}")

    def on_press(self, key):
        if key in {keyboard.Key.alt, keyboard.Key.ctrl, keyboard.Key.shift, keyboard.Key.cmd}:
            self.modifier_keys.add(key)

        if self.target_modifier in self.modifier_keys and key == self.target_key:
            if not self.hotkey_active:
                self.hotkey_active = True
                self.engine.start_record()

    def on_release(self, key):
        if self.hotkey_active and (key == self.target_key or key == self.target_modifier):
            self.engine.stop_record()
            self.hotkey_active = False
            self._type_text_if_needed()

        if key in self.modifier_keys:
            self.modifier_keys.remove(key)

    def run(self):
        print("Hotkey listener started. Press and hold your hotkey to start recording.")
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()
        self.listener.join()

    def close(self, signum, frame):
        logging.info("Closing Hotkey Listener...")
        if self.engine:
            self.engine.close()
        if self.listener:
            self.listener.stop()
        logging.info("Hotkey Listener closed.")

