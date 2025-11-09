# 🐛 Troubleshooting - Session 8 : Clignement Automatique

## 📋 Vue d'ensemble

Ce document recense **tous les problèmes rencontrés** pendant le développement de la fonctionnalité de clignement automatique des yeux, ainsi que leurs solutions complètes.

---

## 🔴 Problème 1 : Blendshapes ne s'appliquent pas visuellement

### Symptômes

- ✅ Console Unity affiche les logs corrects :
  ```
  [AutoBlink] Closing eyes: 0.25
  [AutoBlink] Closing eyes: 0.50
  [AutoBlink] Closing eyes: 0.75
  [AutoBlink] Closing eyes: 1.00 (fully closed)
  ```
- ❌ **Aucun effet visuel** dans la Game View
- ❌ Les paupières de l'avatar ne bougent pas du tout

### Diagnostic

**Étape 1 : Vérifier que le système Lerp fonctionne**
- Test avec le slider manuel "Happy" → ✅ Fonctionne
- → Le problème n'est **pas** dans VRMBlendShapeProxy

**Étape 2 : Vérifier les valeurs dans le VRMAutoBlinkController**
- Ajout de logs dans `PerformBlink()` :
  ```csharp
  Debug.Log($"[AutoBlink] Setting blink value: {value}");
  ```
- → Les valeurs atteignent bien 1.0

**Étape 3 : Inspecter GetBlendShapeKey()**
```csharp
private BlendShapePreset GetBlendShapeKey(string expressionName)
{
    switch (expressionName.ToLower())
    {
        case "happy": return BlendShapePreset.Joy;
        case "sad": return BlendShapePreset.Sorrow;
        // ...
        // ⚠️ MANQUANT : case "blink"
        default: return BlendShapePreset.Unknown;
    }
}
```

**🔍 Cause racine identifiée :**
Le switch statement ne contenait **pas** les cas `"blink"`, `"blink_l"`, `"blink_r"`.

**Conséquence :**
1. `GetBlendShapeKey("blink")` retournait `BlendShapePreset.Unknown`
2. Unity créait une clé BlendShape nommée "unknown"
3. Cette clé n'existe pas dans le modèle VRM
4. Les valeurs étaient ignorées → pas d'effet visuel

### Solution

