# 🔧 Troubleshooting - Chat 12

Guide de résolution des problèmes rencontrés pendant le Chat 12.

---

## 🐛 Problème 1 : Performances IA Extrêmement Lentes (51s par réponse)

### Symptômes
- Réponses IA prennent 40-60 secondes au lieu de ~2 secondes
- Logs montrent : "Profil GPU auto-détecté : 'performance' (RTX 4050, 6.0 GB VRAM)"
- Configuration correcte : `gpu_layers=-1`, profil `performance`
- Utilisateur note : "Le modèle est lancé sur la ram et pas la vram"

### Diagnostic

**Test 1 : Vérifier CUDA disponibilité**
```powershell
cd c:\Dev\workly_project\workly-desktop
.\venv\Scripts\Activate.ps1
python -c "from llama_cpp import Llama; print('CUDA available:', hasattr(Llama, 'n_gpu_layers'))"
```

**Résultat attendu** : `CUDA available: True`
**Si False** → llama-cpp-python installé sans support CUDA

### Cause Racine
`llama-cpp-python` installé en version CPU-only (sans CUDA), probablement parce que :
1. Installation initiale sans variable d'environnement `CMAKE_ARGS="-DLLAMA_CUDA=on"`
2. Cache pip gardait l'ancienne version
3. Wheels précompilés CPU-only installés par défaut

### Solution

**Étape 1 : Activer environnement virtuel**
```powershell
cd c:\Dev\workly_project\workly-desktop
.\venv\Scripts\Activate.ps1
```

**Étape 2 : Réinstaller avec support CUDA**
```powershell
$env:CMAKE_ARGS="-DLLAMA_CUDA=on"
$env:FORCE_CMAKE="1"
pip install llama-cpp-python --force-reinstall --no-cache-dir --verbose
```

**⚠️ Durée** : ~15-20 minutes (compilation complète)

**Étape 3 : Vérifier installation**
```powershell
python -c "from llama_cpp import Llama; print('CUDA available:', hasattr(Llama, 'n_gpu_layers'))"
```

**Résultat attendu** : `CUDA available: True`

**Étape 4 : Relancer l'application**
```powershell
.\venv\Scripts\python.exe main.py
```

**Vérification** : Temps de réponse doit passer de ~51s à ~2s

### Prérequis

**Pour que CUDA fonctionne** :
1. ✅ GPU NVIDIA compatible (GTX 10xx ou plus récent)
2. ✅ Drivers NVIDIA à jour (Game Ready ou Studio)
3. ✅ CUDA Toolkit 11.x ou 12.x (souvent inclus dans drivers)
4. ✅ Visual Studio Build Tools (pour compilation)

**Vérifier drivers NVIDIA** :
```powershell
nvidia-smi
```

### Prévention Future

**Pour distribution publique** :
- Wheels précompilés officiels incluent déjà CUDA support
- Utilisateurs n'auront besoin que de drivers NVIDIA à jour
- Système de profils GPU auto-détecte et configure automatiquement

**Pour développement local** :
- Toujours installer avec `CMAKE_ARGS="-DLLAMA_CUDA=on"`
- Documenter prérequis dans README.md
- Ajouter section "Installation GPU" dans documentation

---

## 🐛 Problème 2 : Auto-Reply Discord Ne Fonctionne Pas

### Symptômes
- Logs montrent : `KiraDiscordBot initialisé (auto_reply=False, channels=1)`
- Salons configurés dans interface mais bot ne répond pas
- `config.json` contient bien `auto_reply_enabled: true`

### Diagnostic

**Vérifier config.json** :
```json
"discord": {
    "auto_reply_enabled": true,
    "auto_reply_channels": [123456789012345678],
    "rate_limit_seconds": 3
}
```

**Vérifier logs bot** :
```
INFO:src.discord_bot.bot:✅ KiraDiscordBot initialisé (auto_reply=False, channels=1)
```

→ **Incohérence** : Config dit `true`, bot lit `False`

### Cause Racine

**3 problèmes identifiés** :

1. **Pas de contrôle UI** : Interface n'avait pas de checkbox pour activer/désactiver auto-reply
2. **Config non rechargée** : Bot démarre avec config initiale, jamais rechargée après modifications
3. **Sauvegarde incomplète** : Interface ne sauvegardait pas `auto_reply_enabled`, seulement les IDs salons

### Solution

**Modifications apportées dans `src/gui/app.py`** :

