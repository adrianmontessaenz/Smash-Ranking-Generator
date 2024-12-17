import pandas as pd
import json
import os
import sys

def get_player_points(json_data, playerName):
    scores = [0,0,0]
    index = 0
    
    # Iterate through all ranking categories in the JSON
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
    # Create dataframe
    playerNames = tournament_df.index.tolist()
    points_df = pd.DataFrame(index=playerNames, columns=tournament_df.columns)
    points_df.index.name = 'Players'
    
    # Depending on position, give each player specific amount of points
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
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants
                if placement < 8:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants * 0.75
                else:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants * 0.5
            if json_tournament_data['tournaments'][json_idx]['tier'] == 'B':
                if placement < 3:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants * 1.25
                if placement < 8:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants
                elif placement < 16:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants * 0.75
                else:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants * 0.5
            elif json_tournament_data['tournaments'][json_idx]['tier'] == 'A':
                if placement < 3:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants * 1.5
                if placement < 8:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants * 1.25
                elif placement < 16:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants
                elif placement < 32:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants * 0.75
                else:
                    points = tournament_points[column_idx] * (1 + entrants - min(entrants, placement))/entrants * 0.5
                
            # Add to list of scores
            points_df.loc[player, tournament_df.columns[column_idx]] = points
            final_score += points
            total_tournaments += 1
        points_df.loc[player, 'Total Score'] = final_score
        points_df.loc[player, 'Total Tournaments'] = total_tournaments
    return points_df
    
