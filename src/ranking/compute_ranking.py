from math import sqrt

import pandas as pd
import json
import os
import sys

from ranking.data_manager import DataManager

def get_podium_bonus(placement) -> float:
    if placement == 1:
        return 1.25
    elif placement == 2:
        return 1.15
    elif placement == 3:
        return 1.08
    else:
        return 1.0

def compute_ranking(data_manager: DataManager):
    # Get the list of tournaments and players from the data manager
    tournaments = data_manager.get_tournaments()
    tiers = data_manager.get_tournament_tiers()
    players = data_manager.get_players()
    rankings = data_manager.get_rankings()
    tournament_weights = [0.4, 0.3, 0.2, 0.1]  # Weights for the top 4 tournaments
    
    # Compute each tournament value based on its tier and the number of entrants
    all_player_data = {}
    for tournament in tournaments:
        tier_multiplier = tiers.get(tournament.get("tier", "D"), 1.0)  # Default to C tier if not found
        entrants = tournament.get("entrants", 0)
        tournament_value = entrants * 5
        all_tournament_players = {player["gamerTag"] for player in tournament.get("player_data", [])}
        
        # Look for special players in the tournament
        special_bonus = 0
        for player in all_tournament_players:
            if player in players:
                max_ranking = max(rankings[player_ranking] for player_ranking in players[player])
                special_bonus += max_ranking
        
        # Apply decreasing returns to the special bonus
        tournament_value += special_bonus ** 0.6
        tournament_value *= tier_multiplier
        
        # Compute each player's score based on their placement in the tournament
        for player in tournament.get("player_data", []):
            user_id = player["userId"]
            gamer_tag = player["gamerTag"]
            placement = player["placement"]
            
            if user_id not in all_player_data:
                all_player_data[user_id] = {"gamerTag": [gamer_tag], "ranking_score": 0, "head-to-head-score": 0, "tournament_scores": {}}
            elif gamer_tag not in all_player_data[user_id]["gamerTag"]:
                all_player_data[user_id]["gamerTag"].append(gamer_tag)
            all_player_data[user_id]["tournament_scores"][tournament["name"]] = tournament_value * (((tournament["entrants"] - placement + 1) / tournament["entrants"]) ** 1.7)
            
            # Add player's ranking score to the final list
            if gamer_tag in players:
                all_player_data[user_id]["ranking_score"] = max(all_player_data[user_id]["ranking_score"], max(rankings[player_ranking] for player_ranking in players[gamer_tag]))
    

    # Compute final tournament scores for each player based on the top 3 (or 4) tournaments they participated in
    for player_id, player_data in all_player_data.items():
        tournament_scores = list(player_data["tournament_scores"].values())
        tournament_scores.sort(reverse=True)      
        weighted_score = sum(score * weight for score, weight in zip(tournament_scores[:4], tournament_weights[:4]))
        all_player_data[player_id]["final_score"] = weighted_score + player_data["ranking_score"]
        
    # Compute head-to-head scores for each player based on their wins on the tournament data
    for tournament in tournaments:
        for player in tournament.get("player_data", []):
            player_id = player["userId"]
            for opponent in player["matches"]["wins"]:
                opponent_id = opponent["userId"]
                
                # Don't count head-to-head score if the opponent was disqualified
                if not opponent["isDisqualified"]:
                    all_player_data[player_id]["head-to-head-score"] += all_player_data[opponent_id]["final_score"]
    
    # Compute final scores for each player based on their final score and head-to-head score
    for player_id, player_data in all_player_data.items():
        all_player_data[player_id]["final_score"] += sqrt(all_player_data[player_id]["head-to-head-score"]) * 0.5
    
    # Remove players who have participated in less than 3 tournaments from the final ranking and sort the remaining players by their final score in descending order
    filtered_players = {
        player_id: data
        for player_id, data in all_player_data.items()
        if len(data["tournament_scores"]) >= 3
    }
    sorted_players = sorted(
        filtered_players.items(),
        key=lambda x: x[1]["final_score"],
        reverse=True
    )
    
    # Create a DataFrame to store the final ranking data
    ranking_data = []
    for rank, (player_id, player_data) in enumerate(sorted_players, start=1):
        ranking_data.append({
            "Rank": rank,
            "GamerTag": ", ".join(player_data["gamerTag"]),
            "Final Score": player_data["final_score"]
        })
        
    ranking_df = pd.DataFrame(ranking_data)
    with pd.ExcelWriter('data/final_ranking.xlsx', engine='openpyxl', mode='w') as writer:
        ranking_df.to_excel(writer, sheet_name='Final Ranking', index=False)
    
        
            
                
    
    