**1. Ajout checkbox dans dialog** :
```python
# manage_auto_reply_channels()
enable_checkbox = QCheckBox("✅ Activer l'auto-reply dans les salons configurés")
enable_checkbox.setChecked(auto_reply_enabled)
```

**2. Modification _save_channels()** :
```python
def _save_channels(self, list_widget, enable_checkbox, dialog):
    # Récupérer état checkbox
    auto_reply_enabled = enable_checkbox.isChecked()

    # Sauvegarder dans config
    self.config.set("discord.auto_reply_enabled", auto_reply_enabled)
    self.config.set("discord.auto_reply_channels", auto_reply_channels)

    # Recharger config du bot EN TEMPS RÉEL (CRUCIAL!)
    if self.discord_manager and self.discord_manager.bot:
        self.discord_manager.bot.auto_reply_enabled = auto_reply_enabled
        self.discord_manager.bot.auto_reply_channels = auto_reply_channels
```

### Utilisation

**Après fix** :

1. Ouvrir Discord → Gérer Salons Auto-Reply
2. ✅ **Cocher** "Activer l'auto-reply dans les salons configurés"
3. Ajouter IDs des salons (Copier ID depuis Discord)
4. Cliquer "OK"
5. **Pas besoin de redémarrer l'app !** Config rechargée automatiquement

**Vérification** :
```
✅ Config Discord sauvegardée : auto_reply=True, 1 salons
✅ Config bot Discord rechargée : auto_reply=True, 1 salons
```

### Obtenir l'ID d'un salon Discord

1. Discord → Paramètres → Avancés → **Activer Mode Développeur**
2. Clic droit sur le salon → **Copier l'identifiant**
3. Coller l'ID dans l'interface Workly

**Format ID** : Nombre à 18 chiffres (ex: `1234567890123456789`)

### Tester Auto-Reply

**Configuration minimale** :
1. ✅ Bot Discord démarré (onglet Discord)
2. ✅ Auto-reply activée (checkbox cochée)
3. ✅ Au moins 1 salon configuré avec ID valide
4. ✅ Bot a accès au salon sur Discord

**Test** :
1. Envoyer un message dans le salon configuré
2. Bot doit répondre automatiquement
3. Rate limit : 3 secondes entre réponses par utilisateur

**Si ne fonctionne pas** :
- Vérifier logs onglet 📋 Logs
- Vérifier permissions bot Discord (lecture/écriture messages)
- Vérifier ID salon correct (18 chiffres)

---

## 📋 Checklist de Diagnostic Général

### Avant de Débugger

**Vérifier logs** :
1. Ouvrir onglet 📋 Logs dans l'application
2. Chercher messages ERROR (rouge) ou WARNING (orange)
3. Noter le module et le message d'erreur

**Vérifier configuration** :
1. Fichier `data/config.json` existe
2. Permissions lecture/écriture OK
3. Format JSON valide (pas d'erreur syntax)

**Vérifier environnement** :
```powershell
# Activer venv
.\venv\Scripts\Activate.ps1

# Vérifier Python
python --version  # Doit être 3.10+

# Vérifier packages critiques
pip show llama-cpp-python
pip show PySide6
pip show discord.py
```

### Problèmes Courants

**IA ne charge pas** :
- ✅ Fichier modèle existe dans `models/` ?
- ✅ GPU détecté ? (Vérifier label profil GPU)
- ✅ VRAM suffisante ? (6GB recommandé pour Zephyr-7B)
- ✅ Profil GPU adapté ? (Essayer "Auto")

**Discord bot ne démarre pas** :
- ✅ Token Discord valide dans `.env` ?
- ✅ Permissions bot Discord correctes ?
- ✅ Bot invité sur le serveur Discord ?
- ✅ Intents activés (Message Content Intent) ?

**Performance lente** :
- ✅ CUDA disponible ? (Test ci-dessus)
- ✅ Profil GPU = Performance ou Auto ?
- ✅ GPU layers = -1 (toutes les layers sur GPU) ?
- ✅ Pas de processus gourmand en background ?

---

## 🔗 Ressources

**Documentation** :
- [CURRENT_STATE.md](CURRENT_STATE.md) : État actuel du projet
- [CHANGELOG.md](../../CHANGELOG.md) : Historique versions
- [llama-cpp-python CUDA](https://github.com/abetlen/llama-cpp-python#installation-with-hardware-acceleration) : Installation GPU officielle

**Support** :
- Discord Workly : https://discord.gg/3Cpyxg29B4
- Issues GitHub : https://github.com/WorklyHQ/workly-desktop/issues
