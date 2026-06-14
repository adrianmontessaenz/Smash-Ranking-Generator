# Import libraries
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import json
import sys
import pandas as pd
import os

from data_manager import add_tournament, add_head2head, add_player_info
from ranking_manager import compute_ranking
from decorate import decorate_excel

# Function to fetch tournament data and store it in a JSON file
def fetch_tournament(slug, eventSlug):
    # Set up the GraphQL client
    transport = RequestsHTTPTransport(
        url="https://api.start.gg/gql/alpha",
        headers={"Authorization": "Bearer 78294e27f422de785e5a19ab20cd309b"},  # Replace with your actual API token
        use_json=True,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Query to get the entrants from event
    query = gql("""
    query getEventData($slug: String, $eventSlug: String) {
      tournament(slug: $slug) {
        events(filter:{slug:$eventSlug})
        {
          id
        	entrants(query:{})
        	{
          	pageInfo {
            	total
          	}
        	}
        }
      }
    }
    """)

    # Get entrants to retrieve all placements
    entrants_data = client.execute(query, variable_values={"slug": slug, "eventSlug": eventSlug})
    total_entrants = entrants_data['tournament']['events'][0]['entrants']['pageInfo']['total']
    
    # Query to get event standings
    standings_query = gql("""
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
                  slots{
                    entrant{
                      participants{
                        gamerTag
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
    
    # Get placements and join jsons
    tmp_counter = 0
    tmp_page_counter = 1
    final_json = []
    while tmp_counter < total_entrants:
      json_data = client.execute(standings_query, variable_values={"slug": slug, "perPage": 10, "page": tmp_page_counter, "eventSlug": eventSlug})
      if not final_json:
        final_json = json_data
      else:
        final_json['tournament']['events'][0]['entrants']['nodes'] += json_data['tournament']['events'][0]['entrants']['nodes']
      tmp_counter += 10
      tmp_page_counter += 1
    return final_json

if __name__ == "__main__":
    # Check which argument was given (compute, decorate or tournament)
    if len(sys.argv) == 2:
      if sys.argv[1] == 'compute':
        compute_ranking()
        sys.exit(0)
      elif sys.argv[1] == 'decorate':
        decorate_excel('ranking_data.xlsx')
        sys.exit(0)
      else:
        print("Usage: python app.py <tournament_slug> <event_slug> <tournament_tier> or python app.py compute / decorate")
        sys.exit(1)
        
    # Check if a slug was provided as a command-line argument
    elif len(sys.argv) != 4:
        print("Usage: python app.py <tournament_slug> <event_slug> <tournament_tier> or python app.py compute / decorate")
        sys.exit(1)

    # Get tournament and event slug and retrieve needed data 
    tournament_slug = sys.argv[1]
    event_slug = sys.argv[2]
    final_data = fetch_tournament(tournament_slug, event_slug)
    
    # Prepare json to store tournament data
    json_data = {"tournaments": []}
    if os.path.exists('tournament_data.json'):
      with open('tournament_data.json', 'r') as file:
        json_data = json.load(file)

    # Create tournament data for json
    tmp_data = {
    "name": final_data['tournament']['name'],
    "entrants": final_data['tournament']['events'][0]['entrants']['pageInfo']['total'],
    "tier": sys.argv[3]
    }
    
    # If it was already created then end, as we already retrieved that data. If changed, restart excel
    if any(tournament['name'] == tmp_data['name'] for tournament in json_data['tournaments']):
      print('Tournament already fetched')
      sys.exit(0)
    json_data['tournaments'].append(tmp_data)
    
    # Create DataFrames to store data
    tournament_df_old = None
    head2head_df_old = None
    player_info_df_old = None
    
    # If excel already created, add new tournament to data
    if os.path.exists('ranking_data.xlsx'):
      tournament_df_old = pd.read_excel('ranking_data.xlsx', sheet_name='Placements')
      head2head_df_old = pd.read_excel('ranking_data.xlsx', sheet_name='Head2Head', index_col=0)
      player_info_df_old = pd.read_excel('ranking_data.xlsx', sheet_name='PlayerInfo')
            
    # Create placement and head-head dataframes with new data
    player_info_df = add_player_info(final_data, player_info_df_old)
    tournament_df = add_tournament(final_data, player_info_df, tournament_df_old)
    head2head_df = add_head2head(final_data, player_info_df, head2head_df_old)
    
    # Write the DataFrames to different sheets in an Excel file
    with pd.ExcelWriter('ranking_data.xlsx', engine='openpyxl', mode='w') as writer:
      player_info_df.to_excel(writer, sheet_name='PlayerInfo', index=False)
      tournament_df.to_excel(writer, sheet_name='Placements', index=False)
      head2head_df.to_excel(writer, sheet_name='Head2Head', index=True)
    print("Tournament data has been stored in ranking_data.xlsx")
    
    # Save data to a JSON file
    with open('tournament_data.json', 'w') as json_file:
        json.dump(json_data, json_file, indent=4)
    print("Tournament data has been fetched and stored in tournament_data.json")



