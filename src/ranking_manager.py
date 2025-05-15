import pandas as pd
import json
import os
import sys

def get_player_points(json_data, playerName):
    scores = [0,0,0]
    index = 0
    
    # Iterate through all ranking categories in the JSON and store player rankings in a separate list
    for ranking_type, rankings in json_data.items():
        for rank_range, rank_info in rankings.items():
            for player in rank_info['players']:
                if player['name'] == playerName:
                    scores[index] = rank_info['point_multiplier']
                    break
            if(scores[index] > 0):
                break
        index += 1
    return scores    

def compute_tournament_scores(tournament_df, json_tournament_data, tournament_points):
    # Create point dataframe
    playerNames = tournament_df.index.tolist()
    points_df = pd.DataFrame(index=playerNames, columns=tournament_df.columns)
    points_df.index.name = 'Players'

    # Depending on placement, give each player specific amount of points
    points_df['Total Score'] = None
    points_df['Total Tournaments'] = None
    for player in playerNames:
        final_score = 0
        total_tournaments = 0
        
        # Check for every tournament
        for column_idx in range(len(tournament_df.columns)):
            json_idx = len(tournament_df.columns) - (column_idx+1)
            placement = tournament_df.loc[player, tournament_df.columns[column_idx]]
            entrants = json_tournament_data['tournaments'][json_idx]['entrants']
            points = 0
            
            # Set points depending on position and tier 
            if placement is None or placement == 0:
                continue
            if json_tournament_data['tournaments'][json_idx]['tier'] == 'C':
                if placement < 3:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants * 1.5
                if placement < 8:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants
                else:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants * 0.5
            if json_tournament_data['tournaments'][json_idx]['tier'] == 'B':
                if placement < 3:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants * 2
                if placement < 8:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants * 1.5
                elif placement < 16:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants
                else:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants * 0.5
            elif json_tournament_data['tournaments'][json_idx]['tier'] == 'A':
                if placement < 3:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants * 4
                if placement < 8:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants * 2
                elif placement < 16:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants * 1.5
                elif placement < 32:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants
                else:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants * 0.5
                
            # Add to list of player scores
            points_df.loc[player, tournament_df.columns[column_idx]] = points
            final_score += points
            total_tournaments += 1
        
        # Set scores on table
        points_df.loc[player, 'Total Score'] = final_score
        points_df.loc[player, 'Total Tournaments'] = total_tournaments
    
    return points_df
    
def compute_h2h_scores(points_df, head2head_df, json_player_data, player_ranking_scores):
    # Create dataframe
    playerNames = points_df.index.tolist()
    
    # Create new head-2-head dataframe and fill diagonal with '-'
    h2h_points_df = pd.DataFrame(index=playerNames, columns=playerNames)
    h2h_points_df = h2h_points_df.infer_objects(copy=False).fillna(int(0))
    h2h_points_df = h2h_points_df.astype('object')
    for player in playerNames:
        h2h_points_df.loc[player, player] = '-'
      
    # Loop for each player's wins
    for i in range(len(playerNames)):
        player1 = playerNames[i]
        for player2 in playerNames[i + 1:]:
            # Skip own score (obvious)
            if player1 == player2:
                continue
            
            # If no h2h score between players, continue
            if head2head_df.loc[player1, player2] == 0 and head2head_df.loc[player2, player1] == 0:
                continue
            
            # If h2h already exists, continue
            if h2h_points_df.loc[player1, player2] != 0 or h2h_points_df.loc[player2, player1] != 0:
                continue
            
            # If h2h score, get total tournament score of the players
            p1_tournament_score = points_df.loc[player1, 'Total Score']
            p2_tournament_score = points_df.loc[player2, 'Total Score']
            
            # Check if players are ranked and set multiplier based on that
            player1_multiply = 0
            player2_multiply = 0
            if player1 in player_ranking_scores:
                for score in player_ranking_scores[player1]:
                    player1_multiply += score
            if player2 in player_ranking_scores:
                for score in player_ranking_scores[player2]:
                    player2_multiply += score        
            
            # Compute final score
            player1_score = p1_tournament_score * max(player1_multiply, 1) * 0.025
            player2_score = p2_tournament_score * max(player2_multiply, 1) * 0.025
            
            # Set scores on table
            h2h_points_df.loc[player1, player2] = player2_score * head2head_df.loc[player1, player2]
            h2h_points_df.loc[player2, player1] = player1_score * head2head_df.loc[player2, player1]            
                
    return h2h_points_df
         
