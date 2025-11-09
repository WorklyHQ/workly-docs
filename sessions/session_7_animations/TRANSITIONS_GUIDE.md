# 🎨 Guide Technique : Transitions Fluides VRM

## 📖 Introduction

Ce guide explique en détail l'implémentation du système de transitions fluides pour les expressions faciales VRM.

## 🏗️ Architecture du système Lerp

### Vue d'ensemble

```
Python (Interface)
    ↓ IPC (TCP Socket)
PythonBridge (Unity - Thread réseau)
    ↓ Queue mainThreadActions
VRMBlendshapeController (Unity - Thread principal)
    ↓ Lerp Update()
VRM BlendShapeProxy
    ↓
Modèle 3D VRM (expressions)
```

## 🔧 VRMBlendshapeController v2.0

### Structure des données

```csharp
/// <summary>
/// VRMBlendshapeController v2.0 - Gestion des expressions avec transitions
/// </summary>
public class VRMBlendshapeController : MonoBehaviour
{
    // Référence au proxy VRM (initialisé au chargement)
    private VRMBlendShapeProxy blendShapeProxy;
    
    // Dictionnaires pour les valeurs (v2.0)
    private Dictionary<BlendShapeKey, float> currentValues;  // Valeurs affichées
    private Dictionary<BlendShapeKey, float> targetValues;   // Valeurs cibles
    
    // Paramètres de transition
    [SerializeField]
    private float transitionSpeed = 3.0f;  // Vitesse par défaut
    
    // Thread-safety
    private Queue<Action> mainThreadActions = new Queue<Action>();
    
    // État
    private bool isInitialized = false;
}
```

### Initialisation

```csharp
public void Initialize(GameObject vrmModel)
{
    // Récupérer le BlendShapeProxy du modèle VRM
    blendShapeProxy = vrmModel.GetComponent<VRMBlendShapeProxy>();
    
    if (blendShapeProxy == null)
    {
        Debug.LogError("[VRMBlendshape] ❌ BlendShapeProxy introuvable !");
        return;
    }
    
    // Initialiser les dictionnaires
    currentValues = new Dictionary<BlendShapeKey, float>();
    targetValues = new Dictionary<BlendShapeKey, float>();
    
    // Initialiser les expressions principales à 0
    string[] expressions = { "joy", "angry", "sorrow", "fun", "surprised" };
    
    foreach (string expr in expressions)
    {
        BlendShapeKey key = GetBlendShapeKey(expr);
        currentValues[key] = 0.0f;
        targetValues[key] = 0.0f;
    }
    
    isInitialized = true;
    Debug.Log("[VRMBlendshape] ✅ Initialisé avec succès");
}
```

### Méthode GetBlendShapeKey

```csharp
/// <summary>
/// Obtient la clé BlendShape selon le nom de l'expression
/// Gère les presets standards et les blendshapes custom
/// </summary>
private BlendShapeKey GetBlendShapeKey(string expressionName)
{
    switch (expressionName.ToLower())
    {
        // Presets standards VRM
        case "joy":
            return BlendShapeKey.CreateFromPreset(BlendShapePreset.Joy);
        case "angry":
            return BlendShapeKey.CreateFromPreset(BlendShapePreset.Angry);
        case "sorrow":
            return BlendShapeKey.CreateFromPreset(BlendShapePreset.Sorrow);
        case "fun":
            return BlendShapeKey.CreateFromPreset(BlendShapePreset.Fun);
            
        // Blendshape custom
        case "surprised":
            return BlendShapeKey.CreateUnknown("Surprised");
            
        default:
            Debug.LogWarning($"[VRMBlendshape] Expression inconnue : {expressionName}");
            return BlendShapeKey.CreateFromPreset(BlendShapePreset.Neutral);
    }
}
```

### Boucle Update - Le cœur du système

```csharp
/// <summary>
/// Update - Appelée chaque frame par Unity
/// C'est ici que la magie du Lerp opère !
/// </summary>
void Update()
{
    // 1. Exécuter les actions en attente (thread-safety)
    lock (mainThreadActions)
    {
        while (mainThreadActions.Count > 0)
        {
            mainThreadActions.Dequeue()?.Invoke();
        }
    }
    
    // 2. Vérifier l'initialisation
    if (!isInitialized || blendShapeProxy == null)
        return;
    
    // 3. Interpoler TOUTES les expressions vers leurs cibles
    List<BlendShapeKey> keys = new List<BlendShapeKey>(currentValues.Keys);
    
    foreach (BlendShapeKey key in keys)
    {
        if (!targetValues.ContainsKey(key))
            continue;
        
        float current = currentValues[key];
        float target = targetValues[key];
        
        // LERP : Interpolation linéaire
        // Plus transitionSpeed est élevé, plus la transition est rapide
        float newValue = Mathf.Lerp(current, target, Time.deltaTime * transitionSpeed);
        
        // Mettre à jour la valeur courante
        currentValues[key] = newValue;
        
        // Appliquer au modèle VRM
        blendShapeProxy.ImmediatelySetValue(key, newValue);
    }
}
```

