"""Tournament manager: fetch, store and manage tournament metadata.

This module provides `_TournamentManager`, a small utility used by
the higher-level `DataManager` to persist tournament lists, tiers,
and a StartGG API key. It also contains logic to fetch tournament
details from the StartGG GraphQL endpoint.
"""

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from pathlib import Path
import json
import os


class _TournamentManager:
    """Manage tournaments, tiers and the StartGG API key.

    The class handles loading and saving `data/tournaments.json` and
    `data/config.json`, provides simple getters/setters and performs
    tournament fetching using the StartGG GraphQL API.
    """
    def __init__(self):
        """Initialize internal state and load persisted data.

        If `data/tournaments.json` does not exist it is created with a
        sensible default tiers mapping.
        """
        # Load tournament data (if any)
        if os.path.exists("data/tournaments.json"):
            with open("data/tournaments.json", "r") as tournaments_file:
                tournaments_data = json.load(tournaments_file)
                self._tournaments = tournaments_data.get("tournaments", [])
                self._tiers = tournaments_data.get("tiers", {"SS": 20.0, "S": 15.0, "A": 7.5, "B": 2.5, "C": 1.0, "D": 0.75})
        else:
            with open("data/tournaments.json", "w") as tournaments_file:
                json.dump({"tournaments": [], "tiers": {"SS": 20.0, "S": 15.0, "A": 7.5, "B": 2.5, "C": 1.0, "D": 0.75}}, tournaments_file)
                self._tournaments = []
                self._tiers = {"SS": 20.0, "S": 15.0, "A": 7.5, "B": 2.5, "C": 1.0, "D": 0.75}

        # Load API key from config file if it exists
        if os.path.exists("data/config.json"):
            with open("data/config.json", "r") as config_file:
                config_data = json.load(config_file)
                self._api_key = config_data.get("api_key", "")
        else:
            self._api_key = ""
    
    # ------------ Public Methods ------------ #
    # ------------ API Key Methods ------------ #
    def get_api_key(self):
        """Return the stored StartGG API key (or empty string)."""
        return self._api_key
      
    def save_api_key(self, api_key):
        """Persist the StartGG API key to `data/config.json`.

        Args:
            api_key (str): API key to save.
        """
        self._api_key = api_key
        config_data = {"api_key": api_key}
        config_path = Path("data/config.json")
        
        # Save the API key to the config file
        with config_path.open("w") as config_file:
            json.dump(config_data, config_file)
    
    # ------------ Tournament Methods ------------ #
    def get_tournaments(self):
        """Return the list of stored tournaments."""
        return self._tournaments

    def get_tournament_tiers(self):
        """Return the mapping of tournament tiers to multipliers."""
        return self._tiers
    
    def change_tournament_tier(self, tournament_name, new_tier):
        """Change the tier for a specific tournament and save changes.

        Args:
            tournament_name: Tournament name to find.
            new_tier: New tier value to assign.

        Returns:
            str: Human-readable status message.
        """
        for tournament in self._tournaments:
            if tournament['name'] == tournament_name:
                tournament['tier'] = new_tier
                break
        
        # Save updated tournaments data to file
        tournaments_path = Path("data/tournaments.json")
        with tournaments_path.open("w") as tournaments_file:
            tournaments_data = {
                "tournaments": self._tournaments,
                "tiers": self._tiers
            }
            json.dump(tournaments_data, tournaments_file, indent=4)

        return "Tournament tier updated successfully."
            
    def add_tournament(self, tournament_link, tournament_tier):
        """Fetch a tournament from StartGG and add it to storage.

        Args:
            tournament_link (str): URL to the tournament event on StartGG.
            tournament_tier: Tier to assign to the new tournament.

        Returns:
            str: Status message describing the outcome.
        """
        if not self._api_key:
            return "API key not set."
        
        # Logic to add tournament using the provided link
        slugs = tournament_link.split("/")[0:]
        if slugs[0] == "https:" or slugs[0] == "http":
            slugs = slugs[2:]
        print(slugs)
        tournament_slug = slugs[2]
        print(tournament_slug)
        event_slug = slugs[4]
        print(event_slug)
        
        # Gather tournament data using GraphQL API
        for t in self._tournaments:
            if t['debug_data']['tournament_slug'] == tournament_slug and t['debug_data']['event_slug'] == event_slug:
                print("Tournament already fetched.")
                return "Tournament already fetched."
        tournament_json = self._fetch_tournament_data(tournament_slug, event_slug)
        
        # Create clearer tournament data structure
        tournament_json_data = {
            "name": tournament_json['tournament']['name'],
            "entrants": tournament_json['tournament']['events'][0]['entrants']['pageInfo']['total'],
            "tier": tournament_tier,
            "link": tournament_link,
            "debug_data": {"tournament_slug": tournament_slug, "event_slug": event_slug},
            "player_data": []
        }
        
        # Extract player data
        for entrant in tournament_json['tournament']['events'][0]['entrants']['nodes']:
            player_info = {
                "gamerTag": entrant['participants'][0]['gamerTag'],
                "userId": entrant['participants'][0]['user']['id'],
                "placement": entrant['standing']['placement'],
                "matches": {"wins": [], "losses": []}
            }
            # Extract match data
            for match in entrant['paginatedSets']['nodes']:
                # Get opponent info
                other_player = {}
                for slot in match['slots']:
                    participantID = slot['entrant']['participants'][0]['user']['id']
                    if participantID != player_info['userId']:
                        other_player = {
                            "gamerTag": slot['entrant']['participants'][0]['gamerTag'],
                            "isDisqualified": True if match["displayScore"] == "DQ" else False,
                            "userId": slot['entrant']['participants'][0]['user']['id']
                        }
                        break
                      
                # Determine win/loss
                if match["winnerId"] == entrant["id"]:
                    player_info['matches']['wins'].append(other_player)
                else:
                    player_info['matches']['losses'].append(other_player)
            tournament_json_data["player_data"].append(player_info)
        
        # Add tournament data to the list
        self._tournaments.append(tournament_json_data)
        
        # Save updated tournaments data to file
        tournaments_path = Path("data/tournaments.json")
        with tournaments_path.open("w") as tournaments_file:
            tournaments_data = {
                "tournaments": self._tournaments,
                "tiers": self._tiers
            }
            json.dump(tournaments_data, tournaments_file, indent=4)

        print("Tournament added successfully.")
        return "Tournament added successfully."
        
    def remove_tournament(self, tournament_name):
        """Remove a tournament by name and persist the change."""
        # Logic to remove tournament by name
        self._tournaments = [t for t in self._tournaments if t['name'] != tournament_name]
        
        # Save updated tournaments data to file
        tournaments_path = Path("data/tournaments.json")
        with tournaments_path.open("w") as tournaments_file:
            tournaments_data = {
                "tournaments": self._tournaments,
                "tiers": self._tiers
            }
            json.dump(tournaments_data, tournaments_file, indent=4)

        return "Tournament removed successfully."
    
    # ------------ Private Methods ------------ #
    
    def _fetch_tournament_data(self, slug, eventSlug) -> dict:
        """Fetch tournament event data from the StartGG GraphQL API.

        The method pages through entrants until all are retrieved and
        returns the assembled JSON payload.

        Args:
            slug (str): Tournament slug.
            eventSlug (str): Event slug within the tournament.

        Returns:
            dict: JSON response from the API with all entrants.
        """
        # Function to fetch tournament data and store it in a JSON file
        # Set up the GraphQL client
        transport = RequestsHTTPTransport(
            url="https://api.start.gg/gql/alpha",
            headers={"Authorization": "Bearer " + self._api_key},  # Replace with your actual API token
            use_json=True,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        # Query to get event standings
        query = gql("""
        query getStandings($slug: String!, $perPage: Int!, $page: Int! $eventSlug: String!) {
          tournament(slug: $slug) {
            name
            events(filter: {slug: $eventSlug}) {
              entrants(query:{perPage: $perPage, page: $page})  {
                pageInfo {
                	total
              	}
                nodes{
                  id
                  isDisqualified
                  participants{
                    gamerTag
                    user{
                      id
                    }
                  }
                  standing {
                    placement
                  }
                  paginatedSets {
                    nodes
                    {
                      winnerId
                      displayScore
                      slots{
                        entrant{
                          participants{
                            gamerTag
                            user{
                              id
                            }
                          }
                        }
                      }                
                    }
                 	}
            		}
              }
            }
          }
        }
        """)

        # Get first page to retrieve number of entrants
        page_counter = 1
        json_data = client.execute(query, variable_values={"slug": slug, "perPage": 10, "page": page_counter, "eventSlug": eventSlug})
        tmp_counter = 10
        page_counter += 1
        total_entrants = json_data['tournament']['events'][0]['entrants']['pageInfo']['total']
        final_json = json_data
        
        # Loop until all entrants are fetched
        while tmp_counter < total_entrants:
            json_data = client.execute(query, variable_values={"slug": slug, "perPage": 10, "page": page_counter, "eventSlug": eventSlug})
            final_json['tournament']['events'][0]['entrants']['nodes'] += json_data['tournament']['events'][0]['entrants']['nodes']
            tmp_counter += 10
            page_counter += 1
        return final_json