**Ajout des 3 cas manquants dans VRMBlendshapeController.cs :**

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
        
        // ✅ AJOUT CRITIQUE
        case "blink": return BlendShapePreset.Blink;
        case "blink_l": return BlendShapePreset.Blink_L;
        case "blink_r": return BlendShapePreset.Blink_R;
        
        default: return BlendShapePreset.Unknown;
    }
}
```

### Résultat

✅ **Clignement visible immédiatement** après ce fix

### Leçons apprises

1. **Toujours vérifier le mapping BlendShape** avant d'accuser le système d'animation
2. Les logs "value = 1.0" ne garantissent **pas** que le modèle est affecté
3. Utiliser `VRMBlendShapeProxy.GetValues()` pour debugger les clés réellement appliquées :
   ```csharp
   foreach (var kvp in blendShapeProxy.GetValues())
   {
       Debug.Log($"Key: {kvp.Key}, Value: {kvp.Value}");
   }
   ```

---

## 🟡 Problème 2 : Animation trop lente (2 secondes par clignement)

### Symptômes

- ✅ Clignement fonctionne visuellement
- ❌ Animation extrêmement lente (~2 secondes pour fermer les yeux)
- ❌ Pas du tout naturel (humain = 0.1-0.2s)

### Diagnostic

**Configuration initiale :**
```csharp
[SerializeField] private float blinkDuration = 1.5f;  // Durée totale du clignement
```

**Dans VRMBlendshapeController (système Lerp) :**
```csharp
[SerializeField] private float lerpSpeed = 3.0f;
```

**Calcul du temps réel :**
- Système Lerp : `time = distance / speed = 1.0 / 3.0 = 0.33s`
- Phase fermeture : 0.33s
- Phase pause : 1.5s (blinkDuration)
- Phase ouverture : 0.33s
- **Total ≈ 2.16s** → Beaucoup trop lent !

### Tentatives de solutions

#### ❌ Tentative 1 : Réduire blinkDuration

```csharp
[SerializeField] private float blinkDuration = 0.3f;
```

**Résultat :** Animation toujours via Lerp → minimum 0.33s incompressible

#### ❌ Tentative 2 : Augmenter lerpSpeed

```csharp
[SerializeField] private float lerpSpeed = 20.0f;  // Très rapide
```

**Problèmes :**
- Instabilité (dépassements possibles)
- Toujours limité par le système de queue Lerp
- Pas de contrôle précis du timing

#### ✅ Tentative 3 : Bypass du système Lerp

**Décision :** Manipuler **directement** le VRMBlendShapeProxy

**Implémentation :**
1. Ajouter méthode publique dans VRMBlendshapeController :
   ```csharp
   public VRMBlendShapeProxy GetBlendShapeProxy()
   {
       return blendShapeProxy;
   }
   ```

2. Appliquer les valeurs directement dans VRMAutoBlinkController :
   ```csharp
   VRMBlendShapeProxy proxy = blendshapeController.GetBlendShapeProxy();
   BlendShapeKey blinkKey = new BlendShapeKey(BlendShapePreset.Blink);
   
   proxy.ImmediatelySetValue(blinkKey, value);
   proxy.Apply();
   ```

**Avantages :**
- Contrôle total du timing (pas de file d'attente)
- Application instantanée (1 frame)
- Permet animation fluide avec coroutines

### Solution finale

**Configuration optimisée :**
```csharp
[SerializeField] private float closeDuration = 0.05f;   // 50ms
[SerializeField] private float pauseDuration = 0.03f;   // 30ms (yeux fermés)
[SerializeField] private float openDuration = 0.08f;    // 80ms
```

**Total : 160ms** → Réalisme humain ✅

### Résultat

✅ Animation rapide et naturelle  
✅ Timing précis au milliseconde  
✅ Pas de conflit avec le système Lerp (coexistent pacifiquement)

### Leçons apprises

1. **Le système Lerp n'est pas adapté** pour des animations très rapides
2. Manipulation directe du proxy = contrôle total
3. Les deux systèmes peuvent coexister :
   - Lerp → Expressions faciales (transitions lentes)
   - Direct → Clignements (animations rapides)

---

## 🟠 Problème 3 : Animation "robotique" / pas naturelle

### Symptômes

- ✅ Clignement rapide (160ms)
- ❌ Mouvement trop linéaire, effet "mécanique"
- ❌ Manque de fluidité

### Diagnostic

**Code initial (interpolation linéaire) :**

```csharp
float elapsed = 0f;
while (elapsed < closeDuration)
{
    elapsed += Time.deltaTime;
    float t = elapsed / closeDuration;
    float value = t;  // ← Linéaire : 0.0 → 1.0 à vitesse constante
    
    proxy.ImmediatelySetValue(blinkKey, value);
    proxy.Apply();
    yield return null;
}
```

**Problème :**
- Accélération constante (pas d'accélération/décélération)
- Humains ne clignent **jamais** de façon linéaire
- Manque de "naturel"

### Évolution des solutions

#### ⚙️ Tentative 1 : Ease-in (accélération progressive)

```csharp
float value = t * t;  // Courbe quadratique
```

**Résultat :**
- ✅ Début smooth (accélération douce)
- ❌ Fin brutale (pas de décélération)

#### ⚙️ Tentative 2 : Ease-out (décélération progressive)

```csharp
float value = 1f - (1f - t) * (1f - t);
```

**Résultat :**
- ❌ Début brutal (accélération instantanée)
- ✅ Fin smooth (décélération douce)

#### ✅ Solution finale : SmoothStep (courbe en S)

```csharp
float value = Mathf.SmoothStep(0f, 1f, t);
```

**Formule mathématique :**
```
SmoothStep(t) = 3t² - 2t³
```

**Caractéristiques :**
- Dérivée nulle en t=0 (accélération douce au départ)
- Dérivée nulle en t=1 (décélération douce à la fin)
- Pente maximale en t=0.5 (vitesse max au milieu)
- Courbe symétrique

**Graphique de la courbe :**
```
Value
1.0 ┤           ╭─────
    │         ╱
0.5 ┤       ╱
    │     ╱
0.0 ┤─────╯
    └────────────────► Time
     0   0.5   1.0
```

### Code final

**Phase 1 : Fermeture**
```csharp
float elapsed = 0f;
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

**Phase 3 : Ouverture**
```csharp
float elapsed = 0f;
while (elapsed < openDuration)
{
    elapsed += Time.deltaTime;
    float t = Mathf.Clamp01(elapsed / openDuration);
    float value = Mathf.SmoothStep(1f, 0f, t);  // ← Courbe S inversée
    
    blendShapeProxy.ImmediatelySetValue(blinkKey, value);
    blendShapeProxy.Apply();
    yield return null;
}
```

### Résultat

✅ Animation fluide et naturelle  
✅ Accélération/décélération automatiques  
✅ Visuellement indistinguable d'un clignement humain

**Retour utilisateur :**
> "Super c'est bien la !" ✅

### Leçons apprises

