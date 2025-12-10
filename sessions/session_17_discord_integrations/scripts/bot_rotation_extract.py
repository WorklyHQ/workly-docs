# Extrait de bot.py - Session 17
# Modifications pour la rotation d'activités Discord

# Dans __init__ :
# Rotation d'activités
self.activity_rotation_task = None

# Dans on_ready :
# Lancer la rotation d'activités
self.activity_rotation_task = self.loop.create_task(self._rotate_activities())

# Nouvelle méthode :
async def _rotate_activities(self):
    """Rotation automatique des activités Discord toutes les 60 secondes"""
    activities = [
        discord.Activity(
            type=discord.ActivityType.playing, name="Regarde ton bureau 🖥️"
        ),
        discord.Activity(
            type=discord.ActivityType.listening, name="Écoute tes messages 📻"
        ),
        discord.Activity(
            type=discord.ActivityType.watching, name="Regarde le VRM s'animer 👀"
        ),
        discord.Activity(
            type=discord.ActivityType.playing, name="Joue avec l'IA conversationnelle 🤖"
        ),
    ]

    idx = 0
    while True:
        try:
            await self.change_presence(activity=activities[idx])
            logger.debug(f"🎭 Activité changée: {activities[idx].name}")
            idx = (idx + 1) % len(activities)
            await asyncio.sleep(60)  # Changer toutes les 60 secondes
        except Exception as e:
            logger.error(f"❌ Erreur rotation activité: {e}")
            await asyncio.sleep(60)

# Nouvelle méthode close :
async def close(self):
    """Fermeture propre du bot"""
    # Arrêter la rotation d'activités
    if self.activity_rotation_task:
        self.activity_rotation_task.cancel()
        logger.info("🛑 Rotation d'activités arrêtée")

    # Appeler la méthode close parente
    await super().close()