def compute_h2h_scores(tournament_df, points_df, head2head_df, json_player_data):
    # Create dataframe
    playerNames = tournament_df.index.tolist()
    
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
            
            # If no h2h score or h2h already set, continue
            if head2head_df.loc[player1, player2] == 0 and h2h_points_df.loc[player1, player2] != 0:
                continue
            
            # If h2h score, get each player's scores where both have participated
            # First check how many tournaments have they participated on
            player1_tc = 0
            player2_tc = 0
            for column_idx in range(len(tournament_df.columns)):
                if tournament_df.loc[player1, tournament_df.columns[column_idx]] != 0: 
                    player1_tc += 1
                if tournament_df.loc[player2, tournament_df.columns[column_idx]] != 0:
                    player2_tc += 1
            
            # Now get tournament scores. For the one with less or equal amount of tournaments, get all his tournaments.
            player1_score = 0
            player2_score = 0
            player1_tc_2 = 0
            player2_tc_2 = 0
            for column_idx in range(len(tournament_df.columns)):
                if tournament_df.loc[player1, tournament_df.columns[column_idx]] != 0 and tournament_df.loc[player2, tournament_df.columns[column_idx]] != 0:
                    player1_score += points_df.loc[player1, tournament_df.columns[column_idx]]
                    player2_score += points_df.loc[player2, tournament_df.columns[column_idx]]
                    player2_tc_2 += 1
                    player1_tc_2 += 1
                elif player2_tc <= player1_tc and tournament_df.loc[player2, tournament_df.columns[column_idx]] != 0:
                    player2_score += points_df.loc[player2, tournament_df.columns[column_idx]]
                    player2_tc_2 += 1
                elif player2_tc >= player1_tc and tournament_df.loc[player1, tournament_df.columns[column_idx]] != 0:
                    player1_score += points_df.loc[player1, tournament_df.columns[column_idx]]
                    player1_tc_2 += 1
            
            
            # Now, for the one with more tournaments (If they don't have the same exact tournaments), get the ones with high scores that haven't been counted
            if player2_tc_2 != player1_tc_2:
                tournaments_for_other_player = {}
                for column_idx in range(len(tournament_df.columns)):
                    if player2_tc < player1_tc and tournament_df.loc[player1, tournament_df.columns[column_idx]] != 0:
                        tournaments_for_other_player[tournament_df.columns[column_idx]] = points_df.loc[player1, tournament_df.columns[column_idx]]
                    elif player2_tc >= player1_tc and tournament_df.loc[player2, tournament_df.columns[column_idx]] != 0:
                        tournaments_for_other_player[tournament_df.columns[column_idx]] = points_df.loc[player2, tournament_df.columns[column_idx]]

                # Sort from highest to smallest
                tournaments_for_other_player = dict(sorted(tournaments_for_other_player.items(), key=lambda item: item[1], reverse=True))
                for tournaments in tournaments_for_other_player.keys():
                    if player1_tc_2 == player2_tc_2:
                        break
                    elif player2_tc < player1_tc and tournament_df.loc[player2,tournaments] == 0:
                        player1_score += tournaments_for_other_player[tournaments]
                        player1_tc_2 += 1
                    elif player1_tc < player2_tc and tournament_df.loc[player1,tournaments] == 0:
                        player2_score += tournaments_for_other_player[tournaments]
                        player2_tc_2 += 1
            
            # Now with the final tournament scores to decide the head to head, multiply by their ranking position
            player1_multiply = 0
            player2_multiply = 0
            
            for ranking_key, ranking in json_player_data.items():
                for sub_key, ranking_value in ranking.items():
                    players = ranking_value.get("players",[])
                    multiplier = ranking_value["point_multiplier"]
                    for player in players:
                        if player1 == player['name']:
                            player1_multiply += multiplier
                        elif player2 == player['name']:
                            player2_multiply += multiplier
            
            # Add extra score if they are ranked
            player1_score += 0 if player1_multiply == 0 else player1_score * player1_multiply * 0.025
            player2_score += 0 if player2_multiply == 0 else player2_score * player2_multiply * 0.025
            
            # Compute difference and set it on final score
            if head2head_df.loc[player1, player2] > 0:
                h2h_points_df.loc[player1, player2] = player2_score * head2head_df.loc[player1, player2]
                h2h_points_df.loc[player2, player1] = player2_score * head2head_df.loc[player2, player1]
            else:
                h2h_points_df.loc[player1, player2] = player1_score * head2head_df.loc[player1, player2]
                h2h_points_df.loc[player2, player1] = player1_score * head2head_df.loc[player2, player1]
    
    return h2h_points_df
         
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
    
    points_df = compute_tournament_scores(tournament_df, json_tournament_data, tournament_points)
    points_df = points_df.sort_values(by=['Total Score', 'Total Tournaments'], ascending=[False, False])
    print('Tournament points have been computed for each player')
    
    h2h_points_df = compute_h2h_scores(tournament_df, points_df, head2head_df, json_player_data)
    print('Head to head points have been computed for each player')
    
    # Get final list of players (Only players that played X amount of tournaments)
    final_player_list = []
    for player in playerNames:
        if points_df.loc[player, 'Total Tournaments'] >= 4:
            final_player_list.append(player)
    
    # Create final dataframe
    final_score_df = pd.DataFrame(index=final_player_list)
    final_score_df.index.name = 'Players'
    final_score_df['Final Score'] = None
    
    # Add tournament score to h2h score
    for player in final_player_list:
        final_score = points_df.loc[player, 'Total Score']
        h2h_score = 0
        for column_idx in range(len(h2h_points_df.columns)):
            if h2h_points_df.loc[player, h2h_points_df.columns[column_idx]] != 0 and h2h_points_df.loc[player, h2h_points_df.columns[column_idx]] != '-':
                name = h2h_points_df.columns[column_idx]
                tmp = h2h_points_df.loc[player, h2h_points_df.columns[column_idx]]
                h2h_score += h2h_points_df.loc[player, h2h_points_df.columns[column_idx]]
        final_score += h2h_score * 0.1
        final_score_df.loc[player, 'Final Score'] = final_score 
        
    final_score_df = final_score_df.sort_values(by='Final Score', ascending=False)
    
    # Write the DataFrames back to the excel
    points_df = points_df.reset_index()
    with pd.ExcelWriter('ranking_data.xlsx', engine='openpyxl', mode='a') as writer:
      points_df.to_excel(writer, sheet_name='Tournament Score', index=False)
      h2h_points_df.to_excel(writer, sheet_name='H2H Score', index=True)
      final_score_df.to_excel(writer, sheet_name='Final Ranking', index=True)
            
            
            
                
                
            
            
            
            
            
                
    
        
    
            
            