1. **SmoothStep est LA solution** pour animations courtes et naturelles
2. Pour encore plus de fluidité → `Mathf.SmootherStep()` (courbe C² continue)
3. Les courbes d'interpolation ont un impact **énorme** sur le "feel"
4. Toujours tester visuellement (pas seulement sur les logs)

---

## 🟣 Problème 4 : Checkbox UI ne sauvegarde pas l'état

### Symptômes

- ✅ Toggle on/off fonctionne pendant l'exécution
- ❌ État non restauré après redémarrage de l'application
- ❌ Configuration `config.json` non mise à jour

### Diagnostic

**Code initial dans app.py :**
```python
def on_auto_blink_toggle(self, state):
    enabled = state == Qt.CheckState.Checked
    
    # ❌ MANQUANT : Sauvegarde config
    
    if self.unity_bridge:
        self.unity_bridge.set_auto_blink(enabled)
```

**Problème :**
Appel IPC envoyé à Unity, mais configuration Python jamais sauvegardée

### Solution

**Ajout de la sauvegarde :**

```python
def on_auto_blink_toggle(self, state):
    enabled = state == Qt.CheckState.Checked
    
    # ✅ Sauvegarder dans config
    self.config.set("avatar.auto_blink.enabled", enabled)
    self.config.save()
    
    # Envoi IPC
    if self.unity_bridge:
        success = self.unity_bridge.set_auto_blink(enabled)
        if not success:
            logger.error("Failed to toggle auto-blink")
```

**Restauration au démarrage :**

```python
# Dans __init__
self.auto_blink_checkbox = QCheckBox("Activer le clignement automatique")
self.auto_blink_checkbox.setChecked(
    self.config.get("avatar.auto_blink.enabled", False)  # ← Lecture config
)
```

### Résultat

✅ État sauvegardé dans `~/.desktop-mate/config.json`  
✅ Restauré automatiquement au redémarrage  
✅ Synchronisé entre UI et Unity

### Leçons apprises

1. Toujours sauvegarder l'état UI dans la config
2. Vérifier la persistance après redémarrage
3. Logger les échecs d'IPC pour faciliter le debug

---

## 🟢 Problème 5 : Unity ne reçoit pas les commandes au démarrage

### Symptômes

- ❌ Premier toggle de la checkbox ne fait rien
- ✅ Les toggles suivants fonctionnent
- 🔍 Timing issue

### Diagnostic

**Séquence de démarrage :**
```
1. Python démarre
2. Python envoie connexion IPC
3. Unity démarre (prend du temps)
4. Unity charge le modèle VRM (prend du temps)
5. Python envoie `set_auto_blink` ← ⚠️ Trop tôt !
6. Unity termine le chargement
```

**Problème :**
Commande envoyée **avant** que Unity soit prêt

### Solution

**Ajout d'un délai d'initialisation dans app.py :**

```python
def send_initial_settings(self):
    """Envoie les paramètres initiaux à Unity (après délai)"""
    # ✅ Délai de 2.5s pour laisser Unity charger
    QTimer.singleShot(2500, self._apply_initial_settings)

def _apply_initial_settings(self):
    """Applique réellement les settings (callback)"""
    if self.unity_bridge and self.unity_bridge.is_connected():
        # Envoi auto-blink
        enabled = self.config.get("avatar.auto_blink.enabled", False)
        if enabled:
            self.unity_bridge.set_auto_blink(True)
```

### Évolution du délai

- Version 1 : 1000ms → ❌ Trop court
- Version 2 : 2000ms → ⚙️ Parfois suffisant
- **Version finale : 2500ms → ✅ Toujours suffisant**

### Résultat

✅ Paramètres appliqués correctement au démarrage  
✅ Clignement démarre automatiquement si enabled=true  
✅ Pas de commande IPC perdue

### Leçons apprises

1. Toujours prévoir un délai pour l'initialisation Unity
2. 2-3 secondes est un bon compromis
3. Alternative future : système de "ready" signal depuis Unity

---

## 🔧 Outils de Debug

### Console Unity

**Activer les logs VRM :**
```csharp
Debug.Log($"[AutoBlink] Current blink value: {value}");
Debug.Log($"[BlendShape] Key: {key.Name}, Preset: {key.Preset}");
```

**Vérifier les clés appliquées :**
```csharp
foreach (var kvp in blendShapeProxy.GetValues())
{
    Debug.Log($"Active key: {kvp.Key.Name} = {kvp.Value}");
}
```

### Logs Python

**Logger unity_bridge :**
```python
logger.debug(f"Sending command: {command}")
logger.error(f"IPC failed: {error}")
```

**Vérifier la config :**
```python
print(config.get("avatar.auto_blink"))
# Output: {'enabled': True, 'min_interval': 2.0, ...}
```

