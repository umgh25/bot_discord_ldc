#!/usr/bin/env python3
"""
Script de test pour vérifier que la refactorisation fonctionne
"""

import sys
import os

def test_imports():
    """Teste que tous les imports fonctionnent"""
    print("🧪 Test des imports...")
    
    try:
        # Test des imports principaux
        sys.path.append('./src')
        sys.path.append('./config')
        
        from config.settings import validate_config, log_dev
        print("✅ config.settings importé avec succès")
        
        from src.database.models import supabase
        print("✅ src.database.models importé avec succès")
        
        from src.database.operations import save_vote, get_leaderboard
        print("✅ src.database.operations importé avec succès")
        
        from src.bot.utils.helpers import check_channel, validate_team
        print("✅ src.bot.utils.helpers importé avec succès")
        
        from src.bot.commands.vote import setup_vote_commands
        print("✅ src.bot.commands.vote importé avec succès")
        
        from src.bot.commands.info import setup_info_commands
        print("✅ src.bot.commands.info importé avec succès")
        
        from src.bot.commands.admin import setup_admin_commands
        print("✅ src.bot.commands.admin importé avec succès")
        
        from src.bot.main import setup_bot, run_bot
        print("✅ src.bot.main importé avec succès")
        
        from utils.keep_alive import keep_alive
        print("✅ utils.keep_alive importé avec succès")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'import : {e}")
        return False

def test_structure():
    """Teste que la structure des dossiers est correcte"""
    print("\n📁 Test de la structure...")
    
    required_files = [
        'main.py',
        'config/settings.py',
        'src/__init__.py',
        'src/bot/__init__.py',
        'src/bot/main.py',
        'src/bot/commands/__init__.py',
        'src/bot/commands/vote.py',
        'src/bot/commands/info.py',
        'src/bot/commands/admin.py',
        'src/bot/utils/__init__.py',
        'src/bot/utils/helpers.py',
        'src/database/__init__.py',
        'src/database/models.py',
        'src/database/operations.py',
        'utils/keep_alive.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"❌ Fichiers manquants : {missing_files}")
        return False
    
    return True

def test_config():
    """Teste la configuration"""
    print("\n⚙️ Test de la configuration...")
    
    try:
        from config.settings import MATCHES, MATCHES_PHASES, ENV
        
        print(f"✅ Configuration chargée")
        print(f"   - ENV: {ENV}")
        print(f"   - Matchs actifs: {len(MATCHES)}")
        print(f"   - Phases disponibles: {list(MATCHES_PHASES.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur de configuration : {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test de la refactorisation du Bot Discord LDC")
    print("=" * 50)
    
    # Tests
    tests = [
        ("Structure des fichiers", test_structure),
        ("Configuration", test_config),
        ("Imports", test_imports),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Résultat : {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! La refactorisation est fonctionnelle.")
        return True
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez la structure.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 