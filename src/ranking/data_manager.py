from pathlib import Path
import json
import os
from ranking.managers.tournament_manager import _TournamentManager
from ranking.managers.player_manager import PlayerManager
from ranking.managers.rules_manager import RulesManager

class DataManager:
    def __init__(self):  
        # Make sure data directory exists. If not, create it.
        if not os.path.exists("data"):
            os.makedirs("data")
        
        # Load managers            
        self._tournament_manager = _TournamentManager()
        self._player_manager = PlayerManager()
        self._rules_manager = RulesManager()
    
    # ------------ Tournament Manager Wrappers ------------ #
    def get_api_key(self):
        return self._tournament_manager.get_api_key()
        
    def save_api_key(self, api_key):
        self._tournament_manager.save_api_key(api_key)
        
    def get_tournaments(self):
        return self._tournament_manager.get_tournaments()
    
    def change_tournament_tier(self, tournament_name, new_tier):
        return self._tournament_manager.change_tournament_tier(tournament_name, new_tier)
    
    def add_tournament(self, tournament_link, tournament_tier):
        return self._tournament_manager.add_tournament(tournament_link, tournament_tier)
    
    def remove_tournament(self, tournament_name):
        return self._tournament_manager.remove_tournament(tournament_name)
    
    # ------------ Player Manager Wrappers ------------ # 
    def get_players(self):
        return self._player_manager.get_players()
    
    def get_rankings(self):
        return self._player_manager.get_rankings()
    
    def add_player(self, player_name, ranking_data):
        self._player_manager.add_player(player_name, ranking_data)
    
    def remove_player(self, player_name):
        self._player_manager.remove_player(player_name)
    
    def edit_player(self, player_name, new_ranking_data):
        self._player_manager.edit_player(player_name, new_ranking_data)
        
    def add_ranking(self, ranking_name, ranking_multiplier):
        self._player_manager.add_ranking(ranking_name, ranking_multiplier)
    
    def remove_ranking(self, ranking_name):
        self._player_manager.remove_ranking(ranking_name)
    
    def edit_ranking(self, ranking_name, new_multiplier):
        self._player_manager.edit_ranking(ranking_name, new_multiplier)
        
    # ------------ Rules Manager Wrappers ------------ #
    def get_rules(self):
        return self._rules_manager.get_rules() 
    
    
    # ----------- Get Managers ------------ #
    def get_tournament_manager(self):
        return self._tournament_manager
    
    def get_player_manager(self):
        return self._player_manager
    
    def get_rules_manager(self):
        return self._rules_manager