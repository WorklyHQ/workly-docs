# 🔧 Guide Technique - Session 8 : Clignement Automatique des Yeux

## 📋 Vue d'ensemble

Cette session implémente un système de **clignement automatique des yeux** réaliste pour l'avatar VRM, avec des animations fluides utilisant l'interpolation **SmoothStep** (courbes de Hermite).

### 🎯 Objectifs accomplis

- ✅ Clignement automatique avec intervalles aléatoires (2-5 secondes)
- ✅ Animation réaliste (0.16s par clignement) avec courbes SmoothStep
- ✅ Toggle on/off depuis l'interface Python
- ✅ Sauvegarde de l'état dans la configuration
- ✅ Pas de conflit avec les expressions manuelles

---

## 🏗️ Architecture

### Composants Unity (C#)

#### 1. VRMAutoBlinkController.cs

**Rôle :** Contrôleur principal du clignement automatique

**Fonctionnement :**
- Coroutine `BlinkLoop()` génère des intervalles aléatoires (Random.Range 2-5s)
- Coroutine `PerformBlink()` exécute l'animation en 3 phases
- Manipulation **directe** du VRMBlendShapeProxy (bypass du système Lerp)

**Phases de l'animation :**

```
Phase 1 : FERMETURE (0.05s)
┌─────────────────────────────┐
│ Value : 0.0 → 1.0          │
│ Courbe : SmoothStep         │
│ Acceleration → Max → Decel  │
└─────────────────────────────┘

Phase 2 : PAUSE (0.03s)
┌─────────────────────────────┐
│ Value : 1.0 (maintenu)      │
│ Yeux complètement fermés    │
└─────────────────────────────┘

Phase 3 : OUVERTURE (0.08s)
┌─────────────────────────────┐
│ Value : 1.0 → 0.0          │
│ Courbe : SmoothStep         │
│ Acceleration → Max → Decel  │
└─────────────────────────────┘

Total : ~0.16s (réalisme humain)
```

**Code clé - Animation SmoothStep :**

```csharp
// Phase 1 : Fermeture
while (elapsed < closeDuration)
{
    elapsed += Time.deltaTime;
    float t = Mathf.Clamp01(elapsed / closeDuration);
    float value = Mathf.SmoothStep(0f, 1f, t);  // ← Courbe S
    
    blendShapeProxy.ImmediatelySetValue(blinkKey, value);
    blendShapeProxy.Apply();
    yield return null;
}
```

**Pourquoi SmoothStep ?**
- `t²` → Accélération naturelle au début
- `1 - t²` → Décélération douce à la fin
- Évite l'effet "robotique" des animations linéaires
- Formule mathématique : `3t² - 2t³` (interpolation de Hermite)

#### 2. VRMBlendshapeController.cs (Modifications)

**Ajout critique :** Mapping des BlendShapes Blink

```csharp
private BlendShapePreset GetBlendShapeKey(string expressionName)
{
    switch (expressionName.ToLower())
    {
        // ... autres expressions ...
        
        // ⚠️ CRITIQUE : Ces lignes sont ESSENTIELLES
        case "blink": return BlendShapePreset.Blink;
        case "blink_l": return BlendShapePreset.Blink_L;
        case "blink_r": return BlendShapePreset.Blink_R;
        
        default: return BlendShapePreset.Unknown;
    }
}
```

**Sans ce mapping :**
- Les blendshapes "blink" créent des clés `Unknown`
- Unity n'applique PAS les valeurs au modèle VRM
- Résultat : logs corrects mais **aucun effet visuel**

**Nouvelle méthode publique :**

```csharp
public VRMBlendShapeProxy GetBlendShapeProxy()
{
    return blendShapeProxy;
}
```

→ Permet à `VRMAutoBlinkController` d'accéder directement au proxy

#### 3. PythonBridge.cs (Extension)

**Nouvelle commande IPC :** `set_auto_blink`

```csharp
case "set_auto_blink":
    if (autoBlinkController != null)
    {
        bool enabled = ExtractBoolValue(json, "enabled");
        autoBlinkController.SetBlinkEnabled(enabled);
        Debug.Log($"[PythonBridge] Auto-blink {(enabled ? "enabled" : "disabled")}");
    }
    break;
```

**Nouvelle méthode helper :**

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

