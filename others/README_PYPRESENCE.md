# 📚 pypresence - Discord Rich Presence pour Workly

## 🎯 Qu'est-ce que pypresence ?

**pypresence** est une bibliothèque Python moderne qui permet d'afficher une **Rich Presence** (présence enrichie) sur Discord. C'est un **wrapper Python** qui communique avec le client Discord de l'utilisateur pour afficher des informations personnalisées sur son profil.

### Exemple visuel

```
┌─────────────────────────────┐
│ 👤 Profil Discord           │
├─────────────────────────────┤
│ 🎮 En train d'utiliser      │
│    Workly Assistant         │
│                             │
│ 💬 Discute avec son avatar  │
│ ⏱️  Depuis 15 minutes       │
│                             │
│ [🔗 Rejoindre] [👁️ Voir]   │
└─────────────────────────────┘
```

---

## 🔧 Installation

```powershell
# Dans ton environnement virtuel Workly
cd c:\Dev\workly_project\workly-desktop
.\venv\Scripts\Activate.ps1
pip install pypresence
```

---

## 💻 Utilisation basique

```python
from pypresence import Presence
import time

# 1. Créer une connexion (besoin d'un Client ID Discord)
client_id = '123456789012345678'  # À obtenir sur Discord Developer Portal
RPC = Presence(client_id)
RPC.connect()

# 2. Mettre à jour la présence
RPC.update(
    state="Discute avec Mura",           # Ligne du bas
    details="Avatar VRM actif",          # Ligne du haut
    start=int(time.time()),              # Temps écoulé depuis maintenant
    large_image="workly_logo",           # Grande image (à uploader sur Discord)
    large_text="Workly - Assistant AI",  # Texte au survol de l'image
    small_image="vrm_avatar",            # Petite image en overlay
    small_text="Modèle VRM",             # Texte au survol
    buttons=[
        {"label": "Télécharger Workly", "url": "https://workly.ai"},
        {"label": "En savoir plus", "url": "https://github.com/WorklyHQ"}
    ]
)

# 3. Garder la connexion active
time.sleep(60)  # La présence reste affichée

# 4. Déconnecter proprement
RPC.close()
```

---

## 🎨 Paramètres disponibles

| Paramètre | Description | Exemple |
|-----------|-------------|---------|
| `state` | Texte en bas (sous-titre) | "En conversation" |
| `details` | Texte en haut (titre) | "Utilise Workly Assistant" |
| `start` | Timestamp de début (affiche "depuis X min") | `int(time.time())` |
| `end` | Timestamp de fin (compte à rebours) | `int(time.time()) + 3600` |
| `large_image` | Nom de la grande image | "workly_logo" |
| `large_text` | Texte au survol | "Workly v0.8" |
| `small_image` | Petite image (badge) | "status_active" |
| `small_text` | Texte au survol | "En ligne" |
| `party_id` | ID de groupe (pour rejoindre) | "party_123" |
| `party_size` | Taille du groupe | `[1, 4]` (1/4) |
| `buttons` | Liste de boutons cliquables | `[{"label": "...", "url": "..."}]` |

---

## 🚀 Intégration dans Workly

### Architecture proposée

```
workly-desktop/
├── src/
│   ├── discord_presence.py    ← Nouveau module
│   └── ...
├── data/
│   └── config.json            ← Ajouter config Discord
└── main.py                    ← Intégrer au démarrage
```

### Code d'implémentation

#### 1. Module Discord (`src/discord_presence.py`)

```python
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
            # Paramètres par défaut
            update_params = {
                "state": state or "Idle",
                "details": details or "Avatar VRM actif",
                "start": self.start_time,
                "large_image": kwargs.get("large_image", "workly_logo"),
                "large_text": kwargs.get("large_text", "Workly - Assistant Virtuel"),
                "small_image": kwargs.get("small_image", "vrm_active"),
                "small_text": kwargs.get("small_text", "En ligne"),
            }

            # Ajouter les boutons si présents
            if "buttons" in kwargs:
                update_params["buttons"] = kwargs["buttons"]
            else:
                update_params["buttons"] = [
                    {"label": "En savoir plus", "url": "https://github.com/WorklyHQ"}
                ]

            self.rpc.update(**update_params)
            self.logger.debug(f"📡 Discord RPC mis à jour: {state}")

        except Exception as e:
            self.logger.error(f"❌ Erreur mise à jour Discord: {e}")
            self.connected = False

    def set_conversation_status(self, avatar_name: str):
        """
        Affiche que l'utilisateur parle avec son avatar

        Args:
            avatar_name: Nom de l'avatar
        """
        self.update_status(
            state=f"Discute avec {avatar_name}",
            details="💬 En conversation",
            small_image="status_talking",
            small_text="En conversation"
        )

    def set_idle_status(self):
        """Affiche que l'avatar est inactif"""
        self.update_status(
            state="Avatar en attente",
            details="😴 Idle",
            small_image="status_idle",
            small_text="Inactif"
        )

    def set_listening_status(self):
        """Affiche que l'avatar écoute"""
        self.update_status(
            state="Écoute l'utilisateur",
            details="🎤 En écoute",
            small_image="status_listening",
            small_text="En écoute"
        )

    def set_thinking_status(self):
        """Affiche que l'avatar réfléchit"""
        self.update_status(
            state="Génère une réponse",
            details="🤔 En réflexion",
            small_image="status_thinking",
            small_text="En train de réfléchir"
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
            "neutral": "😐"
        }

        emoji = expression_emoji.get(expression.lower(), "😊")
        self.update_status(
            state=f"Expression: {expression}",
            details=f"{emoji} Avatar expressif",
            small_image=f"expression_{expression}",
            small_text=f"Expression: {expression}"
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
```

