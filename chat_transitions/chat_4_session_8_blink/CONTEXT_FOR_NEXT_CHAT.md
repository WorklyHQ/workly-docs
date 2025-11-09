# 📖 Contexte pour le Prochain Chat - Session 8 Terminée

## 🎯 Objectif de ce document

Fournir à la **prochaine IA** (nouveau chat) toutes les informations nécessaires pour reprendre le développement exactement où j'ai laissé.

**Date de création :** 21 octobre 2025  
**Projet :** Desktop-Mate (Avatar VRM interactif sur bureau Windows)  
**Dernière session complétée :** Session 8 - Clignement automatique des yeux

---

## 📋 État Global du Projet

### Phase actuelle : Phase 2 (Réalisme & Animations)

**Sessions complétées :** 8/8

| Session | Objectif | État |
|---------|----------|------|
| Session 1 | Setup projet (Git, Python, Unity) | ✅ MVP complet |
| Session 2 | Installation Unity 2022.3 LTS | ✅ MVP complet |
| Session 3 | Installation UniVRM 0.127.3 | ✅ MVP complet |
| Session 4 | Communication IPC Python ↔ Unity | ✅ MVP complet |
| Session 5 | Chargement modèle VRM dynamique | ✅ MVP complet |
| Session 6 | Expressions faciales (6 blendshapes) | ✅ Phase 2 |
| Session 7 | Transitions Lerp smooth | ✅ Phase 2 |
| Session 8 | Clignement automatique (SmoothStep) | ✅ Phase 2 |

### Vision Finale

Créer un **assistant virtuel desktop-mate** avec :
- ✅ Avatar VRM 3D affiché sur le bureau
- ✅ Expressions faciales contrôlables
- ✅ Animations fluides et naturelles
- ✅ Clignement automatique des yeux
- 🔜 Lip-sync audio (parole)
- 🔜 Connexion IA conversationnelle (chatbot)
- 🔜 Mouvements libres sur le bureau

