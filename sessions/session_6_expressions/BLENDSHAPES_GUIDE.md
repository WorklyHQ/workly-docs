# 📖 Guide Technique : Blendshapes VRM

**Session 6 - Expressions Faciales**

---

## 🎯 Qu'est-ce qu'un Blendshape ?

### Définition

Un **blendshape** (ou "shape key", "morph target") est une technique d'animation 3D qui permet de **déformer un modèle** en interpolant entre différentes formes de mesh.

**Analogie simple :**
- Imagine que tu as une boule de pâte à modeler (le visage)
- Tu crées plusieurs "poses" : sourire, froncement, bouche ouverte...
- Le blendshape te permet de "mélanger" ces poses avec des pourcentages
- 0% = forme de base, 100% = forme cible complète

### Application aux avatars VRM

Les modèles VRM utilisent des blendshapes pour :
- 😊 **Expressions faciales** : joy, angry, sorrow, surprised, fun
- 👁️ **Clignements** : blink, blink_l, blink_r
- 👄 **Formes de bouche** : a, i, u, e, o (pour lip-sync)
- 👀 **Regard** : lookup, lookdown, lookleft, lookright

---

## ⚠️ Note de version : BlendShapeKey API

### Évolution de l'API UniVRM

**Ancienne approche (dépréciée) :**
```csharp
// ❌ DEPRECATED - Warning CS0618
blendShapeProxy.ImmediatelySetValue("joy", 0.8f);
```

**Approche actuelle (recommandée) :**
```csharp
// ✅ RECOMMANDÉ - Utiliser BlendShapeKey.CreateUnknown()
BlendShapeKey key = BlendShapeKey.CreateUnknown("joy");
blendShapeProxy.ImmediatelySetValue(key, 0.8f);
```

**Pourquoi `CreateUnknown()` ?**
- `CreateUnknown()` crée une clé pour n'importe quelle expression (preset ou custom)
- Fonctionne avec les expressions standard VRM ("joy", "angry", etc.)
- Fonctionne aussi avec des expressions custom définies dans le modèle
- Plus flexible et future-proof

### Autres approches possibles

```csharp
// Pour les presets standard uniquement
BlendShapeKey key = new BlendShapeKey(BlendShapePreset.Joy);
proxy.ImmediatelySetValue(key, 0.8f);

// Pour expressions custom ou génériques
BlendShapeKey key = BlendShapeKey.CreateUnknown("custom_smile");
proxy.ImmediatelySetValue(key, 0.8f);
```

---

## 🏗️ Architecture VRM Blendshapes

### Structure hiérarchique

```
GameObject Avatar VRM
├── Armature (squelette)
├── Body (mesh principal)
│   └── SkinnedMeshRenderer
│       └── BlendShapes (100+ formes)
├── Face (mesh visage)
│   └── SkinnedMeshRenderer
│       └── BlendShapes (expressions)
└── VRMBlendShapeProxy (Component UniVRM)
    └── BlendShapeAvatar (Asset)
        ├── joy → [Face.Smile:100, Eyes.Happy:80]
        ├── angry → [Face.Angry:100, Brow.Down:90]
        └── ...
```

### VRMBlendShapeProxy (UniVRM)

C'est le **component clé** fourni par UniVRM qui :
- Centralise l'accès aux blendshapes
- Gère les mappings entre noms VRM et blendshapes mesh
- Permet de contrôler plusieurs blendshapes simultanément
- Normalise les valeurs (0.0 à 1.0)

**API principale :**
```csharp
// Accéder au proxy
VRMBlendShapeProxy proxy = vrmInstance.GetComponent<VRMBlendShapeProxy>();

// Définir une expression (0.0 = 0%, 1.0 = 100%)
proxy.ImmediatelySetValue(BlendShapePreset.Joy, 0.8f);  // Sourire à 80%

// Définir par nom de string
proxy.ImmediatelySetValue("joy", 0.8f);

// Reset toutes les expressions
proxy.ImmediatelySetValue(BlendShapePreset.Neutral, 1.0f);
```

---

## 🎭 Expressions VRM Standard

### Expressions principales (VRM 0.0 Spec)

