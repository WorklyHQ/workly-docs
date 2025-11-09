# 🔧 Menu Options - Configuration Discord GUI

**Date** : 24 octobre 2025  
**Amélioration** : Ajout menu "Options" pour configuration Discord facile

---

## 📋 Vue d'Ensemble

Suite à la simplification de l'interface Discord (suppression section configuration redondante), un **menu "Options"** a été ajouté pour permettre de **configurer facilement** le token Discord et les salons auto-reply **directement depuis la GUI**.

### Problème Résolu

Après simplification, la configuration Discord nécessitait :
- ❌ Éditer manuellement le fichier `.env` pour le token
- ❌ Éditer manuellement `data/config.json` pour les salons
- ❌ Redémarrer l'application pour appliquer les changements

**Erreur typique** :
```
ERROR:src.gui.app:❌ Erreur Discord : Improper token has been passed.
```

→ Cause : `.env` non chargé ou token invalide

### Solution Implémentée

**Menu "Options"** entre "Fichier" et "Aide" avec 2 sous-menus :
1. ✅ **"Définir Token Bot Discord..."** → Dialog pour sauvegarder token dans `.env`
2. ✅ **"Gérer Salons Auto-Reply..."** → Dialog pour gérer liste salons dans `config.json`

---

## 🏗️ Architecture Technique

### 1. Chargement `.env` au Démarrage

**Ajout dans `src/gui/app.py`** (ligne ~19) :

```python
# Load .env file at startup
from dotenv import load_dotenv
load_dotenv()
```

✅ **Effet** : Toutes les variables du fichier `.env` sont chargées dans `os.environ` au lancement de l'application.

### 2. Menu "Options" (Menu Bar)

**Emplacement** : `create_menu_bar()` (ligne ~1420)

```python
# Options menu
options_menu = menubar.addMenu("Options")

# Discord bot configuration
set_token_action = options_menu.addAction("Définir Token Bot Discord...")
set_token_action.triggered.connect(self.set_discord_token)

manage_channels_action = options_menu.addAction("Gérer Salons Auto-Reply...")
manage_channels_action.triggered.connect(self.manage_auto_reply_channels)
```

### 3. Dialog Token Discord

**Méthode** : `set_discord_token()` (ligne ~730)

**Fonctionnalités** :
- QInputDialog avec mode **Password** (masque le token)
- Récupère le token actuel depuis `os.getenv("DISCORD_TOKEN")`
- Sauvegarde dans `.env` (mise à jour ou ajout)
- Met à jour `os.environ["DISCORD_TOKEN"]` immédiatement
- Affiche message de confirmation

**Code clé** :

```python
def set_discord_token(self):
    """Open dialog to set Discord bot token."""
    current_token = os.getenv("DISCORD_TOKEN", "")
    
    token, ok = QInputDialog.getText(
        self,
        "Définir Token Bot Discord",
        "Entrez le token Discord de votre bot :\n\n"
        "(Le token sera sauvegardé dans le fichier .env)",
        QLineEdit.EchoMode.Password,
        current_token
    )
    
    if ok and token.strip():
        # Save to .env file
        env_path = Path(__file__).parent.parent.parent / ".env"
        
        # ... lecture/écriture .env ...
        
        # Update environment variable
        os.environ["DISCORD_TOKEN"] = token.strip()
        
        QMessageBox.information(
            self,
            "Token Sauvegardé",
            "Le token Discord a été sauvegardé avec succès !"
        )
```

### 4. Dialog Salons Auto-Reply

**Méthode** : `manage_auto_reply_channels()` (ligne ~783)

**Fonctionnalités** :
- QDialog avec QListWidget pour afficher salons
- Charge les salons depuis `self.config.get("discord.auto_reply_channels")`
- Boutons "➕ Ajouter Salon" et "➖ Retirer Salon"
- Validation ID (doit être un nombre)
- Sauvegarde dans `data/config.json` via `self.config.set()`
- Affiche nombre de salons configurés

**Code clé** :