### Inspector Unity

**Vérifier les références :**
- VRMAutoBlinkController → blendshapeController doit être assigné
- PythonBridge → autoBlinkController doit être assigné

**Vérifier les paramètres :**
- closeDuration = 0.05
- pauseDuration = 0.03
- openDuration = 0.08
- minInterval = 2.0
- maxInterval = 5.0

---

## 📚 Checklist de Debug

Quand le clignement ne fonctionne pas :

- [ ] **Vérifier les logs Unity**
  - [ ] Messages "[AutoBlink] ..." apparaissent ?
  - [ ] Valeurs de 0.0 à 1.0 ?

- [ ] **Vérifier le mapping BlendShape**
  - [ ] `GetBlendShapeKey("blink")` retourne `BlendShapePreset.Blink` ?
  - [ ] Pas de `BlendShapePreset.Unknown` ?

- [ ] **Vérifier les références Unity**
  - [ ] VRMAutoBlinkController.blendshapeController assigné ?
  - [ ] PythonBridge.autoBlinkController assigné ?

- [ ] **Vérifier les timings**
  - [ ] closeDuration, pauseDuration, openDuration corrects ?
  - [ ] Pas de valeurs négatives ?

- [ ] **Vérifier la communication IPC**
  - [ ] Python → Unity connecté ?
  - [ ] Commande `set_auto_blink` reçue ?
  - [ ] Délai d'initialisation suffisant (2.5s) ?

- [ ] **Vérifier la config Python**
  - [ ] `config.json` contient `avatar.auto_blink` ?
  - [ ] `enabled` sauvegardé correctement ?

- [ ] **Vérifier le modèle VRM**
  - [ ] BlendShapes Blink/Blink_L/Blink_R existent ?
  - [ ] Tester manuellement avec le slider ?

---

## 💡 FAQ

### Q1 : L'animation est saccadée, pourquoi ?

**Réponse :** Vérifier le framerate Unity.

```csharp
// Forcer 60 FPS minimum
Application.targetFrameRate = 60;
```

Si < 30 FPS → Animation saccadée même avec SmoothStep

---

### Q2 : Comment changer la vitesse du clignement ?

**Réponse :** Modifier les durations dans VRMAutoBlinkController :

```csharp
[SerializeField] private float closeDuration = 0.05f;  // Plus petit = plus rapide
[SerializeField] private float openDuration = 0.08f;   // Plus petit = plus rapide
```

**⚠️ Ne pas descendre en dessous de 0.02s** (risque de saccades)

---

### Q3 : Comment activer/désactiver le clignement par code Python ?

**Réponse :**

```python
from src.ipc.unity_bridge import UnityBridge

bridge = UnityBridge()
bridge.connect()

# Activer
bridge.set_auto_blink(True)

# Désactiver
bridge.set_auto_blink(False)
```

---

### Q4 : Les clignements sont trop fréquents, comment espacer ?

**Réponse :** Modifier les intervalles dans Unity Inspector :

- Min Interval : 2.0 → 4.0 (minimum 4 secondes)
- Max Interval : 5.0 → 8.0 (maximum 8 secondes)

Ou par code :
```csharp
[SerializeField] private float minInterval = 4.0f;
[SerializeField] private float maxInterval = 8.0f;
```

---

### Q5 : Peut-on faire des clignements asymétriques (wink) ?

**Réponse :** Oui, modifier `PerformBlink()` :

```csharp
private IEnumerator PerformBlink()
{
    // 90% clignement normal, 10% wink
    bool isWink = Random.value < 0.1f;
    
    BlendShapeKey key;
    if (isWink)
    {
        // Choisir œil gauche ou droit
        bool leftEye = Random.value < 0.5f;
        key = new BlendShapeKey(leftEye ? BlendShapePreset.Blink_L : BlendShapePreset.Blink_R);
    }
    else
    {
        key = new BlendShapeKey(BlendShapePreset.Blink);
    }
    
    // ... reste du code ...
}
```

---

## 🎯 Résumé

| Problème | Symptôme principal | Solution clé |
|----------|-------------------|--------------|
| **Mapping manquant** | Logs OK mais pas d'effet visuel | Ajouter Blink dans GetBlendShapeKey() |
| **Animation trop lente** | Clignement de 2 secondes | Bypass Lerp + manipulation directe |
| **Animation robotique** | Mouvement linéaire | Utiliser SmoothStep au lieu de t |
| **Config non sauvegardée** | État perdu au redémarrage | Appeler config.save() dans handler |
| **Commandes perdues** | Premier toggle ne fonctionne pas | Délai 2.5s avant envoi initial |

---

**✅ Tous les problèmes résolus - Session 8 fonctionnelle à 100% !**