| Expression | Enum UniVRM | Description | Valeur typique |
|------------|-------------|-------------|----------------|
| **Joy** | `BlendShapePreset.Joy` | Sourire, yeux heureux | 0.0 - 1.0 |
| **Angry** | `BlendShapePreset.Angry` | Colère, sourcils froncés | 0.0 - 1.0 |
| **Sorrow** | `BlendShapePreset.Sorrow` | Tristesse, yeux baissés | 0.0 - 1.0 |
| **Fun** | `BlendShapePreset.Fun` | Amusement, sourire éclatant | 0.0 - 1.0 |
| **Surprised** | `BlendShapePreset.Surprised` | Surprise, yeux/bouche ouverts | 0.0 - 1.0 |
| **Neutral** | `BlendShapePreset.Neutral` | Neutre, expression par défaut | 1.0 |

### Clignements

| Expression | Enum UniVRM | Description |
|------------|-------------|-------------|
| **Blink** | `BlendShapePreset.Blink` | Clignement des deux yeux |
| **Blink_L** | `BlendShapePreset.Blink_L` | Clignement œil gauche |
| **Blink_R** | `BlendShapePreset.Blink_R` | Clignement œil droit |

### Phonèmes (pour lip-sync)

| Phonème | Enum UniVRM | Description |
|---------|-------------|-------------|
| **A** | `BlendShapePreset.A` | Bouche ouverte (ah) |
| **I** | `BlendShapePreset.I` | Bouche étirée (ii) |
| **U** | `BlendShapePreset.U` | Bouche arrondie (ou) |
| **E** | `BlendShapePreset.E` | Bouche mi-ouverte (eh) |
| **O** | `BlendShapePreset.O` | Bouche ronde (oh) |

### Regard (lookAt - avancé)

| Expression | Enum UniVRM | Description |
|------------|-------------|-------------|
| **LookUp** | `BlendShapePreset.LookUp` | Regard vers le haut |
| **LookDown** | `BlendShapePreset.LookDown` | Regard vers le bas |
| **LookLeft** | `BlendShapePreset.LookLeft` | Regard vers la gauche |
| **LookRight** | `BlendShapePreset.LookRight` | Regard vers la droite |

---

## 💻 Implémentation Unity

### VRMBlendshapeController.cs - Architecture

```csharp
using UnityEngine;
using System.Collections.Generic;
using VRM;

public class VRMBlendshapeController : MonoBehaviour
{
    // Référence au modèle VRM chargé
    public GameObject vrmInstance;
    
    // Proxy UniVRM pour contrôler les blendshapes
    private VRMBlendShapeProxy blendShapeProxy;
    
    // Queue pour thread-safety (comme VRMLoader)
    private Queue<Action> mainThreadActions = new Queue<Action>();
    
    // Initialisation
    void Start() {
        if (vrmInstance != null) {
            InitializeBlendShapeProxy();
        }
    }
    
    // Trouver le VRMBlendShapeProxy
    void InitializeBlendShapeProxy() {
        blendShapeProxy = vrmInstance.GetComponent<VRMBlendShapeProxy>();
        if (blendShapeProxy == null) {
            Debug.LogError("[VRMBlendshape] VRMBlendShapeProxy introuvable !");
        }
    }
    
    // Méthode publique thread-safe
    public void SetExpression(string expressionName, float value) {
        lock (mainThreadActions) {
            mainThreadActions.Enqueue(() => SetExpressionInternal(expressionName, value));
        }
    }
    
    // Exécution sur le main thread
    private void SetExpressionInternal(string expressionName, float value) {
        if (blendShapeProxy == null) return;
        
        // Convertir string → enum (si possible)
        BlendShapeKey key = new BlendShapeKey(expressionName);
        blendShapeProxy.ImmediatelySetValue(key, value);
    }
    
    // Exécuter les actions en queue
    void Update() {
        lock (mainThreadActions) {
            while (mainThreadActions.Count > 0) {
                mainThreadActions.Dequeue()?.Invoke();
            }
        }
    }
}
```

### Mapping String → BlendShapePreset

UniVRM accepte plusieurs formats selon la version :

```csharp
// Format 1 : BlendShapeKey.CreateUnknown() (RECOMMANDÉ)
BlendShapeKey key = BlendShapeKey.CreateUnknown("joy");
proxy.ImmediatelySetValue(key, 0.8f);

// Format 2 : Enum direct (presets standard uniquement)
BlendShapeKey key = new BlendShapeKey(BlendShapePreset.Joy);
proxy.ImmediatelySetValue(key, 0.8f);

// Format 3 : String directement (DÉPRÉCIÉ - warning CS0618)
proxy.ImmediatelySetValue("joy", 0.8f);
```