```python
def manage_auto_reply_channels(self):
    """Open dialog to manage Discord auto-reply channels."""
    dialog = QDialog(self)
    dialog.setWindowTitle("Gérer Salons Auto-Reply Discord")
    
    # ... création UI ...
    
    channels_list = QListWidget()
    
    # Load current channels from config
    auto_reply_channels = self.config.get("discord.auto_reply_channels", [])
    for channel_id in auto_reply_channels:
        channels_list.addItem(str(channel_id))
    
    # ... boutons add/remove ...
    
    button_box.accepted.connect(lambda: self._save_channels(channels_list, dialog))
    
    dialog.exec()

def _save_channels(self, list_widget, dialog):
    """Save channels to config.json."""
    auto_reply_channels = []
    for i in range(list_widget.count()):
        item = list_widget.item(i)
        auto_reply_channels.append(int(item.text()))
    
    self.config.set("discord.auto_reply_channels", auto_reply_channels)
    self.config.save()
    
    QMessageBox.information(
        self,
        "Configuration Sauvegardée",
        f"Nombre de salons configurés : {len(auto_reply_channels)}"
    )
```

---

## 🎯 Guide Utilisateur

### Configurer le Token Discord

**Étape 1 : Obtenir le Token**

1. Aller sur [Discord Developer Portal](https://discord.com/developers/applications)
2. Sélectionner votre application (ou en créer une)
3. Onglet **"Bot"** → Section **"Token"**
4. Cliquer sur **"Reset Token"** ou **"Copy"**

**Étape 2 : Définir le Token dans Desktop-Mate**

1. Lancer Desktop-Mate : `python main.py`
2. Menu : **Options → Définir Token Bot Discord...**
3. Coller le token dans le dialog (masqué avec mode password)
4. Cliquer **"OK"**
5. Message de confirmation : ✅ "Token sauvegardé avec succès !"

**Résultat** : Le token est sauvegardé dans `.env` et prêt à être utilisé.

### Configurer les Salons Auto-Reply

**Étape 1 : Activer Mode Développeur Discord**

1. Discord → **Paramètres Utilisateur** → **Avancés**
2. Activer **"Mode Développeur"**

**Étape 2 : Copier IDs des Salons**

1. Clic droit sur un salon → **"Copier l'identifiant"**
2. Répéter pour chaque salon où le bot doit répondre automatiquement

**Étape 3 : Configurer dans Desktop-Mate**

1. Lancer Desktop-Mate : `python main.py`
2. Menu : **Options → Gérer Salons Auto-Reply...**
3. Cliquer **"➕ Ajouter Salon"**
4. Coller l'ID du salon (ex: `1234567890123456789`)
5. Cliquer **"OK"**
6. Répéter pour chaque salon
7. Cliquer **"OK"** pour sauvegarder

**Résultat** : Les salons sont sauvegardés dans `data/config.json`.

### Démarrer le Bot Discord

**Workflow complet** :

1. ✅ **Configurer Token** (Options → Définir Token)
2. ✅ **Configurer Salons** (Options → Gérer Salons Auto-Reply)
3. ✅ **Charger IA** (Onglet "Connexion" → "Charger IA")
4. ✅ **Démarrer Bot** (Onglet "🤖 Discord" → "▶️ Démarrer Bot Discord")
5. ✅ **Vérifier Statut** : 🟢 Connecté : Kira#1234

---

## 📊 Tests

### Tests Unitaires

**Fichier** : `tests/test_gui_discord.py`  
**Résultat** : ✅ **14/14 tests passent**

```powershell
pytest tests/test_gui_discord.py -v
# ✅ 14 passed, 1 warning in 1.31s
```

**Tests impactés** :
- `test_start_discord_bot_without_token` → Mock `os.getenv()` pour simuler token manquant
- Aucun nouveau test nécessaire (dialogs = interactions manuelles)

### Tests Manuels

**À tester** :

1. ✅ **Menu Options existe** entre "Fichier" et "Aide"
2. ✅ **Dialog Token** :
   - S'ouvre correctement
   - Mode password masque le token
   - Sauvegarde dans `.env`
   - Message de confirmation affiché
3. ✅ **Dialog Salons** :
   - S'ouvre correctement
   - Liste affiche salons existants
   - Ajout salon fonctionne (validation ID)
   - Suppression salon fonctionne
   - Sauvegarde dans `config.json`
   - Message confirmation avec nombre salons
4. ✅ **Connexion Bot** :
   - Token chargé depuis `.env`
   - Bot se connecte avec token valide
   - Statut 🟢 affiché si connexion réussie
   - Erreur claire si token invalide

---

## 🔧 Fichiers Modifiés

### `src/gui/app.py` (~250 lignes ajoutées)

**Imports ajoutés** :
```python
import os
from dotenv import load_dotenv
from PySide6.QtWidgets import (
    QInputDialog, QListWidget, QListWidgetItem, QDialog, QDialogButtonBox
)
```

**Méthodes ajoutées** :
- `set_discord_token()` (ligne ~730, ~70 lignes)
- `manage_auto_reply_channels()` (ligne ~783, ~90 lignes)
- `_add_channel_to_list()` (ligne ~869, ~20 lignes)
- `_remove_channel_from_list()` (ligne ~889, ~15 lignes)
- `_save_channels()` (ligne ~902, ~30 lignes)

**Menu modifié** :
- `create_menu_bar()` → Ajout menu "Options" avec 2 actions

---

## ✅ Avantages de cette Amélioration

### 1. **Facilité d'Utilisation**
- ✅ Configuration via GUI (plus besoin d'éditer manuellement `.env` et `config.json`)
- ✅ Dialogs intuitifs avec instructions claires
- ✅ Validation des entrées (ID salons doivent être numériques)

### 2. **Sécurité**
- ✅ Token masqué avec mode **Password** dans le dialog
- ✅ Token sauvegardé dans `.env` (non versionné)
- ✅ Pas de risque d'erreur de syntaxe dans `.env`

### 3. **Cohérence**
- ✅ Menu "Options" = standard pour configurations applicatives
- ✅ Workflow unifié : tout se configure depuis la GUI
- ✅ Messages de confirmation/erreur clairs

### 4. **Robustesse**
- ✅ Chargement `.env` avec `python-dotenv` (standard Python)
- ✅ Gestion d'erreurs complète (fichier non trouvé, erreurs I/O)
- ✅ Validation des IDs salons avant sauvegarde

---

## 🔄 Comparaison Avant/Après

### Avant (Configuration Manuelle)

**Définir Token** :
```powershell
# Éditer .env manuellement
notepad .env
# Ajouter : DISCORD_TOKEN=MTEyMzQ1...
```

**Définir Salons** :
```powershell
# Éditer config.json manuellement
notepad data/config.json
# Modifier : "auto_reply_channels": [123...]
```

→ ❌ Erreur de syntaxe possible  
→ ❌ Redémarrage nécessaire  
→ ❌ Pas de validation

### Après (Menu Options GUI)

**Définir Token** :
1. Options → Définir Token Bot Discord...
2. Coller token → OK
3. ✅ Sauvegardé !

**Définir Salons** :
1. Options → Gérer Salons Auto-Reply...
2. Ajouter IDs → OK
3. ✅ Sauvegardé !

→ ✅ Pas d'erreur de syntaxe  
→ ✅ Application immédiate  
→ ✅ Validation automatique

---

## 🎊 Conclusion

Le **menu "Options"** complète l'interface Discord de Desktop-Mate en offrant une **configuration facile et sécurisée** du token et des salons auto-reply.

**L'utilisateur peut maintenant** :
- ✅ Configurer Discord **entièrement depuis la GUI**
- ✅ Voir le token actuel (masqué) et le modifier facilement
- ✅ Gérer la liste des salons avec ajout/suppression intuitifs
- ✅ Démarrer le bot sans éditer manuellement les fichiers

**Desktop-Mate dispose d'une interface Discord complète et conviviale !** 🤖🔧✨
