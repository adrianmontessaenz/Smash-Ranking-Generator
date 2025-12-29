from pathlib import Path
import json
import os

class PlayerManager:
    def __init__(self):
        # Load player data (if any)
        if os.path.exists("data/players.json"):
            with open("data/players.json", "r") as players_file:
                self._players = json.load(players_file)
        else:
            self._players = []
        
        
    def get_players(self):
        return self._players
    
    def add_player(self, player_data):
        self._players.append(player_data)
        self._save_players()
        
    def _save_players(self):
        with open("data/players.json", "w") as players_file:
            json.dump(self._players, players_file)