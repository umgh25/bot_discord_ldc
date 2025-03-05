# Bot Discord - Pronostics Ligue des Champions 🏆

Un bot Discord pour gérer les pronostics de la Ligue des Champions, permettant aux utilisateurs de voter pour leurs équipes favorites et de suivre leurs scores.

## 🛠️ Technologies Utilisées

- Python 3.9
- discord.py 2.3.2
- Flask 3.0.0
- python-dotenv 1.0.0
- Render (pour l'hébergement)

## 📋 Prérequis

- Python 3.9 ou supérieur
- Un compte Discord Developer
- Un compte GitHub
- Un compte Render

## 🚀 Installation et Configuration

### 1. Configuration Discord

1. Allez sur [Discord Developer Portal](https://discord.com/developers/applications)
2. Créez une nouvelle application
3. Dans la section "Bot" :
   - Cliquez sur "Add Bot"
   - Activez les "Privileged Gateway Intents" (MESSAGE CONTENT INTENT)
   - Copiez le token du bot
4. Invitez le bot sur votre serveur en utilisant l'URL d'OAuth2 générée dans la section "OAuth2"

### 2. Configuration Locale

1. Clonez le repository :
```bash
git clone https://github.com/votre-nom/bot_discord_ldc.git
cd bot_discord_ldc
```

2. Créez un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

4. Créez un fichier `.env` :
```env
DISCORD_TOKEN=votre_token_discord
```

### 4. Création des Fichiers de Données

1. Créez deux fichiers JSON vides à la racine du projet :

`votes.json` :
```json
{}
```

`points.json` :
```json
{}
```

Ces fichiers sont essentiels pour :
- `votes.json` : Stockage des votes des utilisateurs
- `points.json` : Stockage des points attribués

⚠️ Note : Ces fichiers doivent être créés avant le premier lancement du bot.

### 3. Déploiement sur Render

1. Créez un compte sur [Render](https://render.com)
2. Connectez votre repository GitHub
3. Créez un nouveau "Background Worker"
4. Configurez les variables d'environnement :
   - `DISCORD_TOKEN` = votre_token_discord
5. Configuration du service :
   - Environment : Python 3
   - Build Command : `pip install -r requirements.txt`
   - Start Command : `python3 bot.py`


## 🎮 Commandes Disponibles

### Commandes Principales
- `!vote <numéro du match> <nom de l'équipe>` - Pour voter
- `!modifier_vote <numéro du match> <nom de l'équipe>` - Modifier un vote
- `!supprimer_vote <numéro du match>` - Supprimer un vote

### Commandes de Consultation
- `!recap` - Voir tous vos votes
- `!voir_votes @utilisateur` - Voir les votes d'un autre utilisateur
- `!all_votes` - Voir les statistiques globales

### Commandes Administrateur
- `!point @utilisateur <numéro du match> <points>` - Attribuer des points
- `!reset_points @utilisateur` - Réinitialiser les points
- `!classement` - Voir le classement général

## 🏆 Système de Points

- Victoire (pronostic correct) : +1 point
- Absence de vote avant le match : -1 point
- Les points sont attribués par les administrateurs après chaque match

## 🤝 Contribution

1. Fork le projet
2. Créez une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout d'une nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

## ⚠️ Notes Importantes

- Ne jamais commiter le fichier `.env`
- Toujours garder le token Discord secret
- Vérifier les permissions du bot sur Discord
- Assurez-vous que le bot a les bonnes intentions activées dans le portail développeur Discord

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

Pour toute question ou problème :
1. Ouvrez une issue sur GitHub
2. Consultez la [documentation Discord.py](https://discordpy.readthedocs.io/)