def compute_ranking():
    # Check if all the materials needed for computing the ranking exist
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
    head2head_df = pd.read_excel('ranking_data.xlsx', sheet_name='Head2Head', index_col=0)
    
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
        
    # Compute each tournament value
    tournament_points = []
    for column_idx in range(len(tournament_df.columns)):
        # Get index of tournament in json
        json_idx = len(tournament_df.columns) - (column_idx+1)
                    
        # Set score based on entrants and player points
        entrant_score = 5*json_tournament_data['tournaments'][json_idx]['entrants']
        for player in playerNames:
            if tournament_df.loc[player, tournament_df.columns[column_idx]] <= 0:
                continue
            if playerRankingScores[player][0] > 0:
                entrant_score += 5*playerRankingScores[player][0]
            elif playerRankingScores[player][2] > 0:
                entrant_score += 5*playerRankingScores[player][2]
                
        # Set multiplier of tier of tournament and append final score to list
        tournament_tier = 1.25
        if json_tournament_data['tournaments'][json_idx]['tier'] == 'B':
            tournament_tier = 2.5
        elif json_tournament_data['tournaments'][json_idx]['tier'] == 'A':
            tournament_tier = 3.75
        tournament_points.append(entrant_score * tournament_tier * 0.01)
    
    # Get all player's tournament points and sort excel by total score
    points_df = compute_tournament_scores(tournament_df, json_tournament_data, tournament_points)
    points_df = points_df.sort_values(by=['Total Score', 'Total Tournaments'], ascending=[False, False])
    print('Tournament points have been computed for each player')
    
    # Get all h2h scores
    h2h_points_df = compute_h2h_scores(points_df, head2head_df, json_player_data, playerRankingScores)
    print('Head to head points have been computed for each player')
    
    if 'Natalia' not in h2h_points_df.index:
        raise ValueError("Player 'Natalia' not found in points_df")
    
    # Get final list of players (Only players that played X amount of tournaments)
    final_player_list = []
    for player in playerNames:
        if points_df.loc[player, 'Total Tournaments'] >= 1:
            final_player_list.append(player)
    
    # Create final dataframe
    final_score_df = pd.DataFrame(index=final_player_list)
    final_score_df.index.name = 'Players'
    final_score_df['Final Score'] = None
    
    # Add tournament score to h2h score
    for player in final_player_list:
        final_score = points_df.loc[player, 'Total Score']
        h2h_score = 0
        
        # Get positive h2h scores of player
        for column_idx in range(len(h2h_points_df.columns)):
            if h2h_points_df.loc[player, h2h_points_df.columns[column_idx]] != 0 and h2h_points_df.loc[player, h2h_points_df.columns[column_idx]] != '-':
                h2h_score += h2h_points_df.loc[player, h2h_points_df.columns[column_idx]]
                
        # Multiply by 0.1 and add to final score
        final_score += h2h_score * 0.1
        final_score_df.loc[player, 'Final Score'] = final_score 
    final_score_df = final_score_df.sort_values(by='Final Score', ascending=False)
    
    # Write the DataFrames back to the excel
    points_df = points_df.reset_index()
    with pd.ExcelWriter('ranking_data.xlsx', engine='openpyxl', mode='a') as writer:
        # Check if the sheet already exists and delete it if it does
        if 'Tournament Scores' in writer.book.sheetnames:
            del writer.book['Tournament Scores']
            del writer.book['Head2Head Scores']
            del writer.book['Final Ranking']

        # Write the DataFrames to different sheets in the Excel file
        points_df.to_excel(writer, sheet_name='Tournament Scores', index=False)
        h2h_points_df.to_excel(writer, sheet_name='Head2Head Scores', index=True)
        final_score_df.to_excel(writer, sheet_name='Final Ranking', index=True)  