#### 2. Configuration (`data/config.json`)

Ajouter cette section dans le fichier de configuration :

```json
{
  "discord": {
    "enabled": true,
    "client_id": "TON_CLIENT_ID_ICI"
  }
}
```

#### 3. Intégration dans `main.py`

```python
# Imports
from src.discord_presence import WorklyDiscordPresence

# Dans la classe principale ou au démarrage
def __init__(self):
    # ... autres initialisations ...

    # Discord Rich Presence
    self.discord = None
    if self.config.get("discord", {}).get("enabled", False):
        client_id = self.config["discord"]["client_id"]
        self.discord = WorklyDiscordPresence(client_id)
        if self.discord.connect():
            self.discord.set_idle_status()

# Lors des changements d'état
def on_conversation_start(self, avatar_name: str):
    if self.discord:
        self.discord.set_conversation_status(avatar_name)

def on_listening(self):
    if self.discord:
        self.discord.set_listening_status()

def on_thinking(self):
    if self.discord:
        self.discord.set_thinking_status()

def on_expression_change(self, expression: str):
    if self.discord:
        self.discord.set_expression_status(expression)

def on_idle(self):
    if self.discord:
        self.discord.set_idle_status()

# À la fermeture
def cleanup(self):
    if self.discord:
        self.discord.disconnect()
```

---

## 📋 Étapes de configuration Discord

### 1. Créer une application Discord

1. Va sur https://discord.com/developers/applications
2. Clique sur **"New Application"**
3. Nomme-la **"Workly"**
4. Note le **Client ID** (sous "General Information")

### 2. Uploader les images (Rich Presence Assets)

1. Dans ton application Discord, va dans **"Rich Presence" → "Art Assets"**
2. Upload les images suivantes (format PNG, 512x512 minimum) :

| Nom de l'asset | Description | Usage |
|----------------|-------------|-------|
| `workly_logo` | Logo principal de Workly | Grande image |
| `vrm_active` | Icône avatar VRM actif | Petite image (idle) |
| `status_talking` | Icône conversation | Petite image (conversation) |
| `status_listening` | Icône micro/écoute | Petite image (écoute) |
| `status_thinking` | Icône cerveau/réflexion | Petite image (génération) |
| `status_idle` | Icône sommeil/inactif | Petite image (idle) |
| `expression_joy` | Émoji joyeux | Expressions |
| `expression_sad` | Émoji triste | Expressions |
| `expression_angry` | Émoji en colère | Expressions |

### 3. Configurer dans Workly

Dans `workly-desktop/data/config.json` :

```json
{
  "discord": {
    "enabled": true,
    "client_id": "123456789012345678"
  }
}
```

---

## ✅ Avantages de pypresence

- **✅ 100% Python** : S'intègre parfaitement avec le code Workly
- **✅ Moderne** : Toujours maintenu (contrairement à discord-rpc C++)
- **✅ Simple** : API claire et intuitive
- **✅ Robuste** : Ne plante pas si Discord n'est pas ouvert
- **✅ Léger** : Aucune dépendance lourde (pas de C++ à compiler)
- **✅ Multiplateforme** : Windows, macOS, Linux
- **✅ Thread-safe** : Compatible avec l'architecture asynchrone de Workly

---

## 🎭 Cas d'usage pour Workly

Tu pourrais afficher :

| État de Workly | Discord Presence |
|----------------|------------------|
| **Démarrage** | "Initialisation de l'avatar" |
| **Idle** | "Avatar en attente 😴" |
| **Écoute** | "Écoute l'utilisateur 🎤" |
| **Réflexion** | "Génère une réponse 🤔" |
| **Conversation** | "Discute avec Mura 💬" |
| **Expression** | "Expression: Joy 😊" |
| **Animation** | "Animation en cours 🎬" |
| **Stats** | "127 conversations aujourd'hui 📊" |

---

## 🔗 Ressources

- **Documentation pypresence** : https://github.com/qwertyquerty/pypresence
- **Discord Developer Portal** : https://discord.com/developers/applications
- **Discord Rich Presence Docs** : https://discord.com/developers/docs/rich-presence/how-to
- **PyPI pypresence** : https://pypi.org/project/pypresence/

---

## ⚠️ Notes importantes

### Pourquoi pypresence et pas discord-rpc ?

**discord-rpc** (le dépôt officiel Discord en C++) est **DÉPRÉCIÉ** depuis 2018 :
- ❌ Dernière release : novembre 2018 (il y a 7 ans)
- ❌ Discord recommande GameSDK à la place
- ❌ Nécessite compilation C++
- ❌ Difficile à intégrer avec Python

**pypresence** est la solution moderne :
- ✅ Toujours maintenu activement
- ✅ Pure Python (pas de compilation)
- ✅ API simple et pythonique
- ✅ Communauté active

### Gestion des erreurs

Le module `WorklyDiscordPresence` gère automatiquement :
- Discord non ouvert → Log warning, continue sans planter
- Perte de connexion → Reconnexion automatique possible
- Erreurs de mise à jour → Log error, continue l'exécution

---

## 🚀 Prochaines étapes

1. **Phase 1** : Implémentation basique
   - Connexion Discord au démarrage
   - Statut idle par défaut
   - Déconnexion à la fermeture

2. **Phase 2** : États dynamiques
   - Mise à jour selon l'état de l'avatar
   - Expressions faciales
   - Temps écoulé

3. **Phase 3** : Fonctionnalités avancées
   - Statistiques (nombre de conversations)
   - Boutons personnalisés
   - Party mode (multi-utilisateurs ?)

---

**🎭 Workly x Discord = Présence sociale pour ton assistant virtuel ! 🚀**