**Inspiration :** [Desktop Mate sur Steam](https://store.steampowered.com/app/3301060/Desktop_Mate/)

---

## 🏗️ Architecture Technique Actuelle

### Stack Technologique

**Unity (Rendu 3D) :**
- Unity 2022.3.50f1 LTS (Universal Render Pipeline)
- UniVRM 0.127.3 (SDK pour modèles VRM)
- C# Scripts (VRMLoader, VRMBlendshapeController, VRMAutoBlinkController, PythonBridge)

**Python (Interface & Logique) :**
- Python 3.10.9
- PySide6 6.8.0 (Qt GUI)
- sounddevice, numpy (futur audio)
- pytest (tests unitaires)

**Communication IPC :**
- Socket TCP (localhost:5555)
- Messages JSON bidirectionnels
- Thread Python pour réception
- Queue Unity (thread-safety)

### Architecture de Communication

```
┌──────────────────────────────────────────────────────────┐
│                    PYTHON (Client)                        │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  app.py (PySide6 GUI)                                     │
│  ┌────────────────────────────────────────────┐          │
│  │ Onglet Modèle                              │          │
│  │   - TextField chemin VRM                   │          │
│  │   - Bouton "Charger Modèle"                │          │
│  │                                              │          │
│  │ Onglet Expressions                          │          │
│  │   - 6 sliders (Happy, Sad, Angry, etc.)    │          │
│  │   - Checkbox "Clignement automatique"       │          │
│  └────────────────────────────────────────────┘          │
│           │                                                │
│           ▼                                                │
│  unity_bridge.py (IPC Client)                             │
│  ┌────────────────────────────────────────────┐          │
│  │ - connect() → TCP socket                   │          │
│  │ - send_command(json) → Unity               │          │
│  │ - receive_thread() → Callbacks             │          │
│  └────────────────────────────────────────────┘          │
│           │                                                │
└───────────┼────────────────────────────────────────────────┘
            │ TCP Socket (JSON)
            │ Port 5555
            ▼
┌──────────────────────────────────────────────────────────┐
│                    UNITY (Server)                         │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  PythonBridge.cs (IPC Server)                             │
│  ┌────────────────────────────────────────────┐          │
│  │ - StartServer() → TCP Listener              │          │
│  │ - ProcessMessages() → Parse JSON            │          │
│  │ - Commandes supportées :                    │          │
│  │   * load_vrm                                │          │
│  │   * set_expression                          │          │
│  │   * set_auto_blink                          │          │
│  └────────────────────────────────────────────┘          │
│           │                                                │
│           ▼                                                │
│  VRMLoader.cs                                             │
│  ┌────────────────────────────────────────────┐          │
│  │ - LoadVRMAsync(path) → Charge modèle       │          │
│  │ - Instancie GameObject dans la scène        │          │
│  └────────────────────────────────────────────┘          │
│           │                                                │
│           ▼                                                │
│  VRMBlendshapeController.cs                               │
│  ┌────────────────────────────────────────────┐          │
│  │ - SetExpression(name, value)                │          │
│  │ - Système Lerp (transitions smooth)         │          │
│  │ - Update() : Interpolation continue         │          │
│  │ - GetBlendShapeProxy() : Accès direct       │          │
│  └────────────────────────────────────────────┘          │
│           │                                                │
│           ▼                                                │
│  VRMAutoBlinkController.cs                                │
│  ┌────────────────────────────────────────────┐          │
│  │ - BlinkLoop() : Timer aléatoire (2-5s)     │          │
│  │ - PerformBlink() : Animation SmoothStep     │          │
│  │ - SetBlinkEnabled(bool) : Toggle on/off    │          │
│  └────────────────────────────────────────────┘          │
│                                                            │
└──────────────────────────────────────────────────────────┘
```

---

## 📂 Structure du Projet

```
c:\Dev\desktop-mate\
├── main.py                          ← Point d'entrée Python
├── requirements.txt                 ← Dépendances Python
├── README.md                        ← Documentation principale
├── .gitignore                       ← Configuration Git
│
├── assets/                          ← Ressources
│   └── Mura Mura - Model.vrm       ← Modèle de test
│
├── src/                             ← Code source Python
│   ├── gui/
│   │   └── app.py                   ← Interface PySide6
│   ├── ipc/
│   │   └── unity_bridge.py          ← Communication IPC
│   ├── utils/
│   │   ├── config.py                ← Configuration JSON
│   │   └── logger.py                ← Système de logs
│   └── audio/                       ← (Futur : audio processing)
│
├── unity/                           ← Scripts Unity partagés
│   ├── PythonBridge.cs              ← Serveur IPC
│   ├── VRMLoader.cs                 ← Chargement VRM
│   ├── VRMBlendshapeController.cs   ← Expressions + Lerp
│   ├── VRMAutoBlinkController.cs    ← Clignement automatique
│   └── DesktopMateUnity/            ← Projet Unity complet
│       ├── Assets/
│       │   ├── Scenes/
│       │   │   └── MainScene.unity
│       │   ├── Scripts/
│       │   │   ├── VRMLoader.cs
│       │   │   ├── VRMBlendshapeController.cs
│       │   │   ├── VRMAutoBlinkController.cs
│       │   │   └── IPC/
│       │   │       └── PythonBridge.cs
│       │   └── VRM/                 ← UniVRM package
│       └── ProjectSettings/
│
├── tests/                           ← Tests unitaires Python
│   ├── test_config.py
│   └── test_unity_bridge.py
│
└── docs/                            ← Documentation complète
    ├── INDEX.md                     ← Arborescence du projet
    ├── README.md                    ← Documentation principale docs
    ├── docs/sessions/session_1_setup/
    ├── docs/sessions/session_2_unity_installation/
    ├── docs/sessions/session_3_univrm_installation/
    ├── docs/sessions/session_4_python_unity_connection/
    ├── docs/sessions/session_5_vrm_loading/
    ├── docs/sessions/session_6_expressions/
    ├── docs/sessions/session_7_animations/
    ├── docs/sessions/session_8_auto_blink/        ← Session 8 (dernière)
    │   ├── README.md
    │   ├── TECHNICAL_GUIDE.md
    │   ├── TROUBLESHOOTING.md
    │   └── scripts/                 ← Scripts finaux Session 8
    │       ├── VRMAutoBlinkController.cs
    │       ├── VRMBlendshapeController.cs
    │       ├── PythonBridge.cs
    │       ├── unity_bridge.py
    │       ├── config.py
    │       └── app.py
    └── chat_transitions/
        ├── chat_1_python_unity_start_session_0_to_5/
        ├── chat_2_expressions_session_6/
        ├── chat_3_animations_session_7/
        └── chat_4_session_8_blink/  ← Transition actuelle
            ├── README.md
            ├── CONTEXT_FOR_NEXT_CHAT.md (ce fichier)
            ├── CURRENT_STATE.md
            └── prompt_transition.txt
```

---

## 🔧 Composants Clés

### 1. VRMAutoBlinkController.cs (Session 8)

**Rôle :** Gère le clignement automatique des yeux

**Fonctionnement :**
```csharp
// Timer aléatoire entre clignements
[SerializeField] private float minInterval = 2.0f;  // 2 secondes min
[SerializeField] private float maxInterval = 5.0f;  // 5 secondes max

// Timings d'animation
[SerializeField] private float closeDuration = 0.05f;  // 50ms fermeture
[SerializeField] private float pauseDuration = 0.03f;  // 30ms pause
[SerializeField] private float openDuration = 0.08f;   // 80ms ouverture
// Total : 160ms (réalisme humain)

// Coroutine principale
IEnumerator BlinkLoop()
{
    while (isEnabled)
    {
        float interval = Random.Range(minInterval, maxInterval);
        yield return new WaitForSeconds(interval);
        yield return PerformBlink();
    }
}

// Animation 3 phases avec SmoothStep
IEnumerator PerformBlink()
{
    // Phase 1 : Fermeture (0.0 → 1.0)
    while (elapsed < closeDuration)
    {
        float value = Mathf.SmoothStep(0f, 1f, t);  // Courbe S
        blendShapeProxy.ImmediatelySetValue(blinkKey, value);
        blendShapeProxy.Apply();
        yield return null;
    }
    
    // Phase 2 : Pause (yeux fermés)
    yield return new WaitForSeconds(pauseDuration);
    
    // Phase 3 : Ouverture (1.0 → 0.0)
    while (elapsed < openDuration)
    {
        float value = Mathf.SmoothStep(1f, 0f, t);  // Courbe S inversée
        blendShapeProxy.ImmediatelySetValue(blinkKey, value);
        blendShapeProxy.Apply();
        yield return null;
    }
}
```

**Méthode publique :**
```csharp
public void SetBlinkEnabled(bool enabled)
{
    isEnabled = enabled;
    if (enabled)
        StartCoroutine(BlinkLoop());
    else
        StopAllCoroutines();
}
```

**Dépendances :**
- Référence à `VRMBlendshapeController` (Inspector Unity)
- Accès à `VRMBlendShapeProxy` via `GetBlendShapeProxy()`

---

### 2. VRMBlendshapeController.cs (Sessions 6, 7, 8)

**Rôle :** Gestion centralisée des expressions faciales avec transitions Lerp

**Système Lerp (Session 7) :**
```csharp
private Dictionary<string, float> currentValues = new Dictionary<string, float>();
private Dictionary<string, float> targetValues = new Dictionary<string, float>();
private float lerpSpeed = 3.0f;

void Update()
{
    // Interpolation continue vers les targets
    foreach (var key in currentValues.Keys.ToList())
    {
        float current = currentValues[key];
        float target = targetValues.ContainsKey(key) ? targetValues[key] : 0f;
        
        currentValues[key] = Mathf.Lerp(current, target, lerpSpeed * Time.deltaTime);
        
        BlendShapeKey blendKey = new BlendShapeKey(GetBlendShapeKey(key));
        blendShapeProxy.ImmediatelySetValue(blendKey, currentValues[key]);
    }
    
    blendShapeProxy.Apply();
}

public void SetExpression(string expressionName, float value)
{
    if (!targetValues.ContainsKey(expressionName))
        currentValues[expressionName] = 0f;
    
    targetValues[expressionName] = Mathf.Clamp01(value);
}
```

**Mapping BlendShapes (Session 8 - FIX CRITIQUE) :**
```csharp
private BlendShapePreset GetBlendShapeKey(string expressionName)
{
    switch (expressionName.ToLower())
    {
        case "happy": return BlendShapePreset.Joy;
        case "sad": return BlendShapePreset.Sorrow;
        case "angry": return BlendShapePreset.Angry;
        case "surprised": return BlendShapePreset.Fun;
        case "neutral": return BlendShapePreset.Neutral;
        
        // ⚠️ CRITIQUE : Ajouté en Session 8
        case "blink": return BlendShapePreset.Blink;
        case "blink_l": return BlendShapePreset.Blink_L;
        case "blink_r": return BlendShapePreset.Blink_R;
        
        default:
            Debug.LogWarning($"Unknown expression: {expressionName}");
            return BlendShapePreset.Unknown;
    }
}
```

**Sans ce mapping, les blendshapes Blink ne s'appliquent PAS visuellement !**

**Méthode ajoutée pour Session 8 :**
```csharp
public VRMBlendShapeProxy GetBlendShapeProxy()
{
    return blendShapeProxy;
}
```

→ Permet à `VRMAutoBlinkController` de manipuler directement le proxy (bypass Lerp)

---

### 3. PythonBridge.cs (Sessions 4, 6, 8)

**Rôle :** Serveur IPC qui écoute les commandes Python

**Commandes supportées :**

| Commande | Paramètres | Action |
|----------|-----------|--------|
| `load_vrm` | `path` (string) | Charge modèle VRM |
| `set_expression` | `name` (string), `value` (float) | Change expression faciale |
| `set_auto_blink` | `enabled` (bool) | Toggle clignement auto |

**Handler set_auto_blink (Session 8) :**
```csharp
case "set_auto_blink":
    if (autoBlinkController != null)
    {
        bool enabled = ExtractBoolValue(json, "enabled");
        autoBlinkController.SetBlinkEnabled(enabled);
        Debug.Log($"[PythonBridge] Auto-blink {(enabled ? "enabled" : "disabled")}");
    }
    else
    {
        Debug.LogError("[PythonBridge] autoBlinkController is null!");
    }
    break;
```

**Méthode helper :**
```csharp
private bool ExtractBoolValue(Dictionary<string, object> json, string key)
{
    if (json.ContainsKey(key))
    {
        if (json[key] is bool boolValue)
            return boolValue;
        if (json[key] is string strValue)
            return strValue.ToLower() == "true";
    }
    return false;
}
```

**Références Inspector Unity :**
- `public VRMLoader vrmLoader`
- `public VRMBlendshapeController blendshapeController`
- `public VRMAutoBlinkController autoBlinkController` ← Ajouté Session 8

---

### 4. unity_bridge.py (Python IPC Client)

**Méthodes disponibles :**

```python
class UnityBridge:
    def __init__(self, host="localhost", port=5555):
        self.socket = None
        self.connected = False
        
    def connect(self) -> bool:
        """Connexion TCP au serveur Unity"""
        
    def disconnect(self):
        """Fermeture propre de la connexion"""
        
    def send_command(self, command: dict) -> bool:
        """Envoi commande JSON à Unity"""
        
    def load_vrm(self, file_path: str) -> bool:
        """Charge un modèle VRM"""
        command = {"command": "load_vrm", "path": file_path}
        return self.send_command(command)
        
    def set_expression(self, expression_name: str, value: float) -> bool:
        """Change une expression faciale (0.0-1.0)"""
        command = {
            "command": "set_expression",
            "name": expression_name,
            "value": value
        }
        return self.send_command(command)
        
    def set_auto_blink(self, enabled: bool) -> bool:
        """Active/désactive le clignement automatique"""
        command = {
            "command": "set_auto_blink",
            "enabled": enabled
        }
        return self.send_command(command)
```

---

### 5. app.py (Python GUI)

**Structure PySide6 :**

```python
class DesktopMateApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # IPC
        self.unity_bridge = UnityBridge()
        self.config = Config()
        
        # UI
        self.init_ui()
        
        # Connexion Unity
        self.unity_bridge.connect()
        
        # Délai avant envoi settings initiaux
        QTimer.singleShot(2500, self.send_initial_settings)
        
    def init_ui(self):
        # Onglet Modèle
        self.model_tab = self.create_model_tab()
        
        # Onglet Expressions
        self.expressions_tab = self.create_expressions_tab()
        
    def create_expressions_tab(self):
        # 6 sliders d'expressions
        self.happy_slider = self.create_expression_slider("Happy")
        self.sad_slider = self.create_expression_slider("Sad")
        # ... etc
        
        # Checkbox clignement automatique (Session 8)
        self.auto_blink_checkbox = QCheckBox("Activer le clignement automatique")
        self.auto_blink_checkbox.setChecked(
            self.config.get("avatar.auto_blink.enabled", False)
        )
        self.auto_blink_checkbox.stateChanged.connect(self.on_auto_blink_toggle)
        
    def on_auto_blink_toggle(self, state):
        enabled = state == Qt.CheckState.Checked
        
        # Sauvegarder config
        self.config.set("avatar.auto_blink.enabled", enabled)
        self.config.save()
        
        # Envoi IPC
        if self.unity_bridge:
            success = self.unity_bridge.set_auto_blink(enabled)
            if not success:
                logger.error("Failed to toggle auto-blink")
                
    def send_initial_settings(self):
        """Applique settings après délai de 2.5s (Unity loading time)"""
        if self.unity_bridge and self.unity_bridge.is_connected():
            # Auto-blink
            enabled = self.config.get("avatar.auto_blink.enabled", False)
            if enabled:
                self.unity_bridge.set_auto_blink(True)
```

---

### 6. config.py (Configuration JSON)

**Structure de configuration actuelle :**

```python
DEFAULT_CONFIG = {
    "ipc": {
        "host": "localhost",
        "port": 5555,
        "timeout": 5.0
    },
    "avatar": {
        "default_model": "assets/Mura Mura - Model.vrm",
        "auto_blink": {
            "enabled": False,
            "min_interval": 2.0,
            "max_interval": 5.0,
            "duration": 0.03
        }
    },
    "ui": {
        "theme": "dark",
        "window": {
            "width": 800,
            "height": 600
        }
    }
}
```

**Emplacement du fichier :**
- Windows : `C:\Users\<USERNAME>\.desktop-mate\config.json`
- Linux/Mac : `~/.desktop-mate/config.json`

**Méthodes utiles :**
```python
config = Config()

# Lecture
value = config.get("avatar.auto_blink.enabled", False)

# Écriture
config.set("avatar.auto_blink.enabled", True)
config.save()
```

---

## 🐛 Problèmes Critiques Résolus (Session 8)

### Problème 1 : Blendshapes Blink non appliqués

**Symptôme :**
- Logs Unity corrects (values 0.0 → 1.0)
- **Aucun effet visuel** dans Game View

**Cause :**
```csharp
// GetBlendShapeKey() ne contenait PAS ces lignes :
case "blink": return BlendShapePreset.Blink;
case "blink_l": return BlendShapePreset.Blink_L;
case "blink_r": return BlendShapePreset.Blink_R;
```

→ Retournait `BlendShapePreset.Unknown` → Unity ignorait les valeurs

**Solution :**
Ajout des 3 cas dans le switch statement de `VRMBlendshapeController.cs`

---

### Problème 2 : Animation trop lente

**Symptôme :**
- Clignement prend ~2 secondes (trop lent)

**Cause :**
- Système Lerp avec `lerpSpeed = 3.0` → temps minimum ~0.33s
- `blinkDuration = 1.5s` trop long

**Solution :**
- **Bypass du système Lerp** : manipulation directe VRMBlendShapeProxy
- Timings optimisés : 50ms + 30ms + 80ms = 160ms total

---

### Problème 3 : Animation "robotique"

**Symptôme :**
- Mouvement linéaire, pas naturel

**Cause :**
```csharp
float value = t;  // Interpolation linéaire
```

**Solution :**
```csharp
float value = Mathf.SmoothStep(0f, 1f, t);  // Courbe S (Hermite)
```

→ Accélération/décélération automatiques

---

## 📊 Données Techniques Importantes

### Configuration Unity Inspector

**GameObject "DesktopMate" :**
- VRMLoader
- VRMBlendshapeController
  - Lerp Speed : 3.0
- VRMAutoBlinkController
  - Blendshape Controller : [assigné]
  - Min Interval : 2.0
  - Max Interval : 5.0
  - Close Duration : 0.05
  - Pause Duration : 0.03
  - Open Duration : 0.08
  - Is Enabled : true (par défaut)
- PythonBridge
  - Port : 5555
  - VRM Loader : [assigné]
  - Blendshape Controller : [assigné]
  - Auto Blink Controller : [assigné]

### Expressions Supportées

| Expression | BlendShapePreset VRM | Range |
|-----------|---------------------|-------|
| Happy | Joy | 0.0 - 1.0 |
| Sad | Sorrow | 0.0 - 1.0 |
| Angry | Angry | 0.0 - 1.0 |
| Surprised | Fun | 0.0 - 1.0 |
| Neutral | Neutral | 0.0 - 1.0 |
| Blink | Blink | 0.0 - 1.0 |
| Blink_L | Blink_L | 0.0 - 1.0 |
| Blink_R | Blink_R | 0.0 - 1.0 |

### Protocole IPC (JSON)

**Format de message :**
```json
{
  "command": "<nom_commande>",
  "<param1>": "<value1>",
  "<param2>": "<value2>"
}
```

**Exemples :**

```json
// Charger VRM
{
  "command": "load_vrm",
  "path": "C:/Dev/desktop-mate/assets/Mura Mura - Model.vrm"
}

// Changer expression
{
  "command": "set_expression",
  "name": "happy",
  "value": 0.8
}

// Toggle clignement
{
  "command": "set_auto_blink",
  "enabled": true
}
```

---

## 🚀 Prochaines Étapes Recommandées

### Session 9 : Options Possibles

#### Option A : Lip-Sync Audio (RECOMMANDÉ) 🎤

**Pourquoi ?**
- Prépare la connexion IA conversationnelle (objectif final)
- Fonctionnalité majeure attendue

**Tâches :**
1. Capture microphone (sounddevice)
2. Analyse FFT (numpy)
3. Mapping fréquences → BlendShapes bouche
   - A, I, U, E, O (voyelles)
   - Amplitude → ouverture bouche
4. Animation temps réel (30-60 FPS)

**Difficulté :** 🔴🔴🔴 Élevée (signal processing)

**Prérequis :**
- Installer sounddevice : `pip install sounddevice`
- Installer numpy : déjà installé
- Vérifier que le modèle VRM a des BlendShapes pour la bouche

---

#### Option B : Mouvements de Tête Subtils 🎭

**Pourquoi ?**
- Facile à implémenter (similaire au clignement)
- Ajoute beaucoup de réalisme

**Tâches :**
1. Head bobbing (mouvement léger gauche/droite)
2. Head tilt (inclinaison subtile)
3. Respiration (mouvement du torse)
4. Paramètres configurables (amplitude, fréquence)

**Difficulté :** 🔴 Faible

---

#### Option C : Eye Tracking (Regard Souris) 👀

**Pourquoi ?**
- Interactivité accrue
- Prépare le suivi de regard avancé

**Tâches :**
1. Récupération position curseur (Python)
2. Calcul angles de rotation des yeux
3. Rotation bones yeux gauche/droit (VRM)
4. Contraintes (limites de rotation)

**Difficulté :** 🔴🔴 Moyenne

---

## 📚 Ressources Clés

### Documentation Interne

**À LIRE ABSOLUMENT :**
- `docs/INDEX.md` → Arborescence complète du projet
- `docs/README.md` → Documentation principale
- `.github/instructions/copilot-instructions.instructions.md` → Règles de développement

**Session 8 (dernière complétée) :**
- `docs/sessions/session_8_auto_blink/TECHNICAL_GUIDE.md` → Architecture détaillée
- `docs/sessions/session_8_auto_blink/TROUBLESHOOTING.md` → Problèmes et solutions
- `docs/sessions/session_8_auto_blink/scripts/` → Scripts finaux

**Transitions précédentes :**
- `docs/chat_transitions/chat_1_python_unity_start_session_0_to_5/`
- `docs/chat_transitions/chat_2_expressions_session_6/`
- `docs/chat_transitions/chat_3_animations_session_7/`

### Documentation Externe

**Unity :**
- [Coroutines](https://docs.unity3d.com/Manual/Coroutines.html)
- [Mathf.SmoothStep](https://docs.unity3d.com/ScriptReference/Mathf.SmoothStep.html)

**UniVRM :**
- [Documentation officielle](https://vrm.dev/en/univrm/)
- [BlendShape Specification](https://github.com/vrm-c/vrm-specification/blob/master/specification/VRMC_vrm-1.0/expressions.md)

**Python :**
- [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)
- [sounddevice](https://python-sounddevice.readthedocs.io/)

---

## 💡 Conseils pour la Prochaine IA

### Règles de Documentation (CRITIQUE)

**⚠️ NE JAMAIS OUBLIER :**

Après **CHAQUE** changement de code, mettre à jour :
1. ✅ `docs/INDEX.md` (si nouveaux fichiers)
2. ✅ `docs/README.md` (si architecture modifiée)
3. ✅ `README.md` (racine) (si fonctionnalités ajoutées)
4. ✅ `docs/session_N/README.md` (session en cours)

**Structure session :**
```
docs/session_N_nom/
├── README.md          ← Vue d'ensemble
├── TECHNICAL_GUIDE.md ← Documentation technique
├── TROUBLESHOOTING.md ← Résolution de problèmes (si nécessaire)
└── scripts/           ← OBLIGATOIRE : Scripts finaux
    ├── script1.cs
    ├── script2.py
    └── ...
```

**⚠️ JAMAIS** créer de fichiers .md en dehors de `docs/` (sauf demande explicite)

**⚠️ JAMAIS** oublier le dossier `scripts/` avec les versions finales

### Avant de Dire "Terminé"

**Checklist obligatoire :**
- [ ] Tests exécutés (`pytest`)
- [ ] Erreurs vérifiées (Python + Unity)
- [ ] Documentation mise à jour (INDEX, README, session)
- [ ] Scripts copiés dans `docs/session_N/scripts/`
- [ ] Récapitulatif affiché

### Méthodologie de Travail

1. **Comprendre** : Lire le contexte, poser des questions
2. **Planifier** : Lister les tâches, expliquer l'approche
3. **Implémenter** : Coder proprement, commenter en français
4. **Tester** : pytest + validation Unity
5. **Documenter** : Mettre à jour TOUS les fichiers nécessaires
6. **Récapituler** : Template de réponse structuré

### Spécificités Unity (Utilisateur ne connaît PAS)

**TOUJOURS expliquer :**
- Pourquoi on fait ça dans Unity
- Où créer le fichier (chemin exact)
- Comment l'attacher à un GameObject
- Quels paramètres configurer dans l'Inspector
- Comment tester que ça fonctionne

**Concepts à expliquer :**
- MonoBehaviour, GameObject, Component
- Coroutines vs Threads
- Update() / FixedUpdate() / LateUpdate()
- Inspector Unity (public fields)
- Scene hierarchy

---

## 🎯 État Final Session 8

### Ce Qui Fonctionne Parfaitement

✅ Avatar VRM affiché dans Unity  
✅ Interface Python (PySide6) avec 2 onglets  
✅ Communication IPC Python ↔ Unity (TCP Socket)  
✅ Chargement dynamique de modèles VRM  
✅ 6 expressions faciales contrôlables  
✅ Transitions Lerp smooth (3.0 speed)  
✅ **Clignement automatique des yeux (160ms, 2-5s intervals)**  
✅ Toggle on/off clignement depuis UI  
✅ Sauvegarde configuration (config.json)  
✅ Tests unitaires Python (8/8 passing)  

### Ce Qui Reste à Faire

🔜 Audio lip-sync (parole)  
🔜 Mouvements de tête subtils  
🔜 Eye tracking (suivi regard)  
🔜 Connexion IA conversationnelle  
🔜 Mouvement libre sur le bureau  
🔜 Système d'émotions contextuelles  
🔜 TTS (Text-to-Speech)  
🔜 STT (Speech-to-Text)  

---

**🎉 Session 8 terminée avec succès ! Prêt pour Session 9 !**

**Si tu es la prochaine IA qui lit ce document :**
- Prends le temps de tout lire attentivement
- Consulte les autres fichiers référencés si besoin
- Pose des questions si quelque chose n'est pas clair
- Respecte les règles de documentation
- Bon développement ! 🚀
