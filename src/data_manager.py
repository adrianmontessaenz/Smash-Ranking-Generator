import pandas as pd
import json
import os
import sys

def add_player_info(json_data, player_df: pd.DataFrame | None = None) -> pd.DataFrame:
    # Get player data from tournament
    entrants = json_data['tournament']['events'][0]['entrants']['nodes']
    playerNames = [entrant['participants'][0]['gamerTag'] for entrant in entrants]
    playerIds = [
        entrant['participants'][0]['user']['id'] if entrant['participants'][0]['user'] is not None else -1
        for entrant in entrants
    ]
    
    # If file exists, add new players manually. Check if there are repeated ids with different names
    if player_df is None:
        player_df = pd.DataFrame({'IDs': playerIds, 'PlayerNames1': playerNames})
        
    else:
        for idx, player_id in enumerate(playerIds):
            if player_id == -1:
                # If player_id is -1, skip this player
                continue
            
            player_name = playerNames[idx]
            
            # If id is not in file, add it
            if player_id not in player_df['IDs'].values:
                player_df = pd.concat([player_df, pd.DataFrame({'IDs': [player_id], 'PlayerNames1': [player_name]})], ignore_index=True)

            # If ID is in file, check if name is the same
            elif player_id in player_df['IDs'].values:
                row_idx_in_df = player_df[player_df['IDs'] == player_id].index[0]
                it = 1
                add_name = True
                while True:          
                    cell_value = player_df.at[row_idx_in_df, f'PlayerNames{it}']
                    
                    # If name is already in the list, break
                    if cell_value == player_name:
                        add_name = False
                        break
                    
                    # If reached end of the list, break
                    elif pd.isna(cell_value):
                        break
                    
                    it += 1
                    # If it is the last column, break
                    if f'PlayerNames{it}' not in player_df.columns:
                        break
                
                # If name is not in the list, add it
                if add_name:
                    if f'PlayerNames{it}' not in player_df.columns:
                        player_df[f'PlayerNames{it}'] = None
                    player_df.at[row_idx_in_df, f'PlayerNames{it}'] = player_name
    
    return player_df
  
def add_tournament(json_data, player_info_df : pd.DataFrame, tournament_df: pd.DataFrame | None = None) -> pd.DataFrame:
    # Get player data from tournament
    tournament_name = json_data['tournament']['name']
    entrants = json_data['tournament']['events'][0]['entrants']['nodes']
    playerNames = [entrant['participants'][0]['gamerTag'] for entrant in entrants]
    playerIds = [
        entrant['participants'][0]['user']['id'] if entrant['participants'][0]['user'] is not None else -1
        for entrant in entrants
    ]
    placements = [int(entrant['standing']['placement']) for entrant in entrants]
    disqualified = [entrant['isDisqualified'] for entrant in entrants]
    
    # Set disqualified players to 0 in placements
    for idx, disq in enumerate(disqualified):
        if disq:
            placements[idx] = 0
    
    # If dataframe does not exist, create it
    if tournament_df is None:
        tournament_df = pd.DataFrame({'Players': playerNames, tournament_name: placements})
    
    # If dataframe exists, add new tournament data
    else:
        # Create new column with tournament name
        tournament_df[tournament_name] = None
        
        # Loop through players and add their placements
        for idx, player_name in enumerate(playerNames):
            player_id = playerIds[idx]
            placement = placements[idx]
            
            # If player is in the dataframe, add their placement
            if player_name in tournament_df['Players'].values:
                row_idx_in_df = tournament_df[tournament_df['Players'] == player_name].index[0]
                tournament_df.at[row_idx_in_df, tournament_name] = placement
                
            # If player is not in the dataframe, add them
            else:
                # Get player name from player_info_df
                changedName = False
                if player_id != -1:
                    player_id_row_idx = player_info_df[player_info_df['IDs'] == player_id].index[0]
                    it = 1
                    while True:
                        if player_id == -1:
                            # If player_id is -1, skip this player
                            break
                        cell_value = player_info_df.at[player_id_row_idx, f'PlayerNames{it}']

                        # If name is already in the list, break
                        if cell_value in tournament_df['Players'].values:
                            changedName = True
                            break
                        
                        # If reached end of the list, break
                        elif pd.isna(cell_value):
                            break
                        
                        it += 1
                        # If it is the last column, break
                        if f'PlayerNames{it}' not in player_info_df.columns:
                            break
                if changedName:
                    # Get the name from the dataframe
                    prev_player_name = player_info_df.at[player_id_row_idx, f'PlayerNames{it}']
                    row_idx_in_df = tournament_df[tournament_df['Players'] == prev_player_name].index[0]
                    tournament_df.at[row_idx_in_df, 'Players'] = player_name
                    tournament_df.at[row_idx_in_df, tournament_name] = placement
                else:
                    tournament_df = pd.concat([tournament_df, pd.DataFrame({'Players': [player_name], tournament_name: [placement]})], ignore_index=True)
                
    tournament_df = tournament_df.infer_objects(copy=False).fillna(int(0))
    return tournament_df
          
