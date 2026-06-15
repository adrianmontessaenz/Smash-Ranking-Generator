"""Smash Ranking Generator — main entrypoint.

This module provides a small CLI test runner (`run_test`) used for
quick integration checks of the data management and ranking
computation, and the normal GUI startup when run without the
`--nogui` flag.

Usage:
    python -m src.main          # starts the GUI
    python -m src.main --nogui  # runs `run_test()` smoke tests
"""

import sys
import GUI.window as window
from ranking.data_manager import DataManager
from ranking.compute_ranking import compute_ranking

def run_test():
    """Run a quick integration smoke test of data and ranking logic.

    The function initializes a `DataManager`, verifies or sets a
    StartGG API key, ensures at least one tournament, player and
    ranking exist for demonstration, and invokes
    `compute_ranking(data_manager)` to validate ranking computation.

    Side effects:
        - May modify local data (add test tournament/player/ranking)
        - Prints status messages to stdout

    Returns:
        None
    """
    # Test the DataManager and its managers
    data_manager = DataManager()
    
    # Test StartGG API key management
    print("Current API Key:", data_manager.get_api_key())
    if data_manager.get_api_key() == "":
        print("No API key set. Please set an API key in the config.json file or through the GUI.")
        data_manager.save_api_key("your_api_key_here")  # Replace with a valid API key for testing
        exit("API key not set.")
    
    # Test TournamentManager
    print("Tournaments:", data_manager.get_tournaments())
    if len(data_manager.get_tournaments()) == 0:
        print("No tournaments found. Adding a test tournament for demonstration purposes.")
        data_manager.add_tournament("https://www.start.gg/tournament/e-monthly-3/event/ultimate-singles", "B")
       
    # Test PlayerManager
    print("Players:", data_manager.get_players())
    if len(data_manager.get_players()) == 0:
        print("No players found. Adding a test player for demonstration purposes.")
        data_manager.add_player("Molo", {"No Ranking": 1.0})
    
    print("Rankings:", data_manager.get_rankings())
    if len(data_manager.get_rankings()) == 0:
        print("No rankings found. Adding a test ranking for demonstration purposes.")
        data_manager.add_ranking("Test Ranking", 1.5)
        data_manager.edit_player("Molo", {"Test Ranking": 1.5})
    
    # Test RulesManager
    print("Computing ranking based on current data...")
    compute_ranking(data_manager)
    print("Ranking computation completed. Check the output files for results.")
    
if __name__ == "__main__":
    if "--nogui" in sys.argv:
        run_test()
    else:        
        # Initialize and run the application normally with GUI
        data_manager = DataManager()
        app = window.AppWindow(data_manager)
        app.run()
    
