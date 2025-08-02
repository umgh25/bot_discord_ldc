import sys
sys.path.append('../../../config')
from config.settings import CHANNEL_ID, MATCHES

def check_channel(interaction) -> bool:
    """Vérifie si la commande est utilisée dans le bon canal"""
    return str(interaction.channel_id) == CHANNEL_ID

def get_match_info(match_id):
    """Récupère les informations d'un match"""
    if match_id in MATCHES:
        return MATCHES[match_id]
    return None

def validate_team(match_id, team):
    """Valide si une équipe est valide pour un match donné"""
    match_info = get_match_info(match_id)
    if not match_info:
        return False, None, None
    
    team1, team2 = match_info
    team = team.strip()
    
    if team.lower() not in [team1.lower(), team2.lower()]:
        return False, team1, team2
    
    # Retourner le nom exact de l'équipe (pour garder la casse correcte)
    exact_team = team1 if team.lower() == team1.lower() else team2
    return True, team1, team2, exact_team

def format_match_list():
    """Formate la liste des matchs disponibles"""
    match_list = ""
    for match_id, match in MATCHES.items():
        team1, team2 = match
        match_list += f"\n**Match {match_id}** : {team1} vs {team2}"
    return match_list 