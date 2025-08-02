#!/usr/bin/env python3
"""
Bot Discord LDC - Point d'entrée principal
Système de vote pour la Ligue des Champions
"""

import sys
sys.path.append('./src')
sys.path.append('./config')

from src.bot.main import run_bot
from utils.keep_alive import keep_alive

if __name__ == "__main__":
    print("🚀 Démarrage du Bot Discord LDC...")
    
    # Démarrer le keep alive (pour les plateformes comme Render)
    keep_alive()
    
    # Lancer le bot
    run_bot() 