# Import libraries
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import json
import sys
import pandas as pd
import os
from openpyxl import load_workbook

# Function to fetch tournament data and store it in a JSON file
def fetch_tournament(slug, eventSlug):
    # Set up the GraphQL client
    transport = RequestsHTTPTransport(
        url="https://api.start.gg/gql/alpha",
        headers={"Authorization": "Bearer dc6a93f91afd04e48bb932193e03882e"},  # Replace with your actual API token
        use_json=True,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Query with entrants
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
    

    # Query to get standings
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
              participants{
                gamerTag
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
    # Check if a slug was provided as a command-line argument
    if len(sys.argv) != 3:
        print("Usage: python app.py <tournament_slug> <event_slug>")
        sys.exit(1)

    # Get tournament slug and retrieve needed data 
    tournament_slug = sys.argv[1]
    event_slug = sys.argv[2]
    final_data = fetch_tournament(tournament_slug, event_slug)
    
    # Save data to a JSON file
    with open('tournament_data.json', 'w') as json_file:
        json.dump(final_data, json_file, indent=4)

    print("Tournament data has been fetched and stored in tournament_data.json")

    # Set up dataframes for tournament and head2head data
    tournament_df = None
    head2head_df = None
    
    # If excel already created, add new tournament to data
    if os.path.exists('ranking_data.xlsx'):
      tournament_df = pd.read_excel('ranking_data.xlsx', sheet_name='Placements')
      column_index = 1
      # Check that we are not repeating a tournament data
      while column_index < tournament_df.shape[1]:
        column_data = tournament_df.iloc[:, column_index]
        if column_data.name == final_data['tournament']['name']:
          print("Tournament data already in excel")
          sys.exit()
        else:
          column_index += 1    

      # Get required data separately and create new column for tournament
      players_column = tournament_df['Players']
      tournament_name = final_data['tournament']['name']
      entrants = final_data['tournament']['events'][0]['entrants']['nodes']
      tournament_df[tournament_name] = None
      
      # Set placements for new players and players that already participated in previous tournaments
      for entrant in entrants:
        player_name = entrant['participants'][0]['gamerTag']            
        player_idx = 0
        # Append new player to the 'Players' column if it doesn't exist
        if player_name not in players_column.values:
          new_row = {'Players': player_name, tournament_name: entrant['standing']['placement']}
          tournament_df.loc[len(tournament_df)] = new_row
        else:
          player_idx = players_column[players_column == player_name].index[0]
          tournament_df.iloc[player_idx, column_index] = entrant['standing']['placement']    
      
    # If first time writing on excel
    else:
      # Write excel sheet for placements
      tournament_name = final_data['tournament']['name']
      entrants = final_data['tournament']['events'][0]['entrants']['nodes']
      playerNames = [entrant['participants'][0]['gamerTag'] for entrant in entrants]
      placements = [entrant['standing']['placement'] for entrant in entrants]
      index = ['Players', tournament_name]
      
      # Create a dictionary for DataFrame
      tournament_df = pd.DataFrame({'Players': playerNames, tournament_name: placements})
      
      #Write excel sheet for head to heads
      head2head_df = pd.DataFrame(index=playerNames, columns=playerNames)
      head2head_df = head2head_df.fillna(0)
      
      # Fill diagonal with '-'
      for player in playerNames:
        head2head_df.loc[player, player] = '-'
        
      # Check matches now
      for entrant in entrants:
        gamerId = entrant['id']
        gamerTag = entrant['participants'][0]['gamerTag']
        for set in entrant['paginatedSets']['nodes']:
          
          # If player won set, mark head to head as win
          if set['winnerId'] == gamerId:
            player1name = set['slots'][0]['entrant']['participants'][0]['gamerTag']
            player2name = set['slots'][1]['entrant']['participants'][0]['gamerTag']
            rivalName = player1name if player1name != gamerTag else player2name
            
            # Get player row and rival column and add
            head2head_df.loc[gamerTag, rivalName] += 1
            
    # Write the DataFrames to different sheets in an Excel file
    with pd.ExcelWriter('ranking_data.xlsx') as writer:
      tournament_df.to_excel(writer, sheet_name='Placements', index=False)
      head2head_df.to_excel(writer, sheet_name='Head-Head', index=False)
    
    # Decorate excel: Set width of columns to see tournament name correctly
    workbook = load_workbook('ranking_data.xlsx')
    sheet = workbook.active
    column_names = [cell.value for cell in sheet[1]]
    
    for tmp in range(sheet.max_column):
      letter = sheet.cell(row=1, column=tmp + 1).column_letter
      sheet.column_dimensions[letter].width = len(column_names[tmp]) + 2
      
    # Save the changes
    workbook.save('ranking_data.xlsx')
    workbook.close()
    
    print("Tournament data has been stored in ranking_data.xlsx")



