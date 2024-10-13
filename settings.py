# settings.py

import json
import os

class AppSettings:
    def __init__(self, config_file='settings.json'):
        self.config_file = config_file
        self.settings = {
            "checksum_algorithm": "CRC32",
            "default_directory": os.getcwd(),
            "logging_enabled": True,
            "log_file_path": "sfv_checker_debug.log",
            "log_format": "TXT",
            "history": []
        }
        self.load_settings()
    
    def load_settings(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.settings.update(json.load(f))
            except Exception as e:
                print(f"Error loading settings: {e}")
    
    def save_settings(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    # Getter methods
    def get_checksum_algorithm(self):
        return self.settings.get("checksum_algorithm", "CRC32")
    
    def get_default_directory(self):
        return self.settings.get("default_directory", os.getcwd())
    
    def get_logging_enabled(self):
        return self.settings.get("logging_enabled", True)
    
    def get_log_file_path(self):
        return self.settings.get("log_file_path", "sfv_checker_debug.log")
    
    def get_log_format(self):
        return self.settings.get("log_format", "TXT")
    
    def get_history(self):
        return self.settings.get("history", [])
    
    # Setter methods
    def set_checksum_algorithm(self, algorithm):
        self.settings["checksum_algorithm"] = algorithm
        self.save_settings()
    
    def set_default_directory(self, directory):
        self.settings["default_directory"] = directory
        self.save_settings()
    
    def set_logging_enabled(self, enabled):
        self.settings["logging_enabled"] = enabled
        self.save_settings()
    
    def set_log_file_path(self, path):
        self.settings["log_file_path"] = path
        self.save_settings()
    
    def set_log_format(self, format):
        self.settings["log_format"] = format
        self.save_settings()
    
    # History methods
    def add_history_entry(self, entry):
        self.settings["history"].append(entry)
        self.save_settings()
    
    def clear_history(self):
        self.settings["history"] = []
        self.save_settings()
