# 🚀 Guide de Démarrage Rapide - Desktop-Mate

Ce guide te permettra de démarrer le projet Desktop-Mate en quelques minutes !

## ✅ Prérequis Vérifiés

- [x] **Python 3.10.9** installé et fonctionnel
- [x] **Git** pour le versioning
- [x] **Unity Hub** (à installer pour la phase Unity)

## 📦 Ce qui a été créé

### Structure du Projet
```
desktop-mate/
├── 📄 main.py                    # Point d'entrée de l'application
├── 📋 requirements.txt           # Dépendances Python (installées ✓)
├── 📖 README.md                  # Documentation principale
├── 📜 LICENSE                    # Licence MIT
├── 🙈 .gitignore                 # Fichiers à ignorer par Git
├── 🤝 CONTRIBUTING.md            # Guide de contribution
│
├── 🐍 venv/                      # Environnement virtuel Python ✓
│
├── 📂 src/                       # Code source Python
│   ├── gui/                      # Interface Qt (PySide6)
│   │   └── app.py                # Application principale
│   ├── ipc/                      # Communication Unity ↔ Python
│   │   └── unity_bridge.py       # Bridge socket
│   ├── audio/                    # Module audio (à développer)
│   ├── avatar/                   # Gestion avatar (à développer)
│   └── utils/                    # Utilitaires
│       ├── config.py             # Gestionnaire de configuration
│       └── logger.py             # Système de logs
│
├── 🎮 unity/                     # Projet Unity (à créer)
│   └── README.md                 # Instructions Unity
│
├── 📚 docs/                      # Documentation
│   └── architecture.md           # Architecture technique
│
├── ✅ tests/                     # Tests unitaires (8 tests passent ✓)
│   ├── test_config.py
│   └── test_unity_bridge.py
│
└── 🔧 .github/                   # CI/CD
    └── workflows/
        └── python-ci.yml         # GitHub Actions
```

## 🎯 État Actuel du Projet

### ✅ Fait
- [x] Structure complète du projet
- [x] Environnement virtuel Python créé
- [x] Dépendances installées (PySide6, pytest, etc.)
- [x] Application Qt de base fonctionnelle
- [x] Système de communication IPC (socket)
- [x] Configuration et logging
- [x] Tests unitaires (8/8 passent)
- [x] CI/CD configurée (GitHub Actions)
- [x] Documentation complète

### 🔨 À Faire Ensuite (Prochaines Étapes)

#### Étape 1 : Tester l'Application Python (MAINTENANT)
```powershell
# Activer le venv
.\venv\Scripts\Activate.ps1

# Lancer l'application
python main.py
```

**Résultat attendu** : Une fenêtre Qt s'ouvre avec le panneau de contrôle Desktop-Mate.

#### Étape 2 : Créer le Projet Unity
1. Installer **Unity Hub** : https://unity.com/download
2. Installer **Unity 2022.3 LTS** via Unity Hub
3. Suivre les instructions dans `unity/README.md`

#### Étape 3 : Implémenter la Communication Unity
- Créer `PythonBridge.cs` dans Unity
- Établir la connexion socket
- Tester la communication bidirectionnelle

#### Étape 4 : Charger un Modèle VRM
- Installer UniVRM dans Unity
- Charger `assets/Mura Mura - Model.vrm`
- Afficher le modèle dans la scène

## 🛠️ Commandes Utiles

### Python

```powershell
# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# Lancer l'application
python main.py

# Lancer les tests
pytest tests/ -v

# Lancer les tests avec couverture
pytest tests/ --cov=src --cov-report=html

# Formater le code
black src/ tests/

# Vérifier le linting
flake8 src/ tests/

# Vérifier les types
mypy src/
```

### Git

```powershell
# Initialiser le repo (si pas encore fait)
git init
git add .
git commit -m "feat: initial project setup"

# Ajouter l'origine remote
git remote add origin https://github.com/Xyon15/desktop-mate.git
git push -u origin main
```

## 📖 Documentation Disponible

| Fichier | Description |
|---------|-------------|
| `README.md` | Documentation principale du projet |
| `CONTRIBUTING.md` | Guide pour contribuer au projet |
| `docs/architecture.md` | Architecture technique détaillée |
| `unity/README.md` | Instructions pour Unity |

## 🐛 Résolution de Problèmes

### L'application ne démarre pas
```powershell
# Vérifier que le venv est activé
.\venv\Scripts\Activate.ps1

# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

### Erreur d'import
```powershell
# Vérifier que vous êtes dans le bon dossier
cd C:\Dev\desktop-mate

# Vérifier la version Python
python --version  # Doit être 3.10+
```

### Tests échouent
```powershell
# Nettoyer le cache
pytest --cache-clear

# Réinstaller pytest
pip install pytest pytest-cov --force-reinstall
```

## 🎓 Apprendre en Développant

### Concepts Clés à Comprendre

1. **Architecture Hybride** : Python gère la logique, Unity gère le rendu
2. **IPC (Inter-Process Communication)** : Communication via sockets TCP
3. **Qt/PySide6** : Framework GUI pour l'interface
4. **VRM** : Format de modèle 3D pour avatars
5. **Blendshapes** : Déformations pour expressions faciales

### Ressources

- [Documentation PySide6](https://doc.qt.io/qtforpython/)
- [Documentation Unity](https://docs.unity3d.com/)
- [Spécification VRM](https://github.com/vrm-c/vrm-specification)
- [UniVRM](https://github.com/vrm-c/UniVRM)

## 🎯 Objectifs par Phase

### Phase 1 : MVP Minimal (2-4 semaines)
- [ ] Application Python fonctionnelle
- [ ] Unity charge et affiche un VRM
- [ ] Communication IPC établie
- [ ] Commande simple de chargement de modèle

### Phase 2 : Audio & Lip-Sync (2-3 semaines)
- [ ] Capture audio microphone
- [ ] Traitement amplitude
- [ ] Synchronisation bouche basique
- [ ] UI avec VU-meter

### Phase 3 : Expressions (2-3 semaines)
- [ ] Contrôle blendshapes depuis UI
- [ ] Émotions prédéfinies
- [ ] Transitions fluides
- [ ] Présets sauvegardables

## 💡 Prochaine Action Suggérée

**MAINTENANT** : Lance l'application pour voir le résultat !

```powershell
.\venv\Scripts\Activate.ps1
python main.py
```

Si tout fonctionne, tu verras une fenêtre Qt avec :
- Un titre "Desktop-Mate Control Panel"
- Un statut de connexion Unity
- Des boutons pour se connecter et charger un modèle

**Note** : Unity n'est pas encore configuré, donc la connexion échouera pour l'instant. C'est normal ! 😊

## 🎉 Félicitations !

Tu as maintenant un projet **Desktop-Mate** complètement configuré et prêt à être développé !

**Questions ?** N'hésite pas à ouvrir une issue sur GitHub ou à consulter la documentation.

Bon développement ! 🚀