### Compréhension du Lerp

**Formule mathématique :**
```
newValue = current + (target - current) * (Time.deltaTime * transitionSpeed)
```

**Comportement :**
- Si `current = 0.0` et `target = 1.0` :
  - Frame 1 (dt=0.016s, speed=3.0) : `0.0 + (1.0-0.0) * 0.048 = 0.048`
  - Frame 2 : `0.048 + (1.0-0.048) * 0.048 ≈ 0.094`
  - Frame 3 : `0.094 + (1.0-0.094) * 0.048 ≈ 0.137`
  - ...
  - Converge vers 1.0 de façon **exponentielle**

**Effet de la vitesse :**
- `speed = 1.0` : Transition lente (~1 seconde)
- `speed = 3.0` : Transition normale (~0.3 seconde)
- `speed = 10.0` : Transition rapide (~0.1 seconde)

### Définir une expression

```csharp
/// <summary>
/// Définit l'expression cible (appelé depuis Python via IPC)
/// </summary>
public void SetExpression(string expressionName, float value)
{
    // Enqueue pour exécution sur le thread principal
    lock (mainThreadActions)
    {
        mainThreadActions.Enqueue(() => SetExpressionInternal(expressionName, value));
    }
}

/// <summary>
/// Exécution réelle (main thread uniquement)
/// </summary>
private void SetExpressionInternal(string expressionName, float value)
{
    if (!isInitialized || blendShapeProxy == null)
    {
        Debug.LogWarning("[VRMBlendshape] ⚠️ Commande ignorée : modèle non chargé");
        return;
    }
    
    try
    {
        // Obtenir la clé
        BlendShapeKey key = GetBlendShapeKey(expressionName);
        
        // Clamp la valeur
        value = Mathf.Clamp01(value);
        
        // Définir la CIBLE (pas la valeur courante !)
        targetValues[key] = value;
        
        // Initialiser currentValues si première fois
        if (!currentValues.ContainsKey(key))
        {
            currentValues[key] = 0.0f;
        }
        
        Debug.Log($"[VRMBlendshape] 🎯 {expressionName} → {value:F2} (transition vers cible)");
    }
    catch (Exception e)
    {
        Debug.LogError($"[VRMBlendshape] ❌ Erreur : {e.Message}");
    }
}
```

### Changer la vitesse de transition

```csharp
/// <summary>
/// Change la vitesse de transition (appelable en temps réel)
/// </summary>
public void SetTransitionSpeed(float speed)
{
    lock (mainThreadActions)
    {
        mainThreadActions.Enqueue(() => {
            transitionSpeed = Mathf.Clamp(speed, 0.1f, 10.0f);
            Debug.Log($"[VRMBlendshape] ⚡ Vitesse : {transitionSpeed:F1}");
        });
    }
}
```

### Reset des expressions

```csharp
/// <summary>
/// Reset toutes les expressions à 0 (avec transition smooth)
/// </summary>
public void ResetExpressions()
{
    lock (mainThreadActions)
    {
        mainThreadActions.Enqueue(() => ResetExpressionsInternal());
    }
}

private void ResetExpressionsInternal()
{
    if (!isInitialized || blendShapeProxy == null)
    {
        Debug.Log("[VRMBlendshape] ℹ️ Reset ignoré : modèle non chargé");
        return;
    }
    
    // Mettre toutes les CIBLES à 0
    // L'Update() s'occupera de la transition smooth
    string[] mainExpressions = { "joy", "angry", "sorrow", "fun", "surprised" };
    
    foreach (string expr in mainExpressions)
    {
        BlendShapeKey key = GetBlendShapeKey(expr);
        targetValues[key] = 0.0f;
        
        if (!currentValues.ContainsKey(key))
        {
            currentValues[key] = 0.0f;
        }
    }
    
    Debug.Log("[VRMBlendshape] 🔄 Reset des expressions (transition smooth)");
}
```

## 🌉 PythonBridge - Communication IPC

### Queue thread-safe

