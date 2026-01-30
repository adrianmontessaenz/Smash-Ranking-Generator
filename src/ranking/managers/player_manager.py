from pathlib import Path
import json
import os

class PlayerManager:
    def __init__(self):
        # Load player data (if any)
        if os.path.exists("data/players.json"):
            with open("data/players.json", "r") as players_file:
                player_data_json = json.load(players_file)
                self._players = player_data_json["players"]
                self._rankings = player_data_json["rankings"]
        else:
            self._players = {}
            self._rankings = {"No Ranking": 1.0}
            self._save_data()
        
    def get_players(self):
        return self._players
    
    def get_rankings(self):
        return self._rankings
    
    def add_player(self, player_name, ranking_data):
        for player in self._players.keys():
            if player == player_name:
                return  # Player already exists
        self._players[player_name] = ranking_data
        self._save_data()
    
    def remove_player(self, player_name):
        if player_name in self._players:
            del self._players[player_name]
            self._save_data()
    
    def edit_player(self, player_name, new_ranking_data):
        if player_name in self._players:
            self._players[player_name] = new_ranking_data
            self._save_data()
    
    def add_ranking(self, ranking_name, ranking_multiplier):
        for ranking in self._rankings.keys():
            if ranking == ranking_name:
                return  # Ranking already exists
        self._rankings[ranking_name] = ranking_multiplier
        self._save_data()
    
    def remove_ranking(self, ranking_name):
        if ranking_name in self._rankings:
            del self._rankings[ranking_name]
            self._save_data()
    
    def edit_ranking(self, ranking_name, new_multiplier):
        if ranking_name in self._rankings:
            self._rankings[ranking_name] = new_multiplier
            self._save_data()
            
    def _save_data(self):
        with open("data/players.json", "w") as players_file:
            json.dump({
                "players": self._players,
                "rankings": self._rankings
            }, players_file, indent=4)
    
            