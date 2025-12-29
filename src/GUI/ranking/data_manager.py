from pathlib import Path
import json
import os
from src.GUI.ranking.managers.tournament_manager import TournamentManager
from src.GUI.ranking.managers.player_manager import PlayerManager
from src.GUI.ranking.managers.rules_manager import RulesManager

class DataManager:
    def __init__(self):
        # Load API key from config file if it exists
        if os.path.exists("data/config.json"):
            with open("data/config.json", "r") as config_file:
                config_data = json.load(config_file)
                self._api_key = config_data.get("api_key", "")
        else:
            self._api_key = ""
        
        self._tournament_manager = TournamentManager()
        self._player_manager = PlayerManager()
        self._rules_manager = RulesManager()
        
    def get_api_key(self):
        return self._api_key
        
    def save_api_key(self, api_key):
        self._api_key = api_key
        config_data = {"api_key": api_key}
        
        # Set up data directory and config file path
        data_dir = Path("data")
        config_path = data_dir / "config.json"
        
        # Save the API key to the config file
        data_dir.mkdir(exist_ok=True)
        with config_path.open("w") as config_file:
            json.dump(config_data, config_file)
            
    def get_tournament_manager(self):
        return self._tournament_manager
    
    def get_player_manager(self):
        return self._player_manager
    
    def get_rules_manager(self):
        return self._rules_manager