**Recommandation :** Utiliser **`BlendShapeKey.CreateUnknown()`** pour compatibilité maximale et support des expressions custom.

---

## 🔄 Communication IPC (Python ↔ Unity)

### Format de message

```json
{
    "command": "set_expression",
    "data": {
        "name": "joy",
        "value": 0.8
    }
}
```

### Python → Unity (client)

```python
# src/ipc/unity_bridge.py
class UnityBridge:
    def set_expression(self, expression_name: str, value: float):
        """
        Définir une expression faciale VRM
        
        Args:
            expression_name: Nom de l'expression ("joy", "angry", etc.)
            value: Intensité de 0.0 à 1.0
        """
        return self.send_command("set_expression", {
            "name": expression_name,
            "value": value
        })
    
    def reset_expressions(self):
        """Réinitialiser toutes les expressions à neutre"""
        return self.send_command("reset_expressions", {})
```

### Unity → Python (serveur)

```csharp
// unity/DesktopMateUnity/Assets/Scripts/IPC/PythonBridge.cs
void HandleMessage(string message) {
    // Parser le JSON
    var data = JsonUtility.FromJson<CommandData>(message);
    
    switch (data.command) {
        case "set_expression":
            string name = data.data["name"];
            float value = float.Parse(data.data["value"]);
            blendshapeController.SetExpression(name, value);
            break;
            
        case "reset_expressions":
            blendshapeController.ResetExpressions();
            break;
    }
}
```

---

## 🎨 Interface Python (PySide6)

### Layout proposé

```
┌─────────────────────────────────────────┐
│  Desktop-Mate Control Panel             │
├─────────────────────────────────────────┤
│  [Connection] [VRM Loading] [Expressions] │ ← Onglets
├─────────────────────────────────────────┤
│  Expressions Faciales                    │
│                                          │
│  😊 Joy (Joyeux)         [====•----] 50% │
│  😠 Angry (Colère)       [•---------]  5% │
│  😢 Sorrow (Triste)      [•---------]  0% │
│  😲 Surprised (Surpris)  [•---------]  0% │
│  😄 Fun (Amusé)          [•---------]  0% │
│                                          │
│  [Reset All Expressions]                 │
└─────────────────────────────────────────┘
```

### Code PySide6

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QPushButton
from PySide6.QtCore import Qt

class ExpressionsTab(QWidget):
    def __init__(self, unity_bridge):
        super().__init__()
        self.unity_bridge = unity_bridge
        self.sliders = {}
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Expressions principales
        expressions = [
            ("joy", "😊 Joy (Joyeux)"),
            ("angry", "😠 Angry (Colère)"),
            ("sorrow", "😢 Sorrow (Triste)"),
            ("surprised", "😲 Surprised (Surpris)"),
            ("fun", "😄 Fun (Amusé)")
        ]
        
        for expr_id, expr_label in expressions:
            # Label avec valeur
            label = QLabel(f"{expr_label}: 0%")
            
            # Slider (0-100)
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(100)
            slider.setValue(0)
            
            # Connecter au callback
            slider.valueChanged.connect(
                lambda v, eid=expr_id, lbl=label: self.on_slider_change(eid, lbl, v)
            )
            
            self.sliders[expr_id] = slider
            layout.addWidget(label)
            layout.addWidget(slider)
        
        # Bouton reset
        reset_btn = QPushButton("Reset All Expressions")
        reset_btn.clicked.connect(self.reset_all)
        layout.addWidget(reset_btn)
        
        self.setLayout(layout)
    
    def on_slider_change(self, expression_id, label, value):
        # Convertir 0-100 → 0.0-1.0
        normalized_value = value / 100.0
        
        # Mettre à jour le label
        label.setText(f"{label.text().split(':')[0]}: {value}%")
        
        # Envoyer à Unity
        if self.unity_bridge.connected:
            self.unity_bridge.set_expression(expression_id, normalized_value)
    
    def reset_all(self):
        # Reset tous les sliders
        for slider in self.sliders.values():
            slider.setValue(0)
        
        # Envoyer commande reset à Unity
        if self.unity_bridge.connected:
            self.unity_bridge.reset_expressions()