def add_head2head(json_data, player_info_df : pd.DataFrame, head2head_df: pd.DataFrame | None = None) -> pd.DataFrame:
    # Get needed variables and create dataframe
    entrants = json_data['tournament']['events'][0]['entrants']['nodes']
    playerNames = [entrant['participants'][0]['gamerTag'] for entrant in entrants]
    playerIds = [
        entrant['participants'][0]['user']['id'] if entrant['participants'][0]['user'] is not None else -1
        for entrant in entrants
    ]
    
    # If not file, create h2h table from 0
    if head2head_df is None:
        head2head_df = pd.DataFrame(index=playerNames, columns=playerNames)

        # Fill diagonal with '-'
        head2head_df = head2head_df.infer_objects(copy=False).fillna(int(0))
        head2head_df = head2head_df.astype('object')
        for player in playerNames:
          head2head_df.loc[player, player] = '-'
    
    # If file, add new players to table
    else:
        head2head_df = head2head_df.astype('object')
           
        # Check for new names first
        for idx, player_name in enumerate(playerNames):
            players_row = head2head_df.index
            players_column = head2head_df.columns
            player_id = playerIds[idx]
            
            if player_name not in players_row:
                # Get player name from player_info_df
                old_name = None
                if player_id != -1:
                    player_id_row_idx = player_info_df[player_info_df['IDs'] == player_id].index[0]
                    it = 1
                    while True:                    
                        cell_value = player_info_df.at[player_id_row_idx, f'PlayerNames{it}']

                        # If name is already in the list, break
                        if cell_value in players_row:
                            old_name = cell_value
                            break
                        
                        # If reached end of the list, break
                        elif pd.isna(cell_value):
                            break
                        
                        it += 1
                        # If it is the last column, break
                        if f'PlayerNames{it}' not in player_info_df.columns:
                            break
                if old_name is not None:
                    # Replace old_name with new player_name in the index
                    new_rows = players_row.to_list()
                    new_rows = [player_name if x == old_name else x for x in new_rows]
                    head2head_df.index = new_rows

                    # Replace old_name with new player_name in the columns
                    new_columns = players_column.to_list()
                    new_columns = [player_name if x == old_name else x for x in new_columns]
                    head2head_df.columns = new_columns                
                else:
                    # Add new player to the dataframe
                    head2head_df[player_name] = None
                    head2head_df.loc[player_name] = [None] * len(head2head_df.columns)
                    head2head_df.loc[player_name, player_name] = '-'
                
    head2head_df = head2head_df.infer_objects(copy=False).fillna(0)
    
    # Check matches
    for entrant in entrants:
      gamerId = entrant['id'] if entrant['participants'][0]['user'] is not None else -1
      gamerTag = entrant['participants'][0]['gamerTag']
      for set in entrant['paginatedSets']['nodes']:
        
        # If player won set, mark head to head as win
        if set['winnerId'] == gamerId or (set['winnerId'] == None and gamerId == -1):
          player1name = set['slots'][0]['entrant']['participants'][0]['gamerTag']
          player2name = set['slots'][1]['entrant']['participants'][0]['gamerTag']
          rivalName = player1name if player1name != gamerTag else player2name
          
          # Get player row and rival column and add
          head2head_df.loc[gamerTag, rivalName] += 1
          
          # Add this if you want to subtract points for losing
          # df.loc[rivalName, gamerTag] -= 1
          
    return head2head_df