```csharp
// Déclaration
private Queue<Action> mainThreadActions = new Queue<Action>();

// Update() - Exécution sur le thread principal
void Update()
{
    lock (mainThreadActions)
    {
        while (mainThreadActions.Count > 0)
        {
            mainThreadActions.Dequeue()?.Invoke();
        }
    }
}

// Utilisation depuis le thread réseau
lock (mainThreadActions)
{
    mainThreadActions.Enqueue(() => {
        // Code Unity API ici (Destroy, GetComponent, etc.)
    });
}
```

### Commande set_transition_speed

```csharp
else if (jsonMessage.Contains("\"set_transition_speed\""))
{
    Debug.Log("[PythonBridge] ⚡ Commande : Changer vitesse de transition");
    
    // Extraire la vitesse
    float speed = ExtractFloatValue(jsonMessage, "speed");
    
    if (blendshapeController != null)
    {
        blendshapeController.SetTransitionSpeed(speed);
        
        SendMessage(new {
            type = "response",
            command = "set_transition_speed",
            status = "success",
            message = $"Vitesse de transition définie à {speed:F2}"
        });
    }
}
```

### Commande unload_model

```csharp
else if (jsonMessage.Contains("\"unload_model\""))
{
    Debug.Log("[PythonBridge] 🗑️ Commande : Décharger le modèle VRM");
    
    // IMPORTANT : Enqueue car Destroy() nécessite le thread principal
    lock (mainThreadActions)
    {
        mainThreadActions.Enqueue(() => {
            if (vrmLoader != null)
            {
                vrmLoader.UnloadModel();  // Destroy(currentModel)
                
                SendMessage(new {
                    type = "response",
                    command = "unload_model",
                    status = "success",
                    message = "Modèle déchargé avec succès"
                });
            }
        });
    }
}
```

## 🐍 Interface Python

### Slider de vitesse

```python
# Création du slider
speed_slider = QSlider(Qt.Orientation.Horizontal)
speed_slider.setMinimum(10)   # 1.0
speed_slider.setMaximum(100)  # 10.0
speed_slider.setTickInterval(10)  # Ticks tous les 10
speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)

# Bloquer signaux pendant initialisation
speed_slider.blockSignals(True)
speed_slider.setValue(30)  # 3.0 (défaut)
speed_slider.blockSignals(False)

# Connecter le handler
speed_slider.valueChanged.connect(self.on_speed_slider_change)

# Trigger initial
self.on_speed_slider_change(30)
```

### Handler du slider

```python
def on_speed_slider_change(self, value: int):
    """
    Gère le changement de vitesse
    value: 10-100 → speed: 1.0-10.0
    """
    # Mapping direct
    speed = value / 10.0
    
    # Clamp
    speed = max(0.1, min(10.0, speed))
    
    # Labels adaptatifs
    if speed <= 1.5:
        speed_text = "Très lent"
    elif speed <= 2.5:
        speed_text = "Lent"
    elif speed <= 4.0:
        speed_text = "Normal"
    elif speed <= 7.0:
        speed_text = "Rapide"
    else:
        speed_text = "Très rapide"
    
    # Mise à jour label
    self.speed_label.setText(f"Vitesse de transition : {speed:.1f} ({speed_text})")
    
    # Envoi à Unity (seulement si connecté ET VRM chargé)
    if self.unity_bridge.is_connected() and self.vrm_loaded:
        self.unity_bridge.set_transition_speed(speed)
        logger.debug(f"Set transition speed to {speed:.1f}")
```

### Envoi automatique après chargement VRM

```python
def toggle_vrm_model(self):
    if not self.vrm_loaded:
        # ... chargement du modèle ...
        
        # Envoyer la vitesse après 1.5s (délai pour chargement VRM)
        import time
        import threading
        
        def send_speed_after_delay():
            time.sleep(1.5)
            if hasattr(self, 'speed_slider'):
                value = self.speed_slider.value()
                speed = value / 10.0
                speed = max(0.1, min(10.0, speed))
                self.unity_bridge.set_transition_speed(speed)
                logger.info(f"Set initial transition speed to {speed:.1f}")
        
        threading.Thread(target=send_speed_after_delay, daemon=True).start()
```

## 🎯 Système de modèle par défaut

### Configuration (config.json)

```json
{
  "avatar": {
    "last_model": null,
    "default_model": "C:/Dev/desktop-mate/assets/Mura Mura - Model.vrm"
  }
}
```

### Définir le modèle par défaut