### Composants Python

#### 1. unity_bridge.py (Extension)

**Nouvelle méthode :**

```python
def set_auto_blink(self, enabled: bool) -> bool:
    """Active/désactive le clignement automatique des yeux"""
    command = {
        "command": "set_auto_blink",
        "enabled": enabled
    }
    return self.send_command(command)
```

#### 2. config.py (Extension)

**Nouvelle section de configuration :**

```python
"avatar": {
    "auto_blink": {
        "enabled": False,           # Toggle on/off
        "min_interval": 2.0,        # Intervalle min entre clignements
        "max_interval": 5.0,        # Intervalle max
        "duration": 0.03            # Durée de la pause (yeux fermés)
    }
}
```

**Notes :**
- `min_interval` et `max_interval` : utilisés par Unity (côté C#)
- `duration` : pause entre fermeture/ouverture
- `enabled` : sauvegardé dans `~/.desktop-mate/config.json`

#### 3. app.py (Extension)

**Nouveau widget :**

```python
self.auto_blink_checkbox = QCheckBox("Activer le clignement automatique des yeux")
self.auto_blink_checkbox.setChecked(self.config.get("avatar.auto_blink.enabled", False))
self.auto_blink_checkbox.stateChanged.connect(self.on_auto_blink_toggle)
```

**Handler :**

```python
def on_auto_blink_toggle(self, state):
    enabled = state == Qt.CheckState.Checked
    
    # Sauvegarde config
    self.config.set("avatar.auto_blink.enabled", enabled)
    self.config.save()
    
    # Envoi IPC
    if self.unity_bridge:
        success = self.unity_bridge.set_auto_blink(enabled)
        if not success:
            logger.error("Failed to toggle auto-blink")
```

**Délai d'initialisation :**

```python
def send_initial_settings(self):
    QTimer.singleShot(2500, self._apply_initial_settings)  # 2.5s delay
```

→ Laisse le temps à Unity de charger le modèle VRM avant d'envoyer les paramètres

---

## 🔬 Détails Techniques

### Algorithme SmoothStep

**Formule mathématique :**

```
SmoothStep(x) = 3x² - 2x³
```

**Caractéristiques :**
- Dérivée nulle en x=0 et x=1 (pente = 0 aux extrémités)
- Pente maximale en x=0.5
- Courbe symétrique (forme de "S")
- Interpolation C¹ continue

**Comparaison avec d'autres méthodes :**

| Méthode | Formule | Avantages | Inconvénients |
|---------|---------|-----------|---------------|
| **Linear** | `value = t` | Simple, rapide | Robotique, pas naturel |
| **Ease-In (t²)** | `value = t²` | Accélération douce | Décélération brutale |
| **Ease-Out (1-t²)** | `value = 1-(1-t)²` | Décélération douce | Accélération brutale |
| **SmoothStep** | `3t² - 2t³` | ✅ Natural, fluide | Légèrement plus coûteux |
| **SmootherStep** | `6t⁵ - 15t⁴ + 10t³` | Encore plus lisse | Plus coûteux (non nécessaire ici) |

### Timings et Réalisme

**Référence biologique :**
- Clignement humain normal : **100-150ms**
- Fréquence : **15-20 fois par minute** (3-4 secondes d'intervalle)

**Paramètres implémentés :**
- Close : 50ms (0.05s)
- Pause : 30ms (0.03s)
- Open : 80ms (0.08s)
- **Total : 160ms (0.16s)** → Réalisme humain ✅
- Intervalle : 2-5s (aléatoire) → Naturel ✅

### Gestion du Threading Unity

**⚠️ Règle critique Unity :**
> Unity API calls MUST happen on the main thread

**Architecture mise en place :**

```
Python Thread                Unity Main Thread
     │                              │
     │  ──── TCP Socket ────>      │
     │   (set_auto_blink)           │
     │                              ├── PythonBridge.ProcessMessages()
     │                              │   (dans Update())
     │                              │
     │                              ├── autoBlinkController.SetBlinkEnabled(true)
     │                              │
     │                              └── StartCoroutine(BlinkLoop())
```

**Pourquoi des Coroutines ?**
- Permettent des delays sans bloquer Update()
- `yield return new WaitForSeconds(interval)` = non-bloquant
- Alternative : `Thread.Sleep()` bloquerait tout Unity ❌

### Manipulation Directe vs Lerp

**Système Lerp (Session 7) :**
- `SetExpression("happy", 0.8)` → Queue + Lerp progressif
- Bon pour transitions longues (expressions faciales)
- Problème : trop lent pour clignement (~0.33s minimum)

**Système Direct (Session 8) :**
```csharp
blendShapeProxy.ImmediatelySetValue(key, value);
blendShapeProxy.Apply();
```
- Application instantanée (1 frame)
- Permet contrôle précis du timing avec coroutines
- Utilisé UNIQUEMENT pour le clignement

**Cohabitation des deux systèmes :**
- ✅ Pas de conflit
- Lerp gère : expressions faciales (happy, sad, angry, etc.)
- Direct gère : clignement automatique
- BlendShape Proxy additionne les valeurs automatiquement

---

## 🐛 Problèmes Résolus

### 1. Blendshapes ne s'appliquent pas visuellement

**Symptômes :**
- Logs Unity montrent valeurs correctes (0.0 → 1.0)
- Game View : aucun mouvement des paupières

**Cause racine :**
```csharp
// GetBlendShapeKey() retournait BlendShapePreset.Unknown
// pour "blink", "blink_l", "blink_r"
```

**Solution :**
Ajout des 3 cas manquants dans le switch statement

**Leçon :**
Toujours vérifier que les BlendShape names matchent les presets VRM

### 2. Animation trop lente (2 secondes par clignement)

**Causes :**
- `blinkDuration = 1.5s` initial trop long
- Système Lerp avec `speed = 3.0` → calcul : `1.0 / 3.0 = 0.33s` minimum

**Évolution des solutions :**
1. ❌ Réduire `blinkDuration` → toujours via Lerp = limite physique
2. ❌ Augmenter `lerpSpeed` → instable, pas assez précis
3. ✅ Bypass Lerp + manipulation directe → contrôle total

### 3. Animation "robotique"

**Évolution :**
1. ❌ Linear interpolation (`value = t`) → mécanique
2. ⚙️ Ease-in/ease-out (`t²`, `1-t²`) → mieux mais asymétrique
3. ✅ SmoothStep → naturel et fluide

**Code final :**
```csharp
float value = Mathf.SmoothStep(startValue, endValue, t);
```

---

## 📊 Diagrammes

### Architecture Globale

```
┌─────────────────────────────────────────────────────────────┐
│                    PYTHON (PySide6 GUI)                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  app.py                    unity_bridge.py                   │
│  ┌──────────────┐          ┌────────────────┐               │
│  │ Checkbox UI  │──calls──>│ set_auto_blink │               │
│  │   Toggle     │          │   (enabled)    │               │
│  └──────────────┘          └────────┬───────┘               │
│         │                           │                         │
│         └──saves────>  config.py    │                         │
│                       (enabled=true) │                         │
└───────────────────────────────────────┼─────────────────────┘
                                        │ TCP Socket
                                        │ JSON: {"command":"set_auto_blink",
                                        │        "enabled":true}
                                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   UNITY (C# Scripts)                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  PythonBridge.cs            VRMAutoBlinkController.cs        │
│  ┌────────────────┐         ┌──────────────────────┐        │
│  │ ProcessMessages│─calls──>│ SetBlinkEnabled(true)│        │
│  │   (Update)     │         └──────────┬───────────┘        │
│  └────────────────┘                    │                     │
│                                         │ StartCoroutine     │
│                                         ▼                     │
│                              ┌──────────────────┐            │
│                              │   BlinkLoop()    │            │
│                              │  Wait 2-5s...    │            │
│                              └────────┬─────────┘            │
│                                       │                       │
│                                       ▼                       │
│                              ┌──────────────────┐            │
│                              │ PerformBlink()   │            │
│                              │                  │            │
│                              │ Phase1: Close    │            │
│                              │ Phase2: Pause    │            │
│                              │ Phase3: Open     │            │
│                              └────────┬─────────┘            │
│                                       │                       │
│                                       ▼                       │
│                         VRMBlendShapeProxy.ImmediatelySetValue│
│                         VRMBlendShapeProxy.Apply()           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Flux d'Animation

```
Time (ms)
    0 ──────────────────────────────────────────────────────► 160
    │                                                            │
    │ ◄── 50ms ──► ◄ 30ms ► ◄────── 80ms ──────►               │
    │   Close      Pause         Open                          │
    │                                                            │
    │                                                            │
Value
1.0 ┤           ┌───┐                                           
    │          ╱     ╲                                          
    │         ╱       ╲                                         
0.5 ┤        ╱         ╲                                        
    │       ╱           ╲                                       
    │      ╱             ╲___                                   
0.0 ┤─────╱                  ╲___________________________       
    │                                                            
    └─── Courbe SmoothStep (S-curve) ───────────────────►
```

---

## 🚀 Optimisations Futures Possibles

### 1. Clignements asymétriques (wink)

```csharp
// Clignotement d'un seul œil
if (Random.value < 0.1f)  // 10% de chance
{
    bool leftEye = Random.value < 0.5f;
    PerformBlink(leftEye ? "blink_l" : "blink_r");
}
```

### 2. Variations de vitesse

```csharp
// Clignements "fatigués" (plus lents) selon l'heure
float speedMultiplier = GetTimeOfDayFactor();  // 0.5-1.5
float adjustedDuration = baseDuration * speedMultiplier;
```

### 3. Synchronisation avec la parole

```csharp
// Réduire fréquence pendant que l'avatar parle
if (lipSyncController != null && lipSyncController.IsSpeaking)
{
    nextBlinkTime += 2.0f;  // Retarder le prochain clignement
}
```

### 4. Patterns réalistes

```csharp
// Séquences de 2-3 clignements rapprochés (comme humains)
if (Random.value < 0.15f)  // 15% de chance
{
    yield return PerformBlink();
    yield return new WaitForSeconds(0.3f);
    yield return PerformBlink();  // Double clignement
}
```

---

## 📚 Références Techniques

### Unity APIs utilisées

- `Mathf.SmoothStep(a, b, t)` → Interpolation Hermite
- `Random.Range(min, max)` → Génération d'intervalles aléatoires
- `Time.deltaTime` → Delta time frame-independent
- `yield return new WaitForSeconds(t)` → Delays non-bloquants
- `StartCoroutine()` / `StopCoroutine()` → Gestion coroutines

### UniVRM APIs

- `VRMBlendShapeProxy.ImmediatelySetValue(key, value)` → Set direct
- `VRMBlendShapeProxy.Apply()` → Application des changements
- `BlendShapePreset.Blink` → Preset standard VRM

### Documentation externe

- [Unity Coroutines](https://docs.unity3d.com/Manual/Coroutines.html)
- [UniVRM Documentation](https://vrm.dev/en/univrm/)
- [VRM BlendShape Specification](https://github.com/vrm-c/vrm-specification/blob/master/specification/VRMC_vrm-1.0/expressions.md)
- [Hermite Interpolation](https://en.wikipedia.org/wiki/Hermite_interpolation)

---

## ✅ Checklist d'Intégration

Pour intégrer ce système dans un nouveau projet :

- [ ] **Unity Setup**
  - [ ] Importer UniVRM package
  - [ ] Créer VRMAutoBlinkController.cs dans Assets/Scripts/
  - [ ] Modifier VRMBlendshapeController.cs (ajouter mapping Blink)
  - [ ] Attacher VRMAutoBlinkController au GameObject principal
  - [ ] Assigner référence VRMBlendshapeController dans Inspector

- [ ] **Python Setup**
  - [ ] Ajouter méthode `set_auto_blink()` dans unity_bridge.py
  - [ ] Ajouter section `auto_blink` dans config.py
  - [ ] Créer checkbox UI dans app.py
  - [ ] Connecter handler `on_auto_blink_toggle`

- [ ] **Configuration**
  - [ ] Ajuster timings si nécessaire (closeDuration, pauseDuration, openDuration)
  - [ ] Tester avec différents modèles VRM
  - [ ] Vérifier que Blink/Blink_L/Blink_R existent dans le modèle

- [ ] **Tests**
  - [ ] Toggle on/off fonctionne
  - [ ] Intervalle aléatoire respecté
  - [ ] Animation fluide (pas de saccades)
  - [ ] Pas de conflit avec expressions manuelles
  - [ ] Configuration sauvegardée/restaurée

---

**🎉 Fin du guide technique - Session 8 terminée avec succès !**
