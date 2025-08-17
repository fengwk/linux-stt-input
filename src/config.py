import yaml
from pathlib import Path

class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, config_path="config.yaml"):
        self.config_path = Path(config_path)
        self.settings = self._load_defaults()
        self._load_user_config()

    def _load_defaults(self):
        """
        Loads the default configuration settings.
        """
        return {
            "hotkey": "<alt>+z",
            "type_delay": 30,
            "model": {
                "size": "small",
                "language": "zh",
                "compute_type": "float16",
                "device": "cuda",
            }
        }

    def _load_user_config(self):
        """
        Loads user settings from the config file and merges them with defaults.
        """
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    self._deep_merge(self.settings, user_config)

    def _deep_merge(self, source, destination):
        """
        Recursively merges destination dict into source dict.
        """
        for key, value in destination.items():
            if isinstance(value, dict) and key in source and isinstance(source[key], dict):
                self._deep_merge(source[key], value)
            else:
                source[key] = value

    def get(self, key, default=None):
        """
        Retrieves a value from the settings.
        """
        return self.settings.get(key, default)

# Singleton instance
config = Config()

