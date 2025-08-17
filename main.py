from src.hotkey_listener import HotkeyListener
import signal

def main():
    """
    The main entry point of the application.
    """
    listener = HotkeyListener()

    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, listener.close)
    signal.signal(signal.SIGTERM, listener.close)

    listener.run()

if __name__ == "__main__":
    main()
