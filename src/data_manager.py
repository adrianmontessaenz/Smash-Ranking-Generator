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
           
        # Check for new names first
        for entrant in entrants:
          gamerTag = entrant['participants'][0]['gamerTag']
          # If new player, add to table
          if gamerTag not in players_column:
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
          
          # Add this if you want to subtract points for losing
          # df.loc[rivalName, gamerTag] -= 1
    return df