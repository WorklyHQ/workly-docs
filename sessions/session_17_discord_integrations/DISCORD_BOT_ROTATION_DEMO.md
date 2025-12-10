# 🎭 Rotation d'Activités Discord - Workly Bot

## 📋 Qu'est-ce que c'est ?

Le bot Discord de Workly (Kira) change maintenant automatiquement son activité **toutes les 60 secondes** pour afficher différents messages sur son profil Discord.

## 🎨 Activités en rotation

Le bot alterne entre ces 4 activités :

1. **🎮 Playing** : "Regarde ton bureau 🖥️"
2. **🎧 Listening** : "tes messages 📻"
3. **👀 Watching** : "le VRM s'animer 👀"
4. **🎮 Playing** : "avec l'IA conversationnelle 🤖"

## ⚙️ Fonctionnement technique

### Code ajouté

**Dans `__init__`** :
```python
self.activity_rotation_task = None  # Référence à la tâche async
```

**Dans `on_ready`** :
```python
# Lancer la rotation automatiquement au démarrage
self.activity_rotation_task = self.loop.create_task(self._rotate_activities())
```

**Nouvelle méthode `_rotate_activities`** :
```python
async def _rotate_activities(self):
    """Rotation automatique des activités Discord toutes les 60 secondes"""
    activities = [
        discord.Activity(type=discord.ActivityType.playing, name="Regarde ton bureau 🖥️"),
        discord.Activity(type=discord.ActivityType.listening, name="tes messages 📻"),
        discord.Activity(type=discord.ActivityType.watching, name="le VRM s'animer 👀"),
        discord.Activity(type=discord.ActivityType.playing, name="avec l'IA conversationnelle 🤖"),
    ]

    idx = 0
    while True:
        try:
            await self.change_presence(activity=activities[idx])
            logger.debug(f"🎭 Activité changée: {activities[idx].name}")
            idx = (idx + 1) % len(activities)
            await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"❌ Erreur rotation activité: {e}")
            await asyncio.sleep(60)
```

**Méthode `close` pour arrêt propre** :
```python
async def close(self):
    """Fermeture propre du bot"""
    if self.activity_rotation_task:
        self.activity_rotation_task.cancel()
        logger.info("🛑 Rotation d'activités arrêtée")
    await super().close()
```

## 🚀 Comment tester

1. **Lance le bot Discord** (si pas déjà lancé) :
   ```bash
   cd c:\Dev\workly_project\workly-desktop
   .\venv\Scripts\Activate.ps1
   python -m src.discord_bot.bot
   ```

2. **Ouvre Discord** et regarde le profil du bot

3. **Observe** : l'activité change toutes les 60 secondes

4. **Logs** : vérifie dans la console, tu verras :
   ```
   DEBUG:src.discord_bot.bot:🎭 Activité changée: Regarde ton bureau 🖥️
   DEBUG:src.discord_bot.bot:🎭 Activité changée: tes messages 📻
   ...
   ```

## ⏱️ Modifier l'intervalle

Pour changer l'intervalle de rotation, édite la ligne dans `_rotate_activities` :

```python
await asyncio.sleep(60)  # <-- Change cette valeur (en secondes)
```

Exemples :
- `30` = toutes les 30 secondes (rapide)
- `120` = toutes les 2 minutes (lent)
- `300` = toutes les 5 minutes (très lent)

## 🎨 Ajouter des activités

Pour ajouter plus de messages, édite la liste `activities` :

```python
activities = [
    discord.Activity(type=discord.ActivityType.playing, name="Regarde ton bureau 🖥️"),
    discord.Activity(type=discord.ActivityType.listening, name="tes messages 📻"),
    discord.Activity(type=discord.ActivityType.watching, name="le VRM s'animer 👀"),
    discord.Activity(type=discord.ActivityType.playing, name="avec l'IA conversationnelle 🤖"),
    # Ajoute tes propres messages ici :
    discord.Activity(type=discord.ActivityType.competing, name="un tournoi Discord 🏆"),
    discord.Activity(type=discord.ActivityType.listening, name="Spotify 🎵"),
]
```

## 🛑 Désactiver la rotation

Si tu veux désactiver temporairement la rotation sans supprimer le code, commente la ligne dans `on_ready` :

```python
# self.activity_rotation_task = self.loop.create_task(self._rotate_activities())
```

Ou supprime la tâche et mets un statut fixe :

```python
# Dans on_ready, remplace la rotation par :
activity = discord.Activity(type=discord.ActivityType.playing, name="Regarde ton bureau 🖥️")
await self.change_presence(activity=activity)
```

## 📊 Avantages

✅ **Rend le bot plus vivant** : change régulièrement d'apparence
✅ **Montre différentes fonctionnalités** : VRM, IA, messages...
✅ **Attire l'attention** : les utilisateurs remarquent les changements
✅ **Non-invasif** : ne pollue pas les channels, juste le profil
✅ **Facile à personnaliser** : modifier les messages ou l'intervalle

## ⚠️ Limitations Discord

- **Rate limiting** : Discord limite la fréquence de changement de présence. Respecte un intervalle minimum (30-60s recommandé).
- **Cache** : les changements peuvent prendre quelques secondes à s'afficher chez les autres utilisateurs.

## 🎯 Idées futures

- Rotation **conditionnelle** (ex: afficher stats en temps réel)
- **Synchroniser** avec l'état du VRM (ex: "VRM chargé" quand actif)
- **Mode nuit/jour** : messages différents selon l'heure
- **Événements** : messages spéciaux lors de nouvelles versions

---

**🎭 Profite de ton bot Discord vivant ! ✨**
