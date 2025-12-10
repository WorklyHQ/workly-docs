"""Module de gestion de la Discord Rich Presence pour Workly"""

from pypresence import Presence, InvalidPipe
import time
import logging
from typing import Optional


class WorklyDiscordPresence:
    """Gère la Rich Presence Discord pour Workly"""

    def __init__(self, client_id: str):
        """
        Initialise le gestionnaire Discord RPC

        Args:
            client_id: Client ID de l'application Discord
        """
        self.client_id = client_id
        self.rpc: Optional[Presence] = None
        self.connected = False
        self.logger = logging.getLogger(__name__)
        self.start_time = int(time.time())

    def connect(self) -> bool:
        """
        Connecte à Discord (ne plante pas si Discord n'est pas ouvert)

        Returns:
            True si connexion réussie, False sinon
        """
        try:
            self.rpc = Presence(self.client_id)
            self.rpc.connect()
            self.connected = True
            self.start_time = int(time.time())
            self.logger.info("✅ Discord Rich Presence connectée")
            return True
        except (InvalidPipe, FileNotFoundError):
            self.logger.warning("⚠️ Discord n'est pas ouvert, Rich Presence désactivée")
            self.connected = False
            return False
        except Exception as e:
            self.logger.error(f"❌ Erreur Discord RPC: {e}")
            self.connected = False
            return False

    def update_status(self, state: str = None, details: str = None, **kwargs):
        """
        Met à jour le statut Discord

        Args:
            state: Texte en bas (sous-titre)
            details: Texte en haut (titre)
            **kwargs: Paramètres additionnels (large_image, small_image, etc.)
        """
        if not self.connected:
            return

        try:
            # Paramètres minimaux (sans images pour éviter les erreurs)
            update_params = {
                "state": state or "Idle",
                "details": details or "Avatar VRM actif",
                "start": self.start_time,
            }

            # Ajouter les images SEULEMENT si elles sont explicitement fournies
            if "large_image" in kwargs and kwargs["large_image"]:
                update_params["large_image"] = kwargs["large_image"]
                update_params["large_text"] = kwargs.get(
                    "large_text", "Workly - Assistant Virtuel"
                )

            if "small_image" in kwargs and kwargs["small_image"]:
                update_params["small_image"] = kwargs["small_image"]
                update_params["small_text"] = kwargs.get("small_text", "En ligne")

            # Ajouter les boutons si présents
            if "buttons" in kwargs:
                update_params["buttons"] = kwargs["buttons"]
            else:
                update_params["buttons"] = [
                    {
                        "label": "En savoir plus",
                        "url": "https://workly.xyon.site.elsites.fr",
                    }
                ]

            self.rpc.update(**update_params)
            self.logger.debug(f"📡 Discord RPC mis à jour: {state}")

        except Exception as e:
            self.logger.error(f"❌ Erreur mise à jour Discord: {e}")
            self.connected = False

    def set_conversation_status(self, avatar_name: str = "Kira"):
        """
        Affiche que l'utilisateur parle avec son avatar

        Args:
            avatar_name: Nom de l'avatar
        """
        self.update_status(
            state=f"Discute avec {avatar_name}",
            details="💬 En conversation",
        )

    def set_idle_status(self):
        """Affiche que l'avatar est inactif (sans VRM)"""
        self.update_status(
            state="Avatar en attente",
            details="😴 Idle",
        )

    def set_vrm_ready_status(self):
        """Affiche que l'avatar VRM est chargé et prêt"""
        self.update_status(
            state="Prêt à discuter",
            details="✨ Avatar VRM actif",
        )

    def set_listening_status(self):
        """Affiche que l'avatar écoute"""
        self.update_status(
            state="Écoute l'utilisateur",
            details="🎤 En écoute",
        )

    def set_thinking_status(self):
        """Affiche que l'avatar réfléchit"""
        self.update_status(
            state="Génère une réponse",
            details="🤔 En réflexion",
        )

    def set_expression_status(self, expression: str):
        """
        Affiche l'expression faciale actuelle

        Args:
            expression: Nom de l'expression (joy, sad, angry, etc.)
        """
        expression_emoji = {
            "joy": "😊",
            "sad": "😢",
            "angry": "😠",
            "surprised": "😲",
            "neutral": "😐",
            "fun": "😄",
            "sorrow": "😢",
        }

        emoji = expression_emoji.get(expression.lower(), "😊")
        self.update_status(
            state=f"Expression: {expression}",
            details=f"{emoji} Avatar expressif",
        )

    def set_vrm_loading_status(self):
        """Affiche que le modèle VRM est en cours de chargement"""
        self.update_status(
            state="Chargement du modèle VRM",
            details="⏳ Initialisation",
        )

    def set_ai_loading_status(self):
        """Affiche que l'IA est en cours de chargement"""
        self.update_status(
            state="Chargement du modèle IA",
            details="🤖 Initialisation IA",
        )

    def disconnect(self):
        """Déconnecte proprement"""
        if self.connected and self.rpc:
            try:
                self.rpc.close()
                self.logger.info("🔌 Discord Rich Presence déconnectée")
            except Exception as e:
                self.logger.error(f"⚠️ Erreur lors de la déconnexion: {e}")
        self.connected = False
        self.rpc = None