```python
def set_default_model(self):
    """Dialogue pour définir le modèle par défaut"""
    file_path, _ = QFileDialog.getOpenFileName(
        self,
        "Définir le modèle VRM par défaut",
        self.config.get("avatar.default_model", ""),
        "Fichiers VRM (*.vrm);;Tous les fichiers (*.*)"
    )
    
    if file_path:
        # Sauvegarder dans config
        self.config.set("avatar.default_model", file_path)
        self.config.save()
        
        # Confirmation
        QMessageBox.information(
            self,
            "Modèle par défaut défini",
            f"Le modèle par défaut a été défini :\n\n{file_path}"
        )
```

### Charger le modèle par défaut

```python
def toggle_vrm_model(self):
    if not self.vrm_loaded:
        # Récupérer le modèle par défaut
        default_model = self.config.get("avatar.default_model")
        
        if not default_model:
            # Proposer de le définir
            reply = QMessageBox.question(
                self,
                "Aucun modèle par défaut",
                "Aucun modèle VRM par défaut n'est défini.\n\n"
                "Voulez-vous en définir un maintenant ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.set_default_model()
            return
        
        # Vérifier existence
        from pathlib import Path
        if not Path(default_model).exists():
            QMessageBox.warning(
                self,
                "Fichier introuvable",
                f"Le modèle par défaut est introuvable :\n{default_model}"
            )
            return
        
        # Charger !
        file_path = default_model
        # ... reste du chargement ...
```

## 📊 Diagramme de séquence complet

```
Utilisateur          Python GUI          Unity Bridge        VRMController        VRM Model
    │                     │                     │                  │                  │
    │  Move slider       │                     │                  │                  │
    ├──────────────────>│                     │                  │                  │
    │                    │  set_transition_speed │                │                  │
    │                    ├──────────────────────>│                │                  │
    │                    │                       │  Enqueue()     │                  │
    │                    │                       ├───────────────>│                  │
    │                    │                       │                │                  │
    │                    │                       │  Update()      │                  │
    │                    │                       │  Dequeue()     │                  │
    │                    │                       │  SetSpeed(3.0) │                  │
    │                    │                       │<───────────────┤                  │
    │                    │                       │                │                  │
    │  Change expression │                     │                  │                  │
    ├──────────────────>│                     │                  │                  │
    │                    │  set_expression      │                │                  │
    │                    ├──────────────────────>│                │                  │
    │                    │                       │  Enqueue()     │                  │
    │                    │                       ├───────────────>│                  │
    │                    │                       │                │                  │
    │                    │                       │  Update()      │                  │
    │                    │                       │  Dequeue()     │                  │
    │                    │                       │  SetTarget(1.0)│                  │
    │                    │                       │<───────────────┤                  │
    │                    │                       │                │                  │
    │                    │                       │  Update() x N  │                  │
    │                    │                       │  Lerp()        │                  │
    │                    │                       │  Apply()       │                  │
    │                    │                       │<───────────────┤                  │
    │                    │                       │                ├─────────────────>│
    │                    │                       │                │  ImmediatelySetValue
    │                    │                       │                │<─────────────────┤
    │                    │                       │                │  (animated!)     │
```

## 🔍 Debugging

### Logs Unity à surveiller

```
✅ Succès :
[VRMBlendshape] ✅ Initialisé avec succès
[VRMBlendshape] 🎯 joy → 1.00 (transition vers cible)
[VRMBlendshape] ⚡ Vitesse : 3.0

⚠️ Warnings normaux :
[VRMBlendshape] ⚠️ Commande ignorée : modèle non chargé
[VRMBlendshape] ℹ️ Reset ignoré : modèle non chargé

❌ Erreurs à corriger :
[VRMBlendshape] ❌ BlendShapeProxy introuvable !
[PythonBridge] ❌ Erreur de traitement : Destroy can only be called from main thread
```

### Tests de performance

```csharp
// Ajouter dans Update() pour mesurer le temps Lerp
float startTime = Time.realtimeSinceStartup;

// ... code Lerp ...

float endTime = Time.realtimeSinceStartup;
float elapsed = (endTime - startTime) * 1000f; // en ms

if (elapsed > 1.0f) // Warning si > 1ms
{
    Debug.LogWarning($"[VRMBlendshape] ⚠️ Lerp lent : {elapsed:F2}ms");
}
```

## 📚 Ressources

- [Mathf.Lerp Documentation](https://docs.unity3d.com/ScriptReference/Mathf.Lerp.html)
- [Time.deltaTime Explained](https://docs.unity3d.com/ScriptReference/Time-deltaTime.html)
- [Threading in Unity](https://docs.unity3d.com/Manual/ExecutionOrder.html)
- [UniVRM BlendShape API](https://vrm.dev/en/univrm/api/blendshape/)

---

**🎓 Fin du guide technique**

*Maintenant tu comprends parfaitement le système de transitions !*
