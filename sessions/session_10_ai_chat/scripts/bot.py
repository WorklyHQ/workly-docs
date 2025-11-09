"""
Bot Discord pour Desktop-Mate (Kira)

Bot Discord qui permet à Kira de discuter sur Discord en utilisant :
- ChatEngine (Phase 5) pour générer les réponses
- EmotionAnalyzer (Phase 6) pour détecter les émotions
- UnityBridge pour faire réagir l'avatar VRM

Fonctionnalités :
- Réponse aux mentions (@Kira)
- Auto-reply dans canaux configurés
- Intégration complète avec système IA Desktop-Mate
- Rate limiting pour éviter spam
- Réaction émotionnelle VRM en temps réel
"""

import os
import logging
import asyncio
import time
from typing import Dict, Optional
from datetime import datetime

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import modules Desktop-Mate
from src.ai.chat_engine import get_chat_engine
from src.ai.emotion_analyzer import get_emotion_analyzer
from src.ipc.unity_bridge import UnityBridge
from src.utils.config import Config

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KiraDiscordBot(commands.Bot):
    """
    Bot Discord pour Kira (Desktop-Mate)
    
    Permet à Kira de discuter sur Discord en utilisant le système IA
    complet de Desktop-Mate (ChatEngine + EmotionAnalyzer + UnityBridge).
    """
    
    def __init__(
        self,
        chat_engine=None,
        emotion_analyzer=None,
        unity_bridge=None,
        config=None
    ):
        """
        Initialise le bot Discord Kira
        
        Args:
            chat_engine: ChatEngine pour générer réponses (si None, utilise singleton)
            emotion_analyzer: EmotionAnalyzer pour émotions (si None, utilise singleton)
            unity_bridge: UnityBridge pour VRM (si None, crée nouvelle instance)
            config: Config pour paramètres (si None, charge depuis config.json)
        """
        # Configuration Discord Intents
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True  # Nécessaire pour lire contenu messages
        intents.guilds = True
        
        super().__init__(
            command_prefix="!",  # Prefix commands (même si pas utilisé pour l'instant)
            intents=intents,
            help_command=None  # Désactiver help par défaut
        )
        
        # Composants Desktop-Mate
        self.chat_engine = chat_engine or get_chat_engine()
        self.emotion_analyzer = emotion_analyzer or get_emotion_analyzer()
        self.unity_bridge = unity_bridge or UnityBridge()
        self.config = config or Config()
        
        # Configuration Discord depuis config.json
        discord_config = self.config.get("discord", {})
        self.auto_reply_enabled = discord_config.get("auto_reply_enabled", False)
        self.auto_reply_channels = discord_config.get("auto_reply_channels", [])
        self.rate_limit_seconds = discord_config.get("rate_limit_seconds", 3)
        
        # Rate limiting par utilisateur
        self.last_response_time: Dict[int, float] = {}
        
        # Statistiques
        self.start_time = datetime.now()
        self.messages_processed = 0
        self.responses_sent = 0
        
        logger.info(
            f"✅ KiraDiscordBot initialisé "
            f"(auto_reply={self.auto_reply_enabled}, "
            f"channels={len(self.auto_reply_channels)})"
        )
    
    async def on_ready(self):
        """Event déclenché quand le bot est connecté à Discord"""
        logger.info(f"✅ Bot Discord connecté : {self.user.name} (ID: {self.user.id})")
        logger.info(f"📊 Connecté à {len(self.guilds)} serveur(s)")
        
        # Afficher serveurs
        for guild in self.guilds:
            logger.info(f"   - {guild.name} (ID: {guild.id})")
        
        # Status Discord
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="Ton bureau 🖥️"
        )
        await self.change_presence(activity=activity)
        
        logger.info("🤖 Kira est prête à discuter sur Discord ! 💬")
    
    async def on_message(self, message: discord.Message):
        """
        Event déclenché pour chaque message Discord
        
        Args:
            message: Message Discord reçu
        """
        # Ignorer nos propres messages
        if message.author == self.user:
            return
        
        # Ignorer les bots
        if message.author.bot:
            return
        
        self.messages_processed += 1
        
        # Déterminer si on doit répondre
        should_reply = self._should_reply_to_message(message)
        
        if not should_reply:
            return
        
        # Vérifier rate limiting
        if not self._check_rate_limit(message.author.id):
            logger.debug(
                f"⏱️ Rate limit : Ignorer message de {message.author.name} "
                f"(trop rapide)"
            )
            return
        
        # Nettoyer le prompt (enlever mention si présente)
        prompt = self._clean_prompt(message.content)
        
        if not prompt.strip():
            logger.debug("📝 Prompt vide après nettoyage, ignoré")
            return
        
        # Afficher typing indicator pendant traitement
        async with message.channel.typing():
            try:
                # Générer réponse via ChatEngine
                response = await self._generate_response(
                    prompt=prompt,
                    user_id=str(message.author.id),
                    username=message.author.name
                )
                
                # Envoyer réponse
                await message.channel.send(response)
                
                self.responses_sent += 1
                logger.info(
                    f"✅ Réponse envoyée à {message.author.name} "
                    f"({len(response)} chars)"
                )
                
            except Exception as e:
                logger.error(f"❌ Erreur génération/envoi réponse : {e}")
                await message.channel.send(
                    "Désolée, j'ai rencontré une erreur... 😔"
                )
    
    def _should_reply_to_message(self, message: discord.Message) -> bool:
        """
        Détermine si le bot doit répondre à un message
        
        Args:
            message: Message Discord
        
        Returns:
            True si doit répondre, False sinon
        """
        # Cas 1 : Bot mentionné (@Kira)
        if self.user.mentioned_in(message):
            logger.debug(f"💬 Mention détectée de {message.author.name}")
            return True
        
        # Cas 2 : Auto-reply activé dans ce canal
        if self.auto_reply_enabled and message.channel.id in self.auto_reply_channels:
            logger.debug(
                f"💬 Auto-reply activé dans canal {message.channel.name} "
                f"(ID: {message.channel.id})"
            )
            return True
        
        return False
    
    def _check_rate_limit(self, user_id: int) -> bool:
        """
        Vérifie le rate limiting pour un utilisateur
        
        Args:
            user_id: ID utilisateur Discord
        
        Returns:
            True si peut répondre, False si trop rapide
        """
        current_time = time.time()
        last_time = self.last_response_time.get(user_id, 0)
        
        # Vérifier délai minimum
        if current_time - last_time < self.rate_limit_seconds:
            return False
        
        # Mettre à jour timestamp
        self.last_response_time[user_id] = current_time
        return True
    
    def _clean_prompt(self, content: str) -> str:
        """
        Nettoie le prompt en enlevant les mentions
        
        Args:
            content: Contenu message Discord
        
        Returns:
            Prompt nettoyé
        """
        # Enlever mention du bot
        cleaned = content.replace(f"<@{self.user.id}>", "").strip()
        cleaned = cleaned.replace(f"<@!{self.user.id}>", "").strip()
        
        return cleaned
    
    async def _generate_response(
        self,
        prompt: str,
        user_id: str,
        username: str
    ) -> str:
        """
        Génère une réponse via ChatEngine et met à jour émotions VRM
        
        Args:
            prompt: Message de l'utilisateur
            user_id: ID utilisateur Discord
            username: Nom utilisateur Discord
        
        Returns:
            Réponse générée
        """
        logger.info(f"🤖 Génération réponse pour {username} : '{prompt[:50]}...'")
        
        # Générer réponse avec ChatEngine (bloquant, à exécuter dans executor)
        loop = asyncio.get_event_loop()
        chat_result = await loop.run_in_executor(
            None,
            lambda: self.chat_engine.chat(
                user_input=prompt,
                user_id=user_id,
                source="discord"
            )
        )
        
        response_text = chat_result.response
        
        logger.info(
            f"✅ Réponse générée : {len(response_text)} chars, "
            f"émotion={chat_result.emotion}"
        )
        
        # Analyser émotion avec EmotionAnalyzer avancé
        emotion_result = self.emotion_analyzer.analyze(
            text=response_text,
            user_id=user_id
        )
        
        logger.info(
            f"🎭 Émotion analysée : {emotion_result.emotion} "
            f"(intensité={emotion_result.intensity:.1f}, "
            f"confiance={emotion_result.confidence:.1f})"
        )
        
        # Envoyer émotion à Unity (si connecté)
        self._send_emotion_to_unity(emotion_result.emotion, emotion_result.intensity)
        
        return response_text
    
    def _send_emotion_to_unity(self, emotion: str, intensity: float):
        """
        Envoie l'émotion à Unity pour mise à jour VRM
        
        Args:
            emotion: Émotion détectée ('joy', 'angry', etc.)
            intensity: Intensité 0-100
        """
        if not self.unity_bridge.is_connected():
            logger.debug("⚠️ Unity non connecté, émotion non envoyée")
            return
        
        # Obtenir mapping VRM
        vrm_data = self.emotion_analyzer.get_vrm_blendshape(emotion, intensity)
        
        # Envoyer à Unity
        success = self.unity_bridge.set_expression(
            expression_name=vrm_data['blendshape'],
            value=vrm_data['value']
        )
        
        if success:
            logger.info(
                f"✅ Émotion envoyée à Unity : {vrm_data['blendshape']} "
                f"= {vrm_data['value']:.2f}"
            )
        else:
            logger.warning("⚠️ Échec envoi émotion à Unity")
    
    def get_stats(self) -> Dict:
        """
        Récupère les statistiques du bot
        
        Returns:
            Dictionnaire avec statistiques
        """
        uptime = datetime.now() - self.start_time
        
        return {
            'connected': self.is_ready(),
            'username': self.user.name if self.user else None,
            'guilds': len(self.guilds) if self.is_ready() else 0,
            'uptime_seconds': uptime.total_seconds(),
            'messages_processed': self.messages_processed,
            'responses_sent': self.responses_sent,
            'auto_reply_enabled': self.auto_reply_enabled,
            'auto_reply_channels': self.auto_reply_channels,
            'rate_limit_seconds': self.rate_limit_seconds
        }
    
    def get_status(self) -> Dict:
        """
        Récupère le statut de connexion du bot
        
        Returns:
            Dictionnaire avec informations de connexion
        """
        if not self.is_ready():
            return {
                'connected': False,
                'bot_name': None,
                'bot_id': None,
                'guilds_count': 0
            }
        
        return {
            'connected': True,
            'bot_name': f"{self.user.name}#{self.user.discriminator}",
            'bot_id': self.user.id,
            'guilds_count': len(self.guilds)
        }
    
    def get_connection_info(self) -> Dict:
        """
        Récupère les informations complètes de connexion
        
        Returns:
            Dictionnaire avec infos détaillées
        """
        if not self.is_ready():
            return {
                'connected': False,
                'bot_name': None,
                'guilds': [],
                'active_channels': []
            }
        
        guilds_info = [
            {'name': guild.name, 'id': guild.id}
            for guild in self.guilds
        ]
        
        # Channels auto-reply actifs
        active_channels = []
        for channel_id in self.auto_reply_channels:
            for guild in self.guilds:
                channel = guild.get_channel(channel_id)
                if channel:
                    active_channels.append({
                        'id': channel_id,
                        'name': channel.name,
                        'guild': guild.name
                    })
                    break
        
        return {
            'connected': True,
            'bot_name': f"{self.user.name}#{self.user.discriminator}",
            'guilds': guilds_info,
            'active_channels': active_channels
        }


