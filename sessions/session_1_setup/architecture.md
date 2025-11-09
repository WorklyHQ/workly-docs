# Architecture de Desktop-Mate

## Vue d'ensemble

Desktop-Mate utilise une architecture hybride combinant **Unity** pour le rendu 3D et **Python** pour la logique applicative.

## Diagramme d'architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DESKTOP-MATE SYSTEM                      │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┐                  ┌──────────────────────┐
│   PYTHON LAYER       │                  │   UNITY LAYER        │
│  (Logic & Control)   │                  │  (Rendering)         │
│                      │                  │                      │
│  ┌────────────────┐  │                  │  ┌────────────────┐  │
│  │   GUI (Qt)     │  │                  │  │  VRM Renderer  │  │
│  │  • Main Window │  │                  │  │  • Model Load  │  │
│  │  • Controls    │  │                  │  │  • Animations  │  │
│  │  • Settings    │  │                  │  │  • Blendshapes │  │
│  └────────────────┘  │                  │  └────────────────┘  │
│          │           │                  │          ▲           │
│          ▼           │                  │          │           │
│  ┌────────────────┐  │    Socket IPC    │  ┌────────────────┐  │
│  │   IPC Bridge   │◄─┼──────────────────┼─►│  Socket Server │  │
│  │  • Commands    │  │   (TCP/JSON)     │  │  • Listener    │  │
│  │  • Responses   │  │                  │  │  • Handler     │  │
│  └────────────────┘  │                  │  └────────────────┘  │
│          │           │                  │                      │
│          ▼           │                  │                      │
│  ┌────────────────┐  │                  │                      │
│  │  Audio Module  │  │                  │                      │
│  │  • Microphone  │  │                  │                      │
│  │  • Processing  │  │                  │                      │
│  │  • Lip Sync    │  │                  │                      │
│  └────────────────┘  │                  │                      │
│          │           │                  │                      │
│          ▼           │                  │                      │
│  ┌────────────────┐  │                  │                      │
│  │ Avatar Control │  │                  │                      │
│  │  • Expressions │──┼──────────────────┼──► Commands         │
│  │  • Emotions    │  │                  │                      │
│  └────────────────┘  │                  │                      │
│                      │                  │                      │
│  ┌────────────────┐  │                  │                      │
│  │ Config Manager │  │                  │                      │
│  │  • Save/Load   │  │                  │                      │
│  │  • Preferences │  │                  │                      │
│  └────────────────┘  │                  │                      │
└──────────────────────┘                  └──────────────────────┘
```

## Composants Principaux

### 1. Python Layer

#### GUI Module (`src/gui/`)
- **app.py** : Application Qt principale, fenêtre de contrôle
- Gère l'interface utilisateur
- Affiche les contrôles et paramètres
- Interface avec les autres modules

#### IPC Module (`src/ipc/`)
- **unity_bridge.py** : Communication socket avec Unity
- Protocole JSON sur TCP
- Gestion des commandes et réponses
- Thread de réception en arrière-plan

#### Audio Module (`src/audio/`)
- Capture audio via sounddevice
- Traitement du signal (amplitude, fréquences)
- Génération de données de lip-sync
- Support TTS (futur)

#### Avatar Module (`src/avatar/`)
- Gestion des états de l'avatar
- Contrôle des expressions et émotions
- Interface avec Unity pour les blendshapes

#### Utils Module (`src/utils/`)
- **config.py** : Gestion de configuration (JSON)
- **logger.py** : Système de logging
- Fonctions utilitaires communes

### 2. Unity Layer

#### Core Scripts
- **GameManager.cs** : Gestionnaire principal de la scène
- Coordination des composants Unity

#### IPC Scripts
- **PythonBridge.cs** : Serveur socket pour recevoir commandes Python
- **CommandHandler.cs** : Traitement des commandes reçues
- Sérialisation/désérialisation JSON

#### VRM Scripts
- **VRMLoader.cs** : Chargement dynamique de modèles VRM
- **VRMController.cs** : Contrôle des animations et blendshapes
- Interface avec UniVRM

## Protocole de Communication IPC

### Format des Messages

**Python → Unity (Commandes)**
```json
{
  "command": "load_model",
  "data": {
    "path": "C:/path/to/model.vrm"
  }
}
```

**Unity → Python (Réponses)**
```json
{
  "type": "response",
  "command": "load_model",
  "status": "success",
  "data": {
    "model_name": "Avatar",
    "blendshapes": ["Joy", "Angry", "Sorrow"]
  }
}
```

### Commandes Disponibles

| Commande | Direction | Description |
|----------|-----------|-------------|
| `connect` | Python → Unity | Établir la connexion |
| `load_model` | Python → Unity | Charger un modèle VRM |
| `set_expression` | Python → Unity | Changer l'expression |
| `set_blendshape` | Python → Unity | Modifier un blendshape |
| `play_animation` | Python → Unity | Jouer une animation |
| `model_loaded` | Unity → Python | Notification de chargement |
| `animation_complete` | Unity → Python | Fin d'animation |

## Flux de Données

### Chargement d'un Modèle VRM

```
1. User clicks "Load VRM" in Qt GUI
   │
2. Python: Open file dialog
   │
3. Python: Send "load_model" command via socket
   │
4. Unity: Receive command
   │
5. Unity: Load VRM with UniVRM
   │
6. Unity: Extract blendshapes info
   │
7. Unity: Send "model_loaded" response
   │
8. Python: Update GUI with model info
```

### Lip-Sync Audio

```
1. Python: Capture microphone input (sounddevice)
   │
2. Python: Analyze audio amplitude
   │
3. Python: Calculate mouth open value (0.0 - 1.0)
   │
4. Python: Send "set_blendshape" command
   │
   data: { "name": "A", "value": 0.8 }
   │
5. Unity: Apply blendshape to VRM model
   │
6. Unity: Render updated model
```

## Extensibilité

### Ajout d'une Nouvelle Fonctionnalité

1. **Python Side** :
   - Ajouter module dans `src/`
   - Créer classe de contrôle
   - Ajouter UI si nécessaire
   - Implémenter tests

2. **Unity Side** :
   - Créer script C#
   - Ajouter à GameManager
   - Implémenter handler IPC

3. **Communication** :
   - Définir commandes dans protocole
   - Implémenter dans unity_bridge.py
   - Implémenter dans PythonBridge.cs

## Technologies

### Python
- **PySide6 6.6+** : GUI framework (Qt)
- **sounddevice 0.4+** : Audio capture
- **numpy 1.24+** : Numerical processing
- **pytest 7.4+** : Testing

### Unity
- **Unity 2022.3 LTS** : Game engine
- **UniVRM** : VRM support
- **URP** : Universal Render Pipeline
- **Newtonsoft.Json** : JSON serialization (optionnel)

## Performance

### Optimisations Prévues
- Thread pool pour traitement audio
- Message queue pour IPC
- Frame rate limiting
- LOD pour modèles VRM
- Culling et batching

## Sécurité

- IPC limité à localhost (127.0.0.1)
- Validation des chemins de fichiers
- Sanitization des commandes
- Timeout sur les connexions

## Roadmap Technique

### Phase 1 (MVP)
- [x] Communication socket basique
- [ ] Chargement VRM
- [ ] Contrôle blendshapes simple

### Phase 2
- [ ] Audio streaming optimisé
- [ ] Cache de modèles
- [ ] Hot-reload Unity

### Phase 3
- [ ] OSC protocol support
- [ ] WebSocket alternative
- [ ] Plugin system

### Phase 4
- [ ] gRPC for performance
- [ ] Distributed rendering
- [ ] Multi-avatar support
