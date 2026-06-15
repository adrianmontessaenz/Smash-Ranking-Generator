"""Player manager for storing player records and ranking columns.

This module provides `PlayerManager`, which persists `data/players.json`
and offers basic CRUD operations for players and ranking types.
"""

from pathlib import Path
import json
import os


class PlayerManager:
    """Manage players and ranking definitions persisted to disk."""
    def __init__(self):
        """Load players and rankings from `data/players.json`.

        If the file does not exist a default structure is created.
        """
        # Load player data (if any)
        if os.path.exists("data/players.json"):
            print("Loading player data...")
            with open("data/players.json", "r") as players_file:
                player_data_json = json.load(players_file)
                self._players = player_data_json["players"]
                self._rankings = player_data_json["rankings"]
        else:
            self._players = {}
            self._rankings = {"No Ranking": 1.0}
            self._save_data()

    def get_players(self):
        """Return the mapping of player name to their ranking data."""
        return self._players
    
    def get_rankings(self):
        """Return the ranking columns and their multipliers."""
        return self._rankings
    
    def add_player(self, player_name, ranking_data):
        """Add a player if they do not already exist and persist.

        Args:
            player_name (str): Player identifier.
            ranking_data (dict): Mapping of ranking name to value.
        """
        for player in self._players.keys():
            if player == player_name:
                return  # Player already exists
        self._players[player_name] = ranking_data
        self._save_data()
    
    def remove_player(self, player_name):
        """Remove a player by name and persist changes."""
        if player_name in self._players:
            del self._players[player_name]
            self._save_data()
    
    def edit_player(self, player_name, new_ranking_data):
        """Replace a player's ranking data and persist."""
        if player_name in self._players:
            self._players[player_name] = new_ranking_data
            self._save_data()
    
    def add_ranking(self, ranking_name, ranking_multiplier):
        """Add a ranking column with the given multiplier."""
        for ranking in self._rankings.keys():
            if ranking == ranking_name:
                return  # Ranking already exists
        self._rankings[ranking_name] = ranking_multiplier
        self._save_data()
    
    def remove_ranking(self, ranking_name):
        """Remove a ranking column and persist changes."""
        if ranking_name in self._rankings:
            del self._rankings[ranking_name]
            self._save_data()
    
    def edit_ranking(self, ranking_name, new_multiplier):
        """Update the multiplier for a ranking column and persist."""
        if ranking_name in self._rankings:
            self._rankings[ranking_name] = new_multiplier
            self._save_data()
            
    def _save_data(self):
        """Persist players and rankings to `data/players.json`."""
        with open("data/players.json", "w") as players_file:
            json.dump({
                "players": self._players,
                "rankings": self._rankings
            }, players_file, indent=4)