# Instance globale (optionnel, pour usage singleton)
_bot_instance: Optional[KiraDiscordBot] = None


def get_discord_bot(
    chat_engine=None,
    emotion_analyzer=None,
    unity_bridge=None,
    config=None
) -> KiraDiscordBot:
    """
    Récupère l'instance globale du bot Discord (singleton)
    
    Args:
        chat_engine: ChatEngine (optionnel)
        emotion_analyzer: EmotionAnalyzer (optionnel)
        unity_bridge: UnityBridge (optionnel)
        config: Config (optionnel)
    
    Returns:
        Instance KiraDiscordBot
    """
    global _bot_instance
    
    if _bot_instance is None:
        _bot_instance = KiraDiscordBot(
            chat_engine,
            emotion_analyzer,
            unity_bridge,
            config
        )
    
    return _bot_instance


def run_discord_bot(token: Optional[str] = None):
    """
    Lance le bot Discord
    
    Args:
        token: Token Discord (si None, charge depuis .env)
    """
    # Charger token depuis .env si non fourni
    if token is None:
        load_dotenv()
        token = os.getenv("DISCORD_TOKEN")
    
    if not token:
        raise ValueError(
            "DISCORD_TOKEN non trouvé ! "
            "Définissez-le dans .env"
        )
    
    # Créer et lancer bot
    bot = get_discord_bot()
    
    logger.info("🚀 Lancement du bot Discord...")
    
    try:
        bot.run(token)
    except Exception as e:
        logger.error(f"❌ Erreur lancement bot Discord : {e}")
        raise


if __name__ == "__main__":
    # Lancer le bot directement
    run_discord_bot()
