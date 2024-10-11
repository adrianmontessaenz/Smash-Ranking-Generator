import pandas as pd
import json
import os
import sys

def add_tournament(json_data, tournament_df = None):
    # Write excel sheet for placements
    tournament_name = json_data['tournament']['name']
    entrants = json_data['tournament']['events'][0]['entrants']['nodes']
    playerNames = [entrant['participants'][0]['gamerTag'] for entrant in entrants]
    placements = [int(entrant['standing']['placement']) for entrant in entrants]
    
    # Create a dictionary for DataFrame
    df = pd.DataFrame({'Players': playerNames, tournament_name: placements})    
    if tournament_df is not None:
        df = pd.concat([df.set_index('Players'), tournament_df.set_index('Players')], axis=1)
        df = df.infer_objects(copy=False).fillna(int(0))
        df = df.reset_index()
        print(df)
    return df
          
def add_head2head(json_data, head2head_df = None):
    # Get needed variables and create dataframe
    entrants = json_data['tournament']['events'][0]['entrants']['nodes']
    df = None
    
    # If not file, create h2h table from 0
    if head2head_df is None:
        playerNames = [entrant['participants'][0]['gamerTag'] for entrant in entrants]
        df = pd.DataFrame(index=playerNames, columns=playerNames)

        # Fill diagonal with '-'
        df = df.infer_objects(copy=False).fillna(int(0))
        df = df.astype('object')
        for player in playerNames:
          df.loc[player, player] = '-'
    
    # If file, add new players to table
    else:
        df = head2head_df
        df = df.astype('object')
        players_column = df.index
        players_column = [s.lower() for s in players_column]
           
        # Check for new names first
        for entrant in entrants:
          gamerTag = entrant['participants'][0]['gamerTag']
          # If new player, add to table
          if gamerTag.strip().lower() not in players_column:
            df[gamerTag] = None
            df.loc[gamerTag] = [None] * len(df.columns)
            df.loc[gamerTag, gamerTag] = '-'
        df = df.infer_objects(copy=False).fillna(0)
        
    # Check matches
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
          df.loc[gamerTag, rivalName] += 1
    return df


def get_player_points(json_data, playerName):
    scores = [0,0,0]
    index = 0
    
    # Iterate through all ranking categories in the JSON
    for ranking_type, rankings in json_data.items():
        for rank_range, rank_info in rankings.items():
            for player in rank_info['players']:
                if player['name'].lower() == playerName.lower():
                    scores[index] = rank_info['point_multiplier']
                    break
            if(scores[index] > 0):
                break
        index += 1
    return scores
                 
def compute_ranking():
    # Check if excel exists
    if os.path.exists('ranking_data.xlsx') is False:
        print("First create excel with data, then compute ranking")
        sys.exit(1)
    elif os.path.exists('tournament_data.json') is False:
        print("Create json with tournament values")
        sys.exit(1)
    elif os.path.exists('player_data.json') is False:
        print("Create json with player data values")
        sys.exit(1)
        
    # Get data from tournaments
    tournament_df = pd.read_excel('ranking_data.xlsx', sheet_name='Placements', index_col=0)
    head2head_df = pd.read_excel('ranking_data.xlsx', sheet_name='Head-Head', index_col=0)
    
    # Open and read the JSON file
    json_tournament_data = None
    json_player_data = None
    with open('tournament_data.json', 'r') as file:
        json_tournament_data = json.load(file)
    with open('player_data.json', 'r') as file:
        json_player_data = json.load(file)
    
    # Get player ranking scores
    playerRankingScores = {}
    playerNames = tournament_df.index.tolist()
    for player in playerNames:
        playerRankingScores[player] = get_player_points(json_player_data, player)
        
    # Compute tournament value
    tournament_points = []
    points_df = pd.DataFrame(index=playerNames, columns=tournament_df.columns)
    points_df.index.name = 'Players'
    
    print(points_df)
    for column_idx in range(len(tournament_df.columns)):
        entrant_score = 5*json_tournament_data['tournaments'][column_idx]['entrants']
        for player in playerNames:
            if playerRankingScores[player][0] > 0 or playerRankingScores[player][2] > 0:
                entrant_score += 5*playerRankingScores[player][0]-5
        tournament_tier = 1.25
        if json_tournament_data['tournaments'][column_idx]['tier'] == 'B':
            tournament_tier = 2.5
        elif json_tournament_data['tournaments'][column_idx]['tier'] == 'A':
            tournament_tier = 5
        tournament_points.append(entrant_score * tournament_tier * 0.01)
        
    # Depending on position, give each player specific amount of points
    playerNames = tournament_df.index.tolist()
    points_df['Total Score'] = None
    print(points_df)
    for player in playerNames:
        final_score = 0
        for column_idx in range(len(tournament_df.columns)):
            placement = tournament_df.loc[player, tournament_df.columns[column_idx]]
            entrants = json_tournament_data['tournaments'][column_idx]['entrants']
            points = 0
            if placement is None or placement == 0:
                continue
            if json_tournament_data['tournaments'][column_idx]['tier'] == 'B':
                if placement < 8:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants
                elif placement < 16:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants * 0.75
                else:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants * 0.5
            elif json_tournament_data['tournaments'][column_idx]['tier'] == 'A':
                if placement < 8:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants * 1.25
                elif placement < 16:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants
                elif placement < 32:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants * 0.75
                else:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants * 0.5
                
            points_df.loc[player, tournament_df.columns[column_idx]] = points
            final_score += points
        points_df.loc[player, 'Total Score'] = final_score
        
    print(points_df)
    # Write the DataFrames back to the excel
    points_df = points_df.reset_index()
    with pd.ExcelWriter('ranking_data.xlsx', engine='openpyxl', mode='a') as writer:
      points_df.to_excel(writer, sheet_name='Tournament Score', index=False)
            
            