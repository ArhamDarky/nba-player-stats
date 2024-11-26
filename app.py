from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

# Create a Flask application
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS)
CORS(app)

def get_team_players(team_name, season):
    """
    Get players from a specific team using the NBA API.
    """
    headers = {
        'x-rapidapi-host': "api-nba-v1.p.rapidapi.com",
        'x-rapidapi-key': "171a9990camsh0d24dee603f77eep1b73efjsnde200cc3946e"
    }
    
    try:
        # NBA API endpoint to get teams
        teams_url = "https://api-nba-v1.p.rapidapi.com/teams"
        response = requests.get(teams_url, headers=headers)
        response.raise_for_status()
        teams_data = response.json()
        
        # Find the team ID
        team_id = None
        for team in teams_data.get('response', []):
            if team_name.lower() in team.get('name', '').lower():
                team_id = team['id']
                break
        
        if not team_id:
            return None
            
        # Get players from the team
        players_url = "https://api-nba-v1.p.rapidapi.com/players"
        querystring = {"team": team_id, "season": season}
        
        players_response = requests.get(players_url, headers=headers, params=querystring)
        players_response.raise_for_status()
        players_data = players_response.json()
        
        if not players_data.get('response'):
            return None
            
        # Return list of players with their details
        players_list = []
        for player in players_data['response']:
            players_list.append({
                'id': player['id'],
                'name': f"{player.get('firstname', '')} {player.get('lastname', '')}",
                'position': player.get('position', ''),
                'jersey': player.get('jersey', '')
            })
            
        return players_list
    
    except requests.exceptions.RequestException:
        return None

def get_player_stats_by_id(player_id, season, is_playoffs=False):
    """
    Get player statistics using their ID, with option for regular season or playoff stats.
    """
    headers = {
        'x-rapidapi-host': "api-nba-v1.p.rapidapi.com",
        'x-rapidapi-key': "171a9990camsh0d24dee603f77eep1b73efjsnde200cc3946e"
    }
    
    try:
        # NBA API endpoint for player statistics
        stats_url = "https://api-nba-v1.p.rapidapi.com/players/statistics"
        querystring = {"id": str(player_id), "season": season}
        
        stats_response = requests.get(stats_url, headers=headers, params=querystring)
        stats_response.raise_for_status()
        stats_data = stats_response.json()
        
        if stats_data.get('response'):
            games = stats_data['response']
            if not games:
                return None
                
            valid_games = 0
            total_points = 0
            total_assists = 0
            total_rebounds = 0
            total_minutes = 0
            total_field_goals_made = 0
            total_field_goals_attempted = 0
            total_three_pointers_made = 0
            total_three_pointers_attempted = 0
            
            for game in games:
                # Check if game is playoffs if specified
                is_playoff_game = game.get('game', {}).get('stage') == 'Playoffs'
                if is_playoffs and not is_playoff_game:
                    continue
                if not is_playoffs and is_playoff_game:
                    continue
                
                # Only count games where the player has minutes played
                if game.get('min') and game['min'] != '0:00':
                    valid_games += 1
                    
                    # Parse minutes
                    minutes_parts = game.get('min', '0:00').split(':')
                    total_minutes += int(minutes_parts[0]) + (int(minutes_parts[1]) / 60 if len(minutes_parts) > 1 else 0)
                    
                    # Accumulate stats
                    total_points += game.get('points', 0) or 0
                    total_assists += game.get('assists', 0) or 0
                    
                    # Rebounds
                    total_reb = game.get('totalRebounds', 0) or 0
                    def_reb = game.get('defReb', 0) or 0
                    off_reb = game.get('offReb', 0) or 0
                    total_rebounds += total_reb if total_reb > 0 else (def_reb + off_reb)
                    
                    # Field Goals
                    fgm = game.get('fgm', 0) or 0
                    fga = game.get('fga', 0) or 0
                    total_field_goals_made += fgm
                    total_field_goals_attempted += fga
                    
                    # Three Pointers
                    tpm = game.get('tpm', 0) or 0
                    tpa = game.get('tpa', 0) or 0
                    total_three_pointers_made += tpm
                    total_three_pointers_attempted += tpa
            
            if valid_games > 0:
                # Calculate percentages and averages
                avg_stats = {
                    'games_played': valid_games,
                    'ppg': round(total_points / valid_games, 1),
                    'apg': round(total_assists / valid_games, 1),
                    'rpg': round(total_rebounds / valid_games, 1),
                    'mpg': round(total_minutes / valid_games, 1),
                    'fg_percentage': round((total_field_goals_made / total_field_goals_attempted * 100), 1) if total_field_goals_attempted > 0 else 0,
                    'three_point_percentage': round((total_three_pointers_made / total_three_pointers_attempted * 100), 1) if total_three_pointers_attempted > 0 else 0,
                    'is_playoffs': is_playoffs
                }
                return avg_stats
            else:
                return None
            
        return None
        
    except requests.exceptions.RequestException:
        return None

# Route to get team players
@app.route('/get_team_players', methods=['GET'])
def team_players_route():
    team_name = request.args.get('team')
    season = request.args.get('season')
    
    if not team_name or not season:
        return jsonify({"error": "Missing team or season"}), 400
    
    players = get_team_players(team_name, season)
    
    if players:
        return jsonify(players)
    else:
        return jsonify({"error": "No players found"}), 404

# Route to get player stats
@app.route('/get_player_stats', methods=['GET'])
def player_stats_route():
    player_id = request.args.get('player_id')
    season = request.args.get('season')
    is_playoffs = request.args.get('is_playoffs', 'false').lower() == 'true'
    
    if not player_id or not season:
        return jsonify({"error": "Missing player ID or season"}), 400
    
    stats = get_player_stats_by_id(player_id, season, is_playoffs)
    
    if stats:
        return jsonify(stats)
    else:
        return jsonify({"error": "No stats found"}), 404

# Main entry point to run the Flask application
if __name__ == '__main__':
    app.run(debug=True)