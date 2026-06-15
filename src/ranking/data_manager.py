"""Ranking data management facade.

This module exposes `DataManager`, a thin facade that composes the
lower-level managers for tournaments, players and rules. The class
provides convenience wrapper methods used by the GUI and CLI entry
points so callers do not need to interact with manager classes
directly.

The concrete managers live in `ranking.managers` and handle
persistence and domain logic; `DataManager` merely forwards calls.
"""

from pathlib import Path
import json
import os
from ranking.managers.tournament_manager import _TournamentManager
from ranking.managers.player_manager import PlayerManager
from ranking.managers.rules_manager import RulesManager

class DataManager:
    """Facade composing tournament, player and rules managers.

    The `DataManager` initializes the underlying managers and exposes
    a simplified API for the rest of the application (GUI/CLI).
    """
    def __init__(self):
        """Create manager instances and ensure the data directory exists.

        Side effects:
            - Creates a `data/` directory when missing.
        """
        # Make sure data directory exists. If not, create it.
        if not os.path.exists("data"):
            os.makedirs("data")
        
        # Load managers
        self._tournament_manager = _TournamentManager()
        self._player_manager = PlayerManager()
        self._rules_manager = RulesManager()
    
    # ------------ Tournament Manager Wrappers ------------ #
    def get_api_key(self):
        """Return the stored StartGG API key as a string.

        Returns an empty string when no key is set.
        """
        return self._tournament_manager.get_api_key()
        
    def save_api_key(self, api_key):
        """Persist the provided StartGG API key.

        Args:
            api_key (str): API key to save.
        """
        self._tournament_manager.save_api_key(api_key)
        
    def get_tournaments(self):
        """Return a list/dictionary of known tournaments.

        The exact structure is defined by the tournament manager.
        """
        return self._tournament_manager.get_tournaments()
    
    def get_tournament_tiers(self):
        """Return available tournament tiers (e.g. S, A, B...)."""
        return self._tournament_manager.get_tournament_tiers()
    
    def change_tournament_tier(self, tournament_name, new_tier):
        """Change the tier assigned to a tournament.

        Args:
            tournament_name: Identifier or name of the tournament.
            new_tier: New tier value.
        """
        return self._tournament_manager.change_tournament_tier(tournament_name, new_tier)
    
    def add_tournament(self, tournament_link, tournament_tier):
        """Add a tournament by link and assign a tier.

        Args:
            tournament_link (str): URL or identifier for the tournament.
            tournament_tier: Tier to assign to the tournament.
        """
        return self._tournament_manager.add_tournament(tournament_link, tournament_tier)
    
    def remove_tournament(self, tournament_name):
        """Remove a tournament by name/identifier."""
        return self._tournament_manager.remove_tournament(tournament_name)
    
    # ------------ Player Manager Wrappers ------------ # 
    def get_players(self):
        """Return player records managed by the player manager."""
        return self._player_manager.get_players()
    
    def get_rankings(self):
        """Return configured ranking types and multipliers."""
        return self._player_manager.get_rankings()
    
    def add_player(self, player_name, ranking_data):
        """Add a new player with initial ranking data.

        Args:
            player_name: Name/identifier for the player.
            ranking_data: Mapping of ranking name to value.
        """
        self._player_manager.add_player(player_name, ranking_data)
    
    def remove_player(self, player_name):
        """Remove a player by name/identifier."""
        self._player_manager.remove_player(player_name)
    
    def edit_player(self, player_name, new_ranking_data):
        """Update a player's ranking data.

        Args:
            player_name: Player identifier.
            new_ranking_data: New mapping of rankings to values.
        """
        self._player_manager.edit_player(player_name, new_ranking_data)
        
    def add_ranking(self, ranking_name, ranking_multiplier):
        """Create a new ranking column with a multiplier."""
        self._player_manager.add_ranking(ranking_name, ranking_multiplier)
    
    def remove_ranking(self, ranking_name):
        """Remove an existing ranking column."""
        self._player_manager.remove_ranking(ranking_name)
    
    def edit_ranking(self, ranking_name, new_multiplier):
        """Update the multiplier for a ranking column."""
        self._player_manager.edit_ranking(ranking_name, new_multiplier)
        
    # ------------ Rules Manager Wrappers ------------ #
    def get_rules(self):
        """Return the currently configured rules object/data."""
        return self._rules_manager.get_rules() 
    
    
    # ----------- Get Managers ------------ #
    def get_tournament_manager(self):
        """Return the underlying tournament manager instance."""
        return self._tournament_manager
    
    def get_player_manager(self):
        """Return the underlying player manager instance."""
        return self._player_manager
    
    def get_rules_manager(self):
        """Return the underlying rules manager instance."""
        return self._rules_manager