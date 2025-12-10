# Session 17 - Intégrations Discord 🎮

**Date** : 10 décembre 2025
**Statut** : ✅ Complété
**Version** : 0.20.0-alpha

---

## 📋 Vue d'ensemble

Cette session documente l'implémentation complète de deux intégrations Discord majeures pour Workly :

1. **Discord Rich Presence** (pypresence) - Affiche l'activité Workly sur le profil utilisateur Discord
2. **Discord Bot - Rotation d'activités** - Rend le bot Discord plus vivant avec des statuts changeants

---

## 🎯 Objectifs

### Discord Rich Presence
- ✅ Implémenter module `discord_presence.py` avec pypresence
- ✅ Intégrer dans l'application principale (8 points d'intégration)
- ✅ Afficher statuts : Idle, VRM chargé, Conversation, IA en réflexion
- ✅ Gestion d'erreurs (Discord fermé, connexion perdue)
- ✅ Configuration utilisateur (enabled/disabled, client_id)
- ✅ Documentation utilisateur complète

### Discord Bot - Rotation
- ✅ Implémenter rotation automatique d'activités (4 messages)
- ✅ Changer statut toutes les 60 secondes
- ✅ Gestion lifecycle (démarrage/arrêt propre)
- ✅ Documentation technique

---

## 🚀 Fonctionnalités implémentées

### 1. Discord Rich Presence (pypresence)

**Fichier créé** : `src/discord_presence.py` (190 lignes)

**Classe** : `WorklyDiscordPresence`

**Méthodes principales** :
- `connect()` → Connexion non-bloquante à Discord
- `disconnect()` → Déconnexion propre
- `update_status(state, details, **kwargs)` → Mise à jour générique
- `set_idle_status()` → "Idle - Avatar en attente"
- `set_vrm_ready_status()` → "Avatar VRM actif - Prêt à discuter"  ✨ NOUVEAU
- `set_conversation_status(name)` → "En conversation - Discute avec X"
- `set_thinking_status()` → "En réflexion - Génère une réponse"
- `set_listening_status()` → "En écoute - Écoute l'utilisateur"
- `set_vrm_loading_status()` → "Initialisation - Chargement VRM"
- `set_ai_loading_status()` → "Initialisation IA - Chargement modèle"
- `set_expression_status(expr)` → "Avatar expressif - Expression: X"

**Intégration dans app.py** :
- Ligne ~228 : Initialisation `self.discord_presence`
- Ligne ~2774 : Méthode `_init_discord_presence()`
- Ligne ~2780 : Helper `_update_discord_presence_vrm_loaded()` ✨ MODIFIÉ
- Ligne ~2785 : Helper `_update_discord_presence_ai_loading()`
- Ligne ~2790 : Helper `_update_discord_presence_conversation()`
- Ligne ~2795 : Helper `_update_discord_presence_thinking()`
- Ligne ~2820 : Déconnexion dans `closeEvent()`

**Points d'intégration (8)** :
1. **VRM load** (toggle_vrm_model) → `set_vrm_ready_status()`
2. **VRM unload** (toggle_vrm_model) → `set_idle_status()`
3. **AI load start** (load_ai_model) → `set_ai_loading_status()`
4. **AI load complete** (load_ai_model) → `set_idle_status()`
5. **Conversation start** (send_chat_message) → `set_conversation_status()`
6. **IA thinking** (send_chat_message) → `set_thinking_status()`
7. **Conversation continue** (message processing) → `set_conversation_status()`
8. **App close** (closeEvent) → `disconnect()`

**Configuration** (`data/config.json`) :
```json
{
  "discord_presence": {
    "enabled": false,
    "client_id": ""
  }
}
```

**Dépendance** : `pypresence>=4.6.0` (ajouté à `requirements.txt`)

**Gestion d'erreurs** :
- Discord fermé → Warning log, pas de crash
- Connexion perdue → Logged, `connected = False`
- Assets manquants → Fonctionne sans images (texte + emojis)

**Statuts Discord affichés** :
- 😴 **Sans VRM** : "Idle - Avatar en attente"
- ✨ **VRM chargé** : "Avatar VRM actif - Prêt à discuter" (NOUVEAU !)
- 🤖 **AI loading** : "Initialisation IA - Chargement modèle"
- 💬 **Conversation** : "En conversation - Discute avec Kira"
- 🤔 **IA réfléchit** : "En réflexion - Génère une réponse"
- ⏳ **VRM loading** : "Initialisation - Chargement VRM"

**Boutons** :
- Label : "En savoir plus"
- URL : https://workly.xyon.site.elsites.fr
- ⚠️ **Note** : Les boutons ne fonctionnent que pour applications Discord vérifiées (75+ serveurs)

---

### 2. Discord Bot - Rotation d'activités

**Fichier modifié** : `src/discord_bot/bot.py`

**Changements** :

1. **Attribut `__init__`** (ligne ~102) :
   ```python
   self.activity_rotation_task = None
   ```

2. **Lancement rotation** dans `on_ready` (ligne ~120) :
   ```python
   self.activity_rotation_task = self.loop.create_task(self._rotate_activities())
   ```

3. **Nouvelle méthode** `_rotate_activities()` (ligne ~123) :
   - 4 activités différentes (Playing, Listening, Watching)
   - Rotation toutes les 60 secondes
   - Gestion d'erreurs avec `try/except`
   - Logs de debug

4. **Nouvelle méthode** `close()` (ligne ~437) :
   - Annule la tâche de rotation proprement
   - Appelle `super().close()`

**Activités en rotation** :
1. 🎮 **Playing** : "Regarde ton bureau 🖥️"
2. 🎧 **Listening** : "Écoute tes messages 📻"
3. 👀 **Watching** : "Regarde le VRM s'animer 👀"
4. 🤖 **Playing** : "Joue avec l'IA conversationnelle 🤖"

**Intervalle** : 60 secondes (modifiable dans le code)

**Lifecycle** :
- Démarrage automatique lors de la connexion du bot
- Arrêt propre lors de la fermeture (`bot.close()`)
- Continue en cas d'erreur ponctuelle

---

## 📁 Fichiers créés/modifiés

### Nouveaux fichiers

**Code** :
- `src/discord_presence.py` (190 lignes)

**Documentation** :
- `DISCORD_PRESENCE_SETUP.md` (200+ lignes) - Guide utilisateur complet
- `DISCORD_BOT_ROTATION_DEMO.md` (170+ lignes) - Documentation rotation

**Configuration** :
- `data/config.json` → Ajout section `discord_presence`
- `requirements.txt` → Ajout `pypresence>=4.6.0`

### Fichiers modifiés

**Code** :
- `src/gui/app.py` → 8 intégrations Discord Presence
- `src/discord_bot/bot.py` → Rotation d'activités

---

## 🔧 Configuration utilisateur

### Discord Rich Presence

**Étape 1** : Créer application Discord
1. https://discord.com/developers/applications
2. Créer nouvelle application "Workly"
3. Copier Client ID

**Étape 2** : Configurer Workly
```json
{
  "discord_presence": {
    "enabled": true,
    "client_id": "TON_CLIENT_ID_ICI"
  }
}
```

**Étape 3** : Lancer Workly avec Discord ouvert

**Guide complet** : Voir `DISCORD_PRESENCE_SETUP.md`

### Discord Bot - Rotation

**Aucune configuration nécessaire** - Fonctionne automatiquement dès que le bot se connecte.

**Modification de l'intervalle** :
```python
# Dans _rotate_activities(), ligne ~143
await asyncio.sleep(60)  # <-- Modifier cette valeur (secondes)
```

**Modification des messages** :
```python
# Dans _rotate_activities(), ligne ~126-139
activities = [
    discord.Activity(type=discord.ActivityType.playing, name="Ton message"),
    # ... ajouter d'autres activités
]
```

---

## 🐛 Problèmes résolus

### 1. Status "Idle" après chargement VRM

**Problème** : Quand le VRM se charge, Discord affichait "Idle - Avatar en attente" au lieu d'un statut "Prêt"

**Cause** : `_update_discord_presence_vrm_loaded()` appelait `set_idle_status()`

**Solution** :
- Créé nouvelle méthode `set_vrm_ready_status()`
- Mise à jour de `_update_discord_presence_vrm_loaded()` pour l'utiliser
- Affiche maintenant : "✨ Avatar VRM actif - Prêt à discuter"

**Fichiers** :
- `src/discord_presence.py` → Nouvelle méthode `set_vrm_ready_status()`
- `src/gui/app.py` → Appel mis à jour ligne ~2807

### 2. Boutons Discord non affichés

**Problème** : Les boutons "En savoir plus" ne s'affichaient pas sur Discord

**Cause** : Discord a retiré le support des boutons Rich Presence pour applications non-vérifiées (2021)

**Solution** :
- Boutons fonctionnent uniquement pour applications vérifiées (75+ serveurs)
- Gardé le code pour compatibilité future
- Documentation ajoutée sur la limitation

**Workaround** : Demander vérification de l'application Discord

### 3. Token Discord invalide (bot)

**Problème** : `LoginFailure: Improper token has been passed`

**Cause** : Token Discord expiré/révoqué dans `.env`

**Solution** :
1. Réinitialiser token sur Discord Developer Portal
2. Copier nouveau token
3. Mettre à jour `.env`

---

## 📊 Tests effectués

### Discord Rich Presence
- ✅ Connexion réussie avec Discord ouvert
- ✅ Warning propre si Discord fermé (pas de crash)
- ✅ Statuts s'affichent correctement :
  - Idle (sans VRM)
  - VRM actif prêt (avec VRM chargé) ✨
  - Conversation
  - IA réfléchit
- ✅ Timer fonctionne ("Depuis X minutes")
- ✅ Déconnexion propre lors de la fermeture
- ✅ Import module successful

### Discord Bot - Rotation
- ✅ Bot se connecte correctement
- ✅ Rotation démarre automatiquement
- ✅ Activités changent toutes les 60s
- ✅ Pas de crash en cas d'erreur ponctuelle
- ✅ Arrêt propre lors de `bot.close()`
- ✅ Logs debug corrects

---

## 🎓 Apprentissages

### pypresence vs discord.py

**pypresence (Rich Presence)** :
- Modifie le profil **utilisateur** (ton compte personnel)
- Affiche ce que **tu** fais (jouer à Workly)
- Nécessite Client ID d'une application Discord
- Fonctionne côté client

**discord.py (Bot)** :
- Modifie le statut du **bot** (compte bot)
- Affiche ce que le **bot** fait
- Visible dans la liste des membres du serveur
- Fonctionne côté serveur

**Différences clés** :
| Fonctionnalité | pypresence | discord.py |
|----------------|------------|------------|
| Cible | Profil utilisateur | Profil bot |
| Boutons | Non (sauf vérifiée) | N/A |
| Images | Oui (assets) | Non |
| Timer | Oui | Non |
| Activités | Custom RPC | Playing/Listening/Watching |

### Discord Rich Presence - Limitations

**Boutons** :
- Fonctionnent uniquement pour apps vérifiées (75+ serveurs)
- Non disponibles pour projets personnels/petits

**Images** :
- Doivent être uploadées sur Developer Portal
- Noms doivent correspondre exactement
- Cache Discord (5-10 min après upload)

**Rate limiting** :
- Ne pas changer trop souvent (max 1x/5s recommandé)
- Discord peut throttle/ban si abus

**Assets** :
- Non obligatoires (texte + emojis suffisent)
- Mieux sans images que avec images cassées

### AsyncIO avec discord.py

**Tâches en arrière-plan** :
```python
# Créer tâche qui tourne en boucle
self.loop.create_task(self._rotate_activities())

# Arrêter proprement
task.cancel()
```

**Gestion d'erreurs** :
- Toujours `try/except` dans les boucles infinies
- Continuer même si erreur ponctuelle
- Logger les erreurs pour debug

---

## 🚀 Prochaines étapes possibles

### Discord Rich Presence

1. **Uploader images/assets** sur Developer Portal
   - Logo Workly (512x512)
   - Icônes statuts (talking, thinking, etc.)
   - Tester avec vraies images

2. **Demander vérification** de l'application Discord
   - Objectif : Débloquer les boutons
   - Nécessite 75+ serveurs
   - Promouvoir Workly pour atteindre le seuil

3. **Ajouter plus de statuts** :
   - Expression faciale actuelle (joy, sad, etc.)
   - Mode nuit/jour
   - Statistiques (conversations/jour)

4. **Synchronisation avancée** :
   - Refléter état VRM en temps réel
   - Changer statut selon émotion détectée
   - Afficher nom du modèle VRM chargé

### Discord Bot

1. **Commande admin `!setactivity`**
   - Changer activité à la volée
   - Restreint aux admins
   - Persiste jusqu'au prochain cycle

2. **Rotation conditionnelle** :
   - Messages différents selon heure (jour/nuit)
   - Afficher stats en temps réel (serveurs, uptime)
   - Mode événement (annonce nouvelle version)

3. **Intégration VRM → Bot** :
   - Bot affiche "VRM chargé" quand actif
   - Bot montre expression actuelle
   - Synchronisation GUI ↔ Bot status

4. **Analytics** :
   - Tracker quelle activité attire le plus
   - Statistiques d'engagement
   - A/B testing messages

---

## 📚 Ressources

### Documentation officielle
- **pypresence** : https://github.com/qwertyquerty/pypresence
- **discord.py** : https://discordpy.readthedocs.io/
- **Discord Developer Portal** : https://discord.com/developers/docs

### Guides créés
- `DISCORD_PRESENCE_SETUP.md` → Setup Rich Presence
- `DISCORD_BOT_ROTATION_DEMO.md` → Utilisation rotation
- Cette documentation → Vue d'ensemble complète

### Fichiers de code
- `scripts/discord_presence.py` → Module complet
- `scripts/bot_rotation_extract.py` → Extraits bot

---

## ✅ Checklist de complétion

### Discord Rich Presence
- [x] Module `discord_presence.py` créé
- [x] Intégration dans `app.py` (8 points)
- [x] Configuration `config.json`
- [x] Dépendance `pypresence` ajoutée
- [x] Gestion d'erreurs complète
- [x] Tests réussis (import, connexion, statuts)
- [x] Documentation utilisateur (`DISCORD_PRESENCE_SETUP.md`)
- [x] Nouveau statut VRM Ready implémenté ✨
- [x] Problème "Idle après VRM" résolu

### Discord Bot - Rotation
- [x] Méthode `_rotate_activities()` créée
- [x] 4 activités configurées
- [x] Lifecycle géré (start/stop)
- [x] Tests rotation OK
- [x] Documentation (`DISCORD_BOT_ROTATION_DEMO.md`)

### Documentation
- [x] README session créé
- [x] Scripts archivés dans `scripts/`
- [x] Guides utilisateur complets
- [x] Problèmes documentés

### Commits
- [ ] Commit Discord Rich Presence (en attente)
- [ ] Commit Bot Rotation (en attente)
- [ ] Docs déplacées (en attente)

---

**🎭 Session 17 terminée avec succès ! Discord integrations opérationnelles ! ✨**