```

---

## 🧪 Tests et Debugging

### Test 1 : Vérifier VRMBlendShapeProxy

```csharp
// Dans VRMBlendshapeController.cs Start()
void Start() {
    if (vrmInstance != null) {
        InitializeBlendShapeProxy();
        
        // TEST : Lister toutes les expressions disponibles
        if (blendShapeProxy != null) {
            Debug.Log("[VRMBlendshape] Expressions disponibles :");
            foreach (var clip in blendShapeProxy.BlendShapeAvatar.Clips) {
                Debug.Log($"  - {clip.BlendShapeName}");
            }
        }
    }
}
```

### Test 2 : Test manuel dans Unity Console

```csharp
// Créer un bouton de test dans Unity (optionnel)
[ContextMenu("Test Joy Expression")]
void TestJoyExpression() {
    SetExpression("joy", 1.0f);
}
```

### Test 3 : Logs détaillés

```csharp
private void SetExpressionInternal(string expressionName, float value) {
    Debug.Log($"[VRMBlendshape] SetExpression: {expressionName} = {value:F2}");
    
    if (blendShapeProxy == null) {
        Debug.LogError("[VRMBlendshape] blendShapeProxy est null !");
        return;
    }
    
    BlendShapeKey key = new BlendShapeKey(expressionName);
    blendShapeProxy.ImmediatelySetValue(key, value);
    
    Debug.Log($"[VRMBlendshape] ✅ Expression '{expressionName}' appliquée");
}
```

---

## 🐛 Problèmes Courants

### Problème 1 : Expression ne s'affiche pas

**Causes possibles :**
1. Le modèle VRM ne contient pas cette expression
2. Nom de blendshape incorrect (casse, typo)
3. VRMBlendShapeProxy non initialisé

**Solution :**
```csharp
// Vérifier les noms disponibles
foreach (var clip in blendShapeProxy.BlendShapeAvatar.Clips) {
    Debug.Log(clip.BlendShapeName);
}

// Essayer différentes variantes
SetExpression("joy", 1.0f);
SetExpression("Joy", 1.0f);
SetExpression("Preset.Joy", 1.0f);
```

### Problème 2 : Expressions se cumulent

**Cause :** Les blendshapes ne sont pas mutuellement exclusifs

**Solution :** Reset avant d'appliquer une nouvelle expression
```csharp
void SetExpressionExclusive(string expressionName, float value) {
    // Reset toutes les expressions principales
    blendShapeProxy.ImmediatelySetValue(BlendShapePreset.Neutral, 1.0f);
    
    // Puis appliquer la nouvelle
    SetExpressionInternal(expressionName, value);
}
```

### Problème 3 : Lag ou saccades

**Cause :** Appels trop fréquents depuis Python

**Solution :** Throttling ou debouncing
```python
import time

class ExpressionsTab:
    def __init__(self):
        self.last_update = {}
        self.throttle_delay = 0.05  # 50ms minimum entre updates
    
    def on_slider_change(self, expression_id, value):
        now = time.time()
        if expression_id in self.last_update:
            if now - self.last_update[expression_id] < self.throttle_delay:
                return  # Skip cet update
        
        self.last_update[expression_id] = now
        self.unity_bridge.set_expression(expression_id, value / 100.0)
```

---

## 🎯 Améliorations Futures

### Phase 1 : Expressions combinées
- Permettre plusieurs expressions simultanées
- Système de poids/priorités
- Interpolation smooth entre états

### Phase 2 : Présets d'émotions
- Sauvegarder des configurations complètes
- Boutons quick-action
- Import/export JSON

### Phase 3 : Animations automatiques
- Idle : clignement automatique toutes les 3-5s
- Respiration : légère animation chest/shoulders
- Random micro-expressions

### Phase 4 : Réactivité audio
- Analyse microphone → ouverture bouche
- Détection phonèmes → formes bouche (A, I, U, E, O)
- Synchronisation lip-sync

### Phase 5 : IA émotionnelle
- Analyse sentiment de texte chatbot
- Mapping émotion → expression
- Transitions naturelles entre états

---

## 📚 Ressources Supplémentaires

### Documentation officielle
- [VRM Specification](https://github.com/vrm-c/vrm-specification)
- [UniVRM Documentation](https://vrm.dev/univrm/)
- [BlendShape Schema](https://github.com/vrm-c/vrm-specification/blob/master/specification/0.0/schema/vrm.blendshape.md)

### Tutoriels
- [UniVRM BlendShape Tutorial](https://vrm.dev/en/univrm/blendshape/)
- [Unity BlendShapes Basics](https://docs.unity3d.com/Manual/BlendShapes.html)

---

**🎭 Bon développement des expressions faciales ! 😊**
