import logging
from RealtimeSTT import AudioToTextRecorder
from .config import config
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class STTEngine:
    """
    The core Speech-to-Text engine, designed to run in a separate process.
    """
    def __init__(self, on_record_callback=None):
        model_config = config.get('model', {})
        self.running = True
        self.on_record_callback = on_record_callback
        self.record_event = threading.Event()
        
        logging.info("Initializing STT Engine...")
        print(model_config)
        self.recorder = AudioToTextRecorder(
            model=model_config.get('size', 'small'),
            language=model_config.get('language', ''),
            compute_type=model_config.get('compute_type', 'default'),
            level=logging.WARNING,
            device=model_config.get('device', 'cuda'),
            spinner=False,
            post_speech_silence_duration=3.,
            allowed_latency_limit=1000
        )
        
        self.stt_thread = threading.Thread(target=self._run, daemon=True)
        self.stt_thread.start()
        logging.info("STT Engine initialized.")

    def is_record(self):
        return self.record_event.is_set()

    def _run(self):
        while self.running:
            self.record_event.wait()
            if not self.running:
                break

            print("STT Engine is running. Speak into your microphone.")
            try:
                while self.running and self.record_event.is_set():
                    if self.on_record_callback:
                        self.recorder.text(self.on_record_callback)
            except Exception as e:
                logging.error(f"Error in transcription loop: {e}")
        

    def start_record(self):
        if not self.record_event.is_set():
            self.recorder.start()
            self.record_event.set()
            print("Recording started.")

    def stop_record(self):
        if self.record_event.is_set():
            self.record_event.clear()
            self.recorder.stop()
            print("Recording stopped.")

    def close(self):
        logging.info("Closing STT Engine...")
        self.running = False
        self.record_event.set()  # Wake up the main loop to exit

        if self.recorder and not self.recorder.is_shut_down:
            logging.info("Shutting down audio recorder...")
            self.recorder.stop()
            self.recorder.shutdown()
            logging.info("Audio recorder shut down.")

        if self.stt_thread.is_alive():
            self.stt_thread.join(timeout=2)  # Add a timeout
        
        print("STT